# rtsp/run.py

import subprocess
import webbrowser
import time
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = "8080"


def refresh_cctv_sources():
    print("▶ ITS CCTV 목록 최신화")
    subprocess.run(
        ["python", "fetch_its_cctv.py"],
        cwd=BASE_DIR,
        check=True,
    )


def start_stream_manager():
    print("▶ CCTV 스트림 시작")
    return subprocess.Popen(
        ["python", "stream_manager.py"],
        cwd=BASE_DIR,
    )


def start_dashboard():
    print(f"▶ 관제 화면 서버 실행 (http://localhost:{PORT}/dashboard/index.html)")
    return subprocess.Popen(
        ["python", "-m", "http.server", PORT],
        cwd=BASE_DIR,
    )


def open_browser():
    time.sleep(3)
    webbrowser.open(f"http://localhost:{PORT}/dashboard/index.html")


def cleanup(stream_proc=None, dashboard_proc=None):
    print("\n🛑 종료 중...")

    if stream_proc:
        stream_proc.terminate()

    if dashboard_proc:
        dashboard_proc.terminate()

    os.system("pkill -f ffmpeg")
    print("종료 완료")


if __name__ == "__main__":
    stream_proc = None
    dashboard_proc = None

    try:
        refresh_cctv_sources()

        stream_proc = start_stream_manager()
        dashboard_proc = start_dashboard()

        open_browser()

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        cleanup(stream_proc, dashboard_proc)

    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")
        cleanup(stream_proc, dashboard_proc)