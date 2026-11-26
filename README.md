# 📡 ROGOS - CCTV RTSP 관제 시스템

## Portfolio overview / 구현 범위

This repository implements the CCTV ingestion and streaming module of ROGOS: HLS sources, ffmpeg, MediaMTX, RTSP for downstream processing and HLS for browser monitoring. The separate TAS/ROGOS AI prototype explores VLM interpretation, BM25 retrieval and LLM response generation; these components are not implemented in this repository. External stream availability varies; live coverage and disaster-response accuracy are not certified.


## 📌 프로젝트 개요

ROGOS는 **다양한 CCTV 영상 소스를 수집하고**, 이를 **RTSP 스트림으로 변환하여**
관제 화면에서 **여러 영상을 동시에 모니터링**할 수 있는 시스템입니다.

본 파트는 다음 역할을 담당합니다:

* CCTV 영상 수집 (m3u8 기반)
* RTSP 스트림 변환 (MediaMTX + ffmpeg)
* 멀티 CCTV 관제 화면 구축

---

## 🧠 전체 시스템 구조

```
CCTV (m3u8 / HLS)
        ↓
     ffmpeg
        ↓
   MediaMTX (RTSP 서버)
        ↓
 ┌───────────────┬───────────────┐
 │ RTSP (AI용)   │ HLS (웹용)     │
 │ rtsp://       │ http://       │
 └───────────────┴───────────────┘
        ↓
  Dashboard (관제 화면)
```

---

## 📁 폴더 구조

```
rtsp/
├── cctv_sources.json      # CCTV 목록 (핵심)
├── stream_manager.py      # 여러 스트림 실행 (핵심)
├── dashboard/
│   └── index.html         # 관제 화면
├── docker-compose.yml     # MediaMTX 실행
├── mediamtx.yml           # RTSP 서버 설정
├── requirements.txt
└── README.md
```

---

## ⚙️ 설치 및 실행 방법

### 1️⃣ Docker 실행

```bash
docker compose up -d
```

---

### 2️⃣ Python 환경 설정

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### 3️⃣ CCTV 스트림 실행

```bash
python stream_manager.py
```

---

### 4️⃣ 관제 화면 실행

```bash
cd dashboard
python -m http.server 3000
```

브라우저 접속:

```
http://localhost:3000
```

---

## 📡 CCTV 데이터 구조

`cctv_sources.json`

```json
[
  {
    "id": "seoul_424",
    "name": "원효대교 북단",
    "region": "서울",
    "source_type": "hls",
    "source_url": "https://strm3.spatic.go.kr/live/424.stream/playlist.m3u8",
    "rtsp_url": "rtsp://localhost:8554/seoul_424",
    "hls_url": "http://localhost:8888/seoul_424/index.m3u8"
  }
]
```

---

## 📺 스트림 주소

### 🔹 RTSP (AI 분석용)

```
rtsp://localhost:8554/{id}
```

예시:

```
rtsp://localhost:8554/seoul_424
```

---

### 🔹 HLS (웹 관제용)

```
http://localhost:8888/{id}/index.m3u8
```

예시:

```
http://localhost:8888/seoul_424/index.m3u8
```

---

## 🚀 주요 기능

* ✅ 여러 CCTV 동시 스트리밍
* ✅ RTSP 변환 및 송출
* ✅ 웹 기반 관제 화면
* ✅ 스트림 끊김 자동 복구 (stream_manager)
* ✅ 확장 가능한 구조 (AI 연결 가능)

---

## ❗ 주의사항

* 브라우저는 RTSP를 직접 지원하지 않음 → HLS 사용
* CCTV 영상은 대부분 m3u8(HLS) 기반
* 일부 CCTV는 인증/API 필요

---

## 🔮 향후 확장

* 🎯 FastVLM 기반 영상 분석
* 🎯 LLM 기반 상황 대응 안내
* 🎯 이벤트 감지 (사고, 정체 등)
* 🎯 알림 시스템 연동

---

## 💡 한 줄 요약

> CCTV 영상을 RTSP로 변환하고, 여러 영상을 한 화면에서 모니터링하는 관제 시스템

---
