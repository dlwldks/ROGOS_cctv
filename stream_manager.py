# rtsp/stream_manager.py

import json
import subprocess
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SOURCE_FILE = BASE_DIR / "cctv_sources.json"
FETCH_FILE = BASE_DIR / "fetch_its_cctv.py"

START_INTERVAL = 91
RESTART_DELAY = 30
HEALTH_CHECK_INTERVAL = 5

processes = []
sources = []


def load_sources():
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def refresh_sources():
    print("\n🔄 ITS CCTV URL 최신화 중...")
    subprocess.run(
        ["python", str(FETCH_FILE)],
        cwd=BASE_DIR,
        check=False,
    )


def find_latest_source(old_source):
    latest_sources = load_sources()

    old_id = old_source.get("id")
    old_name = old_source.get("name")

    for source in latest_sources:
        if source.get("id") == old_id:
            return source

    for source in latest_sources:
        if source.get("name") == old_name:
            return source

    print(f"⚠️ 최신 목록에서 CCTV를 찾지 못함: {old_name}")
    return old_source


def start_stream(source):
    source_url = source["source_url"]
    rtsp_url = source["rtsp_url"]
    name = source["name"]

    cmd = [
        "ffmpeg",
        "-re",
        "-user_agent", "Mozilla/5.0",
        "-headers", "Referer: https://its.go.kr/\r\n",
        "-reconnect", "1",
        "-reconnect_streamed", "1",
        "-reconnect_delay_max", "5",
        "-rw_timeout", "15000000",
        "-fflags", "+genpts",
        "-i", source_url,
        "-an",
        "-c:v", "copy",
        "-f", "rtsp",
        "-rtsp_transport", "tcp",
        rtsp_url,
    ]

    print(f"\n▶ 송출 시작: {name}")
    print(f"   source: {source_url}")
    print(f"   rtsp:   {rtsp_url}")

    return subprocess.Popen(
        cmd,
        stdin=subprocess.DEVNULL,
    )


def stop_process(process):
    if process and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


def restart_stream(index):
    global sources

    old_source = sources[index]

    print(f"\n⚠️ 스트림 종료됨: {old_source['name']}")
    print(f"⏳ {RESTART_DELAY}초 대기 후 URL 갱신")

    time.sleep(RESTART_DELAY)

    refresh_sources()

    new_source = find_latest_source(old_source)
    sources[index] = new_source

    print("🔁 새 URL로 재시작")
    processes[index] = start_stream(new_source)


def main():
    global sources

    sources = load_sources()

    print("🚀 CCTV 스트림 전체 시작")
    print(f"총 CCTV 개수: {len(sources)}")

    for i, source in enumerate(sources):
        process = start_stream(source)
        processes.append(process)

        print(f"({i + 1}/{len(sources)}) 실행 완료")
        time.sleep(START_INTERVAL)

    print("\n✅ 모든 CCTV 실행 완료")

    try:
        while True:
            time.sleep(HEALTH_CHECK_INTERVAL)

            for i, process in enumerate(processes):
                if process.poll() is not None:
                    restart_stream(i)

    except KeyboardInterrupt:
        print("\n🛑 전체 스트림 종료 중...")

        for process in processes:
            stop_process(process)

        print("✅ 종료 완료")


if __name__ == "__main__":
    main()