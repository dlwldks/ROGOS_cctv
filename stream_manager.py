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
        "-i",
        source_url,
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-tune",
        "zerolatency",
        "-rtsp_transport",
        "tcp",
        "-f",
        "rtsp",
        rtsp_url,
    ]

    print(f"▶ 송출 시작: {name}")
    print(f"   source: {source_url}")
    print(f"   rtsp:   {rtsp_url}")

    return subprocess.Popen(cmd)


def main():
    sources = load_sources()

    for source in sources:
        process = start_stream(source)
        processes.append(process)
        time.sleep(1)

    print("\n✅ 모든 CCTV 송출 프로세스 실행됨")
    print("종료하려면 Ctrl + C")

    try:
        while True:
            time.sleep(5)

            for i, process in enumerate(processes):
                if process.poll() is not None:
                    print(f"⚠️ 프로세스 종료 감지: {sources[i]['name']}")
                    print("   다시 시작합니다.")
                    processes[i] = start_stream(sources[i])

    except KeyboardInterrupt:
        print("\n🛑 전체 스트림 종료 중...")

        for process in processes:
            process.terminate()

        print("종료 완료")


if __name__ == "__main__":
    main()