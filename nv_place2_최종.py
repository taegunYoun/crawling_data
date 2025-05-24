from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import random
import re

def convert_map_to_place_url(input_url):
    match = re.search(r'/place/(\d+)', input_url)
    if match:
        place_id = match.group(1)
        return f"https://m.place.naver.com/restaurant/{place_id}/review/visitor"
    else:
        return input_url

def crawl_naver_reviews(url, filename):
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # 창 없이 실행하려면 주석 해제
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1')

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(2)

    # 스크롤 끝까지 내리기
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(1.5, 3.5))
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # ✅ '더보기' 버튼 클릭
    more_buttons = driver.find_elements(By.CSS_SELECTOR, 'a.pui__3Xn2I')  # 더보기 버튼
    for btn in more_buttons:
        try:
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.3)
        except:
            pass

    review_blocks = driver.find_elements(By.CSS_SELECTOR, 'div.pui__vn15t2')
    nickname_elements = driver.find_elements(By.CSS_SELECTOR, 'span.pui__NMi-Dp')
    date_elements = driver.find_elements(By.CSS_SELECTOR, 'div.pui__QKE5Pr time')

    reviews = []
    for block, nickname, date in zip(review_blocks, nickname_elements, date_elements):
        try:
            full_review = block.find_elements(By.TAG_NAME, 'a')[0].text  # 첫 번째 <a>만 추출
            reviews.append({
                '작성자': nickname.text,
                '리뷰내용': full_review,
                '작성일': date.text
            })
        except:
            continue


    # 파일명 확장자 확인 및 저장
    if not filename.endswith(".csv"):
        filename += ".csv"

    if reviews:
        df = pd.DataFrame(reviews)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✅ 크롤링 완료! 리뷰 {len(reviews)}개를 '{filename}'에 저장했어.")
    else:
        print("⚠️ 리뷰를 찾지 못했어. 페이지 구조가 바뀌었을 수도 있어.")

    driver.quit()

if __name__ == "__main__":
    input_url = input("리뷰 페이지 또는 지도 URL을 입력하세요: ").strip()
    converted_url = convert_map_to_place_url(input_url)
    filename = input("저장할 파일명을 입력하세요 (예: reviews.csv): ").strip()
    crawl_naver_reviews(converted_url, filename)
