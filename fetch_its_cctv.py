# rtsp/fetch_its_cctv.py

import json
import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

# ✅ .env는 rtsp/.env 에 있어야 함
load_dotenv(BASE_DIR / ".env")

ITS_API_URL = "https://openapi.its.go.kr:9443/cctvInfo"

API_KEY = os.getenv("ITS_API_KEY")

ITS_TYPE = os.getenv("ITS_TYPE", "its")
ITS_CCTV_TYPE = os.getenv("ITS_CCTV_TYPE", "4")

MIN_X = os.getenv("ITS_MIN_X", "126.7")
MAX_X = os.getenv("ITS_MAX_X", "127.3")
MIN_Y = os.getenv("ITS_MIN_Y", "37.3")
MAX_Y = os.getenv("ITS_MAX_Y", "37.8")

GET_TYPE = os.getenv("ITS_RESPONSE_TYPE", "json")

RTSP_BASE = os.getenv("RTSP_BASE", "rtsp://localhost:8554")
HLS_BASE = os.getenv("HLS_BASE", "http://localhost:8888")

# ✅ 기본 저장 위치: rtsp/cctv_sources.json
OUTPUT_PATH = os.getenv("CCTV_JSON_PATH", "cctv_sources.json")


def safe_id(text: str, fallback: str) -> str:
    if not text:
        return fallback

    text = text.lower().strip()
    text = re.sub(r"https?://", "", text)
    text = re.sub(r"[^a-z0-9가-힣]+", "_", text)
    text = text.strip("_")

    return text or fallback


def get_cctv_items(response_json) -> list:
    if isinstance(response_json, list):
        return response_json

    if not isinstance(response_json, dict):
        return []

    for key in ["response", "body", "items", "item", "data", "cctvInfo"]:
        value = response_json.get(key)

        if isinstance(value, list):
            return value

        if isinstance(value, dict):
            found = get_cctv_items(value)
            if found:
                return found

    return []


def normalize_cctv(item: dict, index: int) -> dict | None:
    name = (
        item.get("cctvname")
        or item.get("cctvName")
        or item.get("name")
        or f"its_cctv_{index}"
    )

    source_url = (
        item.get("cctvurl")
        or item.get("cctvUrl")
        or item.get("url")
        or item.get("source_url")
    )

    if not source_url:
        return None

    raw_id = (
        item.get("cctvid")
        or item.get("cctvId")
        or item.get("id")
        or f"its_{index}"
    )

    cctv_id = f"its_{safe_id(str(raw_id), str(index))}"

    return {
        "id": cctv_id,
        "name": name,
        "region": "ITS",
        "source_type": "hls",
        "source_url": source_url,
        "rtsp_url": f"{RTSP_BASE}/{cctv_id}",
        "hls_url": f"{HLS_BASE}/{cctv_id}/index.m3u8",
    }


def fetch_its_cctv() -> list:
    if not API_KEY:
        raise ValueError(f"ITS_API_KEY가 .env에 없습니다. 확인 위치: {BASE_DIR / '.env'}")

    params = {
        "apiKey": API_KEY,
        "type": ITS_TYPE,
        "cctvType": ITS_CCTV_TYPE,
        "minX": MIN_X,
        "maxX": MAX_X,
        "minY": MIN_Y,
        "maxY": MAX_Y,
        "getType": GET_TYPE,
    }

    print("ITS CCTV API 요청 중...")
    print(f"- .env 위치: {BASE_DIR / '.env'}")
    print(f"- type: {ITS_TYPE}")
    print(f"- cctvType: {ITS_CCTV_TYPE}")
    print(f"- 영역: X({MIN_X}~{MAX_X}), Y({MIN_Y}~{MAX_Y})")

    response = requests.get(ITS_API_URL, params=params, timeout=15)
    response.raise_for_status()

    data = response.json()
    items = get_cctv_items(data)

    print(f"API 응답 CCTV 개수: {len(items)}")

    result = []
    seen_ids = set()

    for index, item in enumerate(items, start=1):
        normalized = normalize_cctv(item, index)

        if not normalized:
            continue

        original_id = normalized["id"]
        unique_id = original_id
        count = 2

        while unique_id in seen_ids:
            unique_id = f"{original_id}_{count}"
            count += 1

        normalized["id"] = unique_id
        normalized["rtsp_url"] = f"{RTSP_BASE}/{unique_id}"
        normalized["hls_url"] = f"{HLS_BASE}/{unique_id}/index.m3u8"

        seen_ids.add(unique_id)
        result.append(normalized)

    return result


def save_json(cctv_sources: list):
    output_file = Path(OUTPUT_PATH)

    # ✅ 상대경로면 rtsp 폴더 기준으로 저장
    if not output_file.is_absolute():
        output_file = BASE_DIR / output_file

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cctv_sources, f, ensure_ascii=False, indent=2)

    print(f"\n저장 완료: {output_file}")
    print(f"저장된 CCTV 개수: {len(cctv_sources)}")


def main():
    cctv_sources = fetch_its_cctv()

    if not cctv_sources:
        print("저장할 CCTV 데이터가 없습니다.")
        return

    save_json(cctv_sources)


if __name__ == "__main__":
    main()