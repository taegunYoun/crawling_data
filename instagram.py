from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import re

# 🎯 대상 계정 ID
target_username = 'fcbarcelona'  # 원하는 인스타 ID로 변경 가능

# 🎯 크롬 드라이버 설정
options = Options()
# options.add_argument("--headless")
options.add_argument("user-agent=Mozilla/5.0")
driver = webdriver.Chrome(options=options)

# 🎯 수동 로그인
driver.get("https://www.instagram.com/accounts/login/")
print("🔐 로그인 후 40초 대기...")
time.sleep(40)

# 🎯 프로필 페이지 이동
profile_url = f"https://www.instagram.com/{target_username}/"
driver.get(profile_url)
time.sleep(7)  # 페이지 로딩 시간 늘림

# 🎯 게시물 링크 수집 (최대 50개)
MAX_POSTS = 15
SCROLL_PAUSE = 2
post_links = set()

while len(post_links) < MAX_POSTS:
    links = driver.find_elements(By.XPATH, '//a[contains(@href, "/p/")]')
    for link in links:
        post_links.add(link.get_attribute('href'))
        if len(post_links) >= MAX_POSTS:
            break
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE)

print(f"📸 수집된 게시물 수: {len(post_links)}")

# 🎯 게시물별 데이터 추출
post_data = []
for idx, url in enumerate(list(post_links)):
    print(f"\n[{idx+1}/{len(post_links)}] 게시물 처리 중: {url}")
    driver.get(url)
    time.sleep(3)

    # 본문
    try:
        caption = driver.find_element(By.TAG_NAME, 'h1').text
        print(f"본문 추출 성공: {caption[:30]}..." if len(caption) > 30 else f"본문 추출 성공: {caption}")
    except:
        caption = ""
        print("본문 추출 실패")

    # 좋아요 수 - 여러 방법 시도
    likes = 0
    like_text = ""
    
    # 방법 1: span 요소에서 직접 찾기
    try:
        # 모든 span 요소를 가져와서 정규식으로 "만" 포함된 텍스트 찾기
        spans = driver.find_elements(By.TAG_NAME, 'span')
        for span in spans:
            try:
                text = span.text.strip()
                if '만' in text and re.search(r'[\d,.]+만', text):
                    # 숫자와 '만'만 추출
                    number_match = re.search(r'([\d,.]+)만', text)
                    if number_match:
                        number_str = number_match.group(1).replace(',', '')
                        likes = float(number_str) * 10000
                        like_text = f"{number_str}만"
                        print(f"방법 1 성공 - 추출: '{like_text}', 변환: {int(likes)}")
                        break
            except:
                continue
    except Exception as e:
        print(f"방법 1 실패: {e}")
    
    # 방법 2: 클래스로 찾기 (좋아요 수가 아직 추출되지 않은 경우)
    if likes == 0:
        try:
            # 일반적인 클래스 조합으로 시도
            like_elements = driver.find_elements(By.XPATH, '//span[contains(@class, "x1vvkbs")]')
            if like_elements:
                for element in like_elements:
                    try:
                        text = element.text.strip()
                        if '만' in text and re.search(r'[\d,.]+만', text):
                            number_match = re.search(r'([\d,.]+)만', text)
                            if number_match:
                                number_str = number_match.group(1).replace(',', '')
                                likes = float(number_str) * 10000
                                like_text = f"{number_str}만"
                                print(f"방법 2 성공 - 추출: '{like_text}', 변환: {int(likes)}")
                                break
                    except:
                        continue
        except Exception as e:
            print(f"방법 2 실패: {e}")
    
    # 방법 3: ARIA 레이블 사용 (좋아요 수가 아직 추출되지 않은 경우)
    if likes == 0:
        try:
            # aria-label 속성으로 시도 (영어 "likes" 또는 한국어 "좋아요" 포함)
            like_elements = driver.find_elements(By.XPATH, '//*[contains(@aria-label, "likes") or contains(@aria-label, "좋아요")]')
            if like_elements:
                for element in like_elements:
                    try:
                        aria_label = element.get_attribute('aria-label')
                        if aria_label and ('만' in aria_label or 'likes' in aria_label.lower() or '좋아요' in aria_label):
                            # 숫자 추출
                            if '만' in aria_label:
                                number_match = re.search(r'([\d,.]+)만', aria_label)
                                if number_match:
                                    number_str = number_match.group(1).replace(',', '')
                                    likes = float(number_str) * 10000
                                    like_text = f"{number_str}만"
                                    print(f"방법 3 성공 - 추출: '{like_text}', 변환: {int(likes)}")
                                    break
                    except:
                        continue
        except Exception as e:
            print(f"방법 3 실패: {e}")
    
    # 모든 방법 실패 시 페이지 소스 저장 (디버깅용)
    if likes == 0:
        print(f"모든 방법 실패!")
        
        # 디버깅을 위해 HTML 일부 저장
        with open(f"debug_post_{idx+1}.html", "w", encoding="utf-8") as f:
            # 전체 페이지 소스가 너무 크므로 일부만 저장
            f.write(driver.page_source[:10000])
        print(f"디버깅용 HTML 저장됨: debug_post_{idx+1}.html")

    post_data.append({
        "URL": url,
        "본문": caption,
        "좋아요 수": int(likes),
        "좋아요 수(만 단위)": like_text
    })
    
    print(f"최종 결과 - URL: {url}, 좋아요 수: {int(likes)}, 좋아요 수(만 단위): {like_text}")

# 🎯 좋아요 수 기준 상위 10개 정렬
df = pd.DataFrame(post_data)
df_top10 = df.sort_values(by="좋아요 수", ascending=False).head(10)

print("\n===== 추출 결과 =====")
print(df[["URL", "좋아요 수", "좋아요 수(만 단위)"]])

# 🎯 사용자에게 파일 이름 입력받기
filename = input("\n📄 저장할 CSV 파일 이름을 입력하세요 (확장자 .csv 생략 가능): ").strip()
if not filename.endswith(".csv"):
    filename += ".csv"

# 🎯 파일 저장
df_top10.to_csv(filename, index=False, encoding="utf-8-sig")
print(f"✅ 저장 완료: {filename}")

# 🎯 드라이버 종료
driver.quit()