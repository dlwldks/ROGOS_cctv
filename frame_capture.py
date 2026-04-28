# rtsp/frame_capture.py

import cv2
import time

RTSP_URL = "rtsp://localhost:8554/seoul_424"

cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("RTSP 스트림 연결 실패")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("프레임 읽기 실패")
        time.sleep(1)
        continue

    cv2.imwrite("latest_frame.jpg", frame)
    print("프레임 저장 완료")

    time.sleep(3)