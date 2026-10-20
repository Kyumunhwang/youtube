# 📥 StreamYT Downloader

> **YouTube 고화질 비디오(1080p, 4K) 및 고음질 MP3 다운로더**  
> Streamlit 기반의 깔끔한 웹 인터페이스와 최신 YouTube 봇/시그니처 차단(HTTP 403 Forbidden) 우회 엔진이 탑재된 초경량 다운로더입니다.

---

## ✨ 주요 기능 및 특징

1. **최신 YouTube 차단 정책 완벽 대응**:
   - YouTube의 n-sig / SABR 스트리밍 및 봇 챌린지를 로컬 Node.js EJS 엔진으로 실시간 해결하여 **`HTTP 403: Forbidden` 차단 없이 안정적 다운로드**.
2. **최고 화질 & 무손실 음원 추출**:
   - 1080p(Full HD), 1440p(2K), 2160p(4K) 비디오 스트림과 오디오 스트림을 무손실 MP4로 자동 결합.
   - 고음질 MP3 (192kbps) 원클릭 추출.
3. **스마트 다운로드 경로 감지**:
   - Windows 레지스트리를 조회하여 사용자가 설정한 실제 **'다운로드(Downloads)'** 폴더를 자동으로 감지하여 저장.
4. **다운로드 완료 후 즉시 파일 탐색기 열기**:
   - 다운로드가 끝나면 `📂 Open in File Explorer` 버튼을 클릭하여 파일이 저장된 위치를 윈도우 탐색기에서 바로 확인 가능.
5. **초경량 & 제로 컨피그(Zero-Config)**:
   - 복잡한 가상환경이나 라이브러리 설정 없이 **`run.bat` 더블 클릭 한 번으로 모든 환경 자동 구축 및 실행**.

---

## 🛠️ 사전 준비 (필수 프로그램)

다른 컴퓨터에서 처음 실행하기 전에 아래 **두 가지 프로그램**이 설치되어 있어야 합니다.

1. **Python 3.11 이상**
   - [공식 다운로드 링크 (python.org)](https://www.python.org/downloads/)
   - ⚠️ **매우 중요**: 설치 시 첫 화면 하단의 **`Add python.exe to PATH`** 체크박스를 반드시 체크하고 설치하세요!
2. **Node.js (LTS 버전 권장)**
   - [공식 다운로드 링크 (nodejs.org)](https://nodejs.org/)
   - YouTube의 최신 JavaScript 시그니처 챌린지를 해석하여 **403 Forbidden 에러를 방지**하는 핵심 런타임입니다. (기본 설정대로 Next를 눌러 설치 완료)
3. **Git (선택 사항)**
   - [공식 다운로드 링크 (git-scm.com)](https://git-scm.com/)
   - Git이 설치되어 있지 않다면 GitHub 페이지에서 **`Code` -> `Download ZIP`**으로 받아 압축을 풀어도 됩니다.

---

## 💻 1. 다른 컴퓨터에서 Clone (다운로드) 하는 방법

### 방법 A: Git 명령어로 Clone 하기 (추천)
1. 키보드의 `Win + R`을 누르고 `cmd`를 입력 후 엔터를 눌러 명령 프롬프트(터미널)를 엽니다.
2. 프로젝트를 저장할 폴더로 이동합니다. (예: C:\Projects)
   ```cmd
   cd C:\
   ```
3. 다음 명령어를 복사하여 붙여넣고 엔터를 누릅니다:
   ```cmd
   git clone https://github.com/Kyumunhwang/youtube.git
   ```
4. 복제된 폴더로 이동합니다:
   ```cmd
   cd youtube
   ```

### 방법 B: Git 없이 ZIP 파일로 다운로드하기
1. GitHub 저장소 주소에 접속합니다: [https://github.com/Kyumunhwang/youtube](https://github.com/Kyumunhwang/youtube)
2. 우측 상단의 초록색 **`< > Code`** 버튼을 클릭합니다.
3. **`Download ZIP`**을 클릭합니다.
4. 다운로드된 `youtube-main.zip` 파일의 압축을 원하는 폴더에 풉니다.

---

## 🚀 2. 설치 및 실행 방법 (가장 쉬운 방법)

### 👉 원클릭 자동 실행: `run.bat` 더블 클릭!

다운로드한 폴더 안의 **`run.bat`** 파일을 마우스로 **더블 클릭**하기만 하면 됩니다.

- **최초 실행 시**:
  1. 가상환경(`.venv`)을 자동으로 생성합니다.
  2. 필요한 필수 라이브러리(`streamlit`, `yt-dlp`, `static-ffmpeg` 등)를 자동으로 설치합니다.
  3. 설치 완료 후 웹 브라우저 창이 자동으로 열리며 프로그램이 시작됩니다.
- **두 번째 실행부터**:
  - 이미 구축된 가상환경을 통해 1초 만에 즉시 실행됩니다.

---

### ⚙️ (선택 사항) 수동으로 설치 및 실행하고 싶은 경우
명령 프롬프트(CMD) 또는 PowerShell에서 직접 구동할 수도 있습니다:

```cmd
# 1. 가상환경 생성
python -m venv .venv

# 2. 가상환경 활성화 (Windows CMD)
.venv\Scripts\activate

# 3. 필수 라이브러리 설치
pip install -r requirements.txt

# 4. Streamlit 웹 앱 구동
streamlit run app.py
```

---

## 🖥️ 3. 사용 방법 (매우 쉽고 직관적)

웹 브라우저에 **StreamYT Downloader** 화면(`http://localhost:8501`)이 열리면 다음과 같이 사용하세요:

```
┌─────────────────────────────────────────────────────────────┐
│                   StreamYT Downloader                       │
│       Target Folder: C:\Users\Username\Downloads            │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Enter YouTube Video URL: [ https://youtu.be/...       ] │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

1. **YouTube 링크 입력**:
   - `Enter YouTube Video URL:` 입력창에 다운로드할 유튜브 영상 주소를 붙여넣고 엔터를 누릅니다.
2. **영상 정보 확인**:
   - 잠시 기다리면 영상의 썸네일, 제목, 업로더, 재생 시간이 카드 형태로 나타납니다.
3. **다운로드 옵션 선택**:
   - **Video & Audio**: 비디오와 오디오가 모두 포함된 MP4 파일로 다운로드합니다. 아래의 `Select Resolution` 드롭다운에서 원하는 해상도(예: `1080p (Full HD)`, `720p (HD)` 등)를 선택할 수 있습니다.
   - **Audio Only (MP3)**: 영상 없이 고음질 MP3 음원 파일만 추출합니다.
4. **다운로드 시작**:
   - **`Start Download`** 버튼을 누릅니다.
   - 실시간 진행률(Progress bar)과 함께 다운로드 및 포맷 병합이 진행됩니다.
5. **완료 및 파일 확인**:
   - 다운로드가 완료되면 성공 메시지와 함께 저장된 파일 경로가 표시됩니다.
   - **`📂 Open in File Explorer`** 버튼을 누르면 윈도우 탐색기가 열리며 방금 다운로드된 파일이 자동으로 선택(강조)됩니다.

---

## ❓ 자주 묻는 질문 및 문제 해결 (Troubleshooting)

### Q1. `HTTP Error 403: Forbidden` 오류가 발생해요!
- **원인**: YouTube가 봇 차단 챌린지를 적용했으나, 이를 해석할 JavaScript 엔진(Node.js)을 찾지 못한 경우입니다.
- **해결책**: [nodejs.org](https://nodejs.org/)에 접속하여 **Node.js (LTS)**를 설치한 후 프로그램을 다시 실행해 주세요. 본 프로그램은 설치된 Node.js를 자동으로 감지하여 403 차단을 우회합니다.

### Q2. `run.bat` 실행 시 `Python is not installed` 라고 나와요!
- **원인**: 컴퓨터에 파이썬이 설치되어 있지 않거나 환경 변수(PATH)에 등록되지 않았습니다.
- **해결책**: [python.org](https://www.python.org/downloads/)에서 Python 3.11 이상을 다운로드하여 설치할 때, 반드시 첫 화면 하단의 **`Add python.exe to PATH`**를 체크하고 설치를 완료해 주세요.

### Q3. 다운로드된 파일은 어디에 저장되나요?
- 내 컴퓨터의 기본 **`다운로드(Downloads)`** 폴더에 저장됩니다. (상단 자막에 현재 지정된 폴더 경로가 표시됩니다.)
- 다운로드 완료 카드의 **`📂 Open in File Explorer`** 버튼을 누르면 즉시 해당 폴더가 열립니다.

---

## 📦 프로젝트 구조 (저장소 최소 파일 구성)

```text
youtube/
├── app.py              # Streamlit 프론트엔드 UI 및 이벤트 처리
├── downloader.py       # yt-dlp 코어 다운로더 엔진 (EJS 및 FFmpeg 연동)
├── requirements.txt    # 필수 파이썬 패키지 명세
├── run.bat             # 원클릭 환경 자동구성 및 실행 배치 파일
├── .gitignore          # 불필요한 빌드/캐시/가상환경 배제 설정
└── README.md           # 상세 사용 및 설치 설명서
```
