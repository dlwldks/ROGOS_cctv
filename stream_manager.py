# rtsp/stream_manager.py

import json
import subprocess
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SOURCE_FILE = BASE_DIR / "cctv_sources.json"

processes = []


def load_sources():
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def start_stream(source):
    source_url = source["source_url"]
    rtsp_url = source["rtsp_url"]
    name = source["name"]

    cmd = [
        "ffmpeg",
        "-re",

        # HLS 조각 간 시간값 보정
        "-fflags", "+genpts+igndts",
        "-use_wallclock_as_timestamps", "1",
        "-avoid_negative_ts", "make_zero",

        "-i", source_url,

        "-an",

        # 재인코딩 없음
        "-c:v", "copy",

        # RTSP 송출 안정화
        "-f", "rtsp",
        "-rtsp_transport", "tcp",
        "-muxdelay", "0.1",
        "-muxpreload", "0.1",

        rtsp_url,
    ]

    print(f"\n▶ 송출 시작: {name}")
    print(f"   source: {source_url}")
    print(f"   rtsp:   {rtsp_url}")

    return subprocess.Popen(
        cmd,
        stdin=subprocess.DEVNULL,
    )


def main():
    sources = load_sources()

    print("🚀 CCTV 스트림 전체 시작")

    for source in sources:
        process = start_stream(source)
        processes.append(process)
        time.sleep(1)

    print("\n✅ 모든 CCTV 실행 완료")

    try:
        while True:
            time.sleep(5)

            for i, process in enumerate(processes):
                if process.poll() is not None:
                    print(f"\n⚠️ 스트림 종료됨: {sources[i]['name']}")
                    print("🔄 재시작 중...")
                    processes[i] = start_stream(sources[i])

    except KeyboardInterrupt:
        print("\n🛑 전체 스트림 종료")

        for process in processes:
            process.terminate()

        print("종료 완료")


if __name__ == "__main__":
    main()