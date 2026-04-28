ffmpeg -re -i "https://strm3.spatic.go.kr/live/424.stream/playlist.m3u8" \
-an \
-c:v libx264 \
-preset veryfast \
-tune zerolatency \
-rtsp_transport tcp \
-f rtsp rtsp://localhost:8554/seoul_424