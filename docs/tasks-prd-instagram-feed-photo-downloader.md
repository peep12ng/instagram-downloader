## Relevant Files
- `app.py` - 메인 Flask 애플리케이션 파일입니다. HTML 페이지 렌더링 및 다운로드 API 요청 처리를 위한 라우트를 포함합니다.
- `scraper.py` - Playwright를 사용하여 인스타그램 페이지에서 이미지 URL을 스크래핑하는 로직을 포함하는 모듈입니다.
- `browser_manager.py` - 로그인 쿠키를 사용하여 인증된 Playwright 브라우저 컨텍스트를 생성하는 로직을 포함합니다.
- `utils.py` - 이미지 다운로드 및 ZIP 파일 생성을 처리하는 유틸리티 함수를 포함하는 모듈입니다.
- `templates/index.html` - 사용자가 보게 될 메인 페이지의 Jinja2 템플릿입니다.
- `static/js/main.js` - 다운로드 요청, 로딩 상태 및 오류 메시지 표시 등 클라이언트 측 상호작용을 처리하는 JavaScript 파일입니다.
- `static/css/style.css` - UI 스타일링 및 반응형 디자인을 위한 CSS 파일입니다.
- `requirements.txt` - 프로젝트에 필요한 Python 패키지(Flask, Playwright, pytest 등) 목록입니다.
- `instagram_cookies.json` - 스크래퍼가 인증에 사용할 로그인 쿠키 파일입니다. (버전 관리에서 제외되어야 함)
- `tests/test_app.py` - `app.py`의 Flask 라우트에 대한 단위/통합 테스트입니다.
- `tests/test_scraper.py` - `scraper.py`의 스크래핑 함수에 대한 단위 테스트입니다.
- `tests/test_browser_manager.py` - `browser_manager.py`의 인증 함수에 대한 단위 테스트입니다.
- `.github/workflows/ci.yml` - GitHub Actions를 사용한 CI/CD 파이프라인 설정 파일입니다.

### Notes
- 가상 환경을 설정하고 `pip install -r requirements.txt` 명령으로 의존성을 설치합니다.
- `pytest` 명령을 사용하여 테스트를 실행합니다.

## Tasks
- [x] **1.0: Flask 프로젝트 기본 구조 설정**
  - [x] 1.1 `app.py`, `requirements.txt` 파일 및 `templates`, `static`, `tests` 디렉터리 생성
  - [x] 1.2 `requirements.txt`에 `Flask`, `Playwright`, `pytest` 추가
  - [x] 1.3 `app.py`에 기본 Flask 앱 인스턴스 생성 및 메인 페이지를 렌더링할 기본 라우트 (`/`) 추가

- [x] **2.0: 프론트엔드 UI 템플릿 구현 (HTML/Jinja2)**
  - [x] 2.1 `templates/index.html` 파일 생성 및 기본 HTML 구조 작성
  - [x] 2.2 PRD 디자인 고려사항에 따라 제목, 텍스트 입력 필드, 다운로드 버튼, 메시지 표시 영역 UI 요소 추가
  - [x] 2.3 `static/css/style.css` 파일 생성 및 `index.html`에 연결. 기본 레이아웃 및 반응형 스타일 적용
  - [x] 2.4 `static/js/main.js` 파일 생성 및 `index.html`에 연결

- [x] **3.0: 인스타그램 스크래핑 로직 구현 (Python/Playwright)**
  - [x] 3.1 `scraper.py` 파일 생성
  - [x] 3.2 Playwright를 사용하여 지정된 인스타그램 계정 페이지로 이동하고, 페이지의 모든 콘텐츠가 로드될 때까지 스크롤하는 함수 구현
  - [x] 3.3 로드된 페이지 HTML에서 모든 사진 게시물의 이미지 URL을 추출하는 파싱 로직 구현
  - [x] 3.4 존재하지 않는 계정 또는 비공개 계정 페이지의 특징을 감지하여 특정 예외(exception)를 발생시키는 로직 추가
  - [x] 3.5 로그인 쿠키를 사용하여 인증된 브라우저 세션을 생성하는 로직 구현 및 `scraper`에 통합 (`browser_manager.py`)

- [x] **4.0: 이미지 다운로드 및 ZIP 압축 기능 구현 (Python)**
  - [x] 4.1 `utils.py` 파일 생성
  - [x] 4.2 이미지 URL 목록을 받아 각 이미지를 비동기적으로 다운로드하고 메모리에 바이트(bytes) 형태로 저장하는 함수 구현
  - [x] 4.3 다운로드된 이미지 데이터 목록을 받아 단일 ZIP 파일 스트림(in-memory)으로 압축하는 함수 구현

- [ ] **5.0: Flask 라우트 및 비동기 통신 연동**
  - [ ] 5.1 `app.py`에 `/download` POST 라우트 생성. 요청에서 'username'을 받아 유효성 검사
  - [ ] 5.2 `/download` 라우트에서 `scraper`와 `utils` 모듈을 호출하여 스크래핑, 다운로드, 압축 프로세스 실행
  - [ ] 5.3 성공 시, 생성된 ZIP 파일을 `[계정명]_instagram_photos.zip` 이름으로 Flask `Response` 객체에 담아 반환
  - [ ] 5.4 스크래핑/다운로드 중 발생한 오류를 처리하고, 적절한 HTTP 상태 코드와 오류 메시지를 JSON 형식으로 반환
  - [ ] 5.5 `static/js/main.js`에서 '다운로드' 버튼 클릭 이벤트를 감지하고, `fetch` API를 사용하여 `/download`로 POST 요청 전송
  - [ ] 5.6 JavaScript에서 요청 시작 시 로딩 UI(예: 버튼 비활성화, 메시지 표시)를 활성화하고, 응답 수신 시 로딩 UI 비활성화
  - [ ] 5.7 JavaScript에서 API 응답을 확인하여, 성공 시 브라우저에서 파일 다운로드를 트리거하고, 오류 시 메시지 영역에 적절한 오류 문구 표시

- [ ] **6.0: CI/CD 파이프라인 구축 및 배포**
  - [ ] 6.1 `tests` 디렉터리에 각 모듈(`app`, `scraper`)에 대한 기본 단위/통합 테스트 케이스 작성
  - [ ] 6.2 `.github/workflows/ci.yml` 파일 생성
  - [ ] 6.3 main 브랜치에 코드가 푸시될 때 Python 환경 설정, `pip install`, `pytest`를 실행하는 GitHub Actions 워크플로우 정의