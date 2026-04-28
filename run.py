# rtsp/run.py

import subprocess
import webbrowser
import time
import os
import signal

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = "8080"


def start_stream_manager():
    print("▶ CCTV 스트림 시작")
    return subprocess.Popen(
        ["python", "stream_manager.py"],
        cwd=BASE_DIR
    )


def start_dashboard():
    print(f"▶ 관제 화면 서버 실행 (http://localhost:{PORT}/dashboard/index.html)")
    return subprocess.Popen(
        ["python", "-m", "http.server", PORT],
        cwd=BASE_DIR
    )


def open_browser():
    time.sleep(3)
    webbrowser.open(f"http://localhost:{PORT}/dashboard/index.html")


if __name__ == "__main__":
    stream_proc = start_stream_manager()
    dashboard_proc = start_dashboard()

    open_browser()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 종료 중...")

        stream_proc.terminate()
        dashboard_proc.terminate()

        os.system("pkill -f ffmpeg")
        print("종료 완료")