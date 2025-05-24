다음은 해당 Instagram 이미지 수집 자동화 스크립트용 `README.md` 파일 예시입니다. 이모티콘 없이, 복사 후 바로 사용할 수 있도록 구성했습니다.

---

# Instagram Image Scraper

Python 및 Selenium을 이용하여 Instagram 게시물에서 이미지를 자동으로 수집하고 저장하는 스크립트입니다.
캐러셀 형식의 게시물도 자동으로 탐색하며, 중복 없이 고해상도 이미지를 다운로드합니다.

## 주요 기능

* 게시물 URL 입력을 통한 자동 이미지 수집
* 캐러셀 형식 게시물의 다음 버튼 자동 클릭
* 중복 제거 및 해상도 필터링 적용
* 사용자 지정 폴더 및 파일명으로 저장
* 이미지 URL 정보 파일 (`_info.txt`) 저장

## 설치 및 실행 방법

### 1. 필수 라이브러리 설치

```bash
pip install selenium requests
```

크롬 드라이버는 사용 중인 Chrome 브라우저 버전에 맞는 버전을 설치하고, 환경변수에 등록하거나 실행 파일과 같은 경로에 위치시켜야 합니다.
[ChromeDriver 다운로드](https://sites.google.com/chromium.org/driver/)

### 2. 스크립트 실행

```bash
python instagram_scraper.py
```

실행 시 아래와 같은 입력을 요구합니다:

* 저장할 폴더 이름
* 파일명 앞에 붙일 이름 (예: piro\_22)
* Instagram 게시물 URL

### 3. 결과물

* 이미지 파일: 지정한 폴더에 순차적으로 저장 (예: `piro_22_001.jpg`)
* 정보 파일: URL 및 수집된 이미지 목록 저장 (`piro_22_info.txt`)

## 예시

```
저장할 폴더 이름을 입력하세요: instagram_post
파일명 앞에 붙일 이름을 입력하세요 (예: piro_22): piro_22
Instagram 게시물 URL: https://www.instagram.com/p/XXXXXXXXX/
```

결과:

```
instagram_post/
├── piro_22_001.jpg
├── piro_22_002.jpg
├── ...
└── piro_22_info.txt
```

## 주의사항

* 로그인 없이 접근 가능한 게시물만 수집 가능합니다.
* Instagram UI 구조 변경 시 CSS 선택자 수정이 필요합니다.
* 너무 빠른 요청이나 반복 사용 시 Instagram 측에서 일시 차단될 수 있습니다.
* 동영상 콘텐츠는 수집되지 않습니다 (이미지 전용).

---
