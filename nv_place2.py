from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import random
import re

def convert_map_to_place_url(input_url):
    """
    map.naver.com URL을 m.place.naver.com 리뷰 URL로 변환해주는 함수
    """
    # place ID를 추출
    match = re.search(r'/place/(\d+)', input_url)
    if match:
        place_id = match.group(1)
        # m.place.naver.com 리뷰 페이지 URL로 변환
        return f"https://m.place.naver.com/restaurant/{place_id}/review/visitor"
    else:
        # 이미 m.place.naver.com이라면 그대로!!!!!!!!!!!!
        return input_url

def crawl_naver_reviews(url):
    # 크롬 드라이버 옵션 설정
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # 처음엔 창 보이게
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
        time.sleep(random.uniform(1.5, 3.5))  # 랜덤 딜레이
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # 리뷰, 작성자, 작성일 긁어오기
    review_elements = driver.find_elements(By.CSS_SELECTOR, 'div.pui__vn15t2 a')
    nickname_elements = driver.find_elements(By.CSS_SELECTOR, 'span.pui__NMi-Dp')
    date_elements = driver.find_elements(By.CSS_SELECTOR, 'div.pui__QKE5Pr time')

    # 데이터 정리
    reviews = []
    for review, nickname, date in zip(review_elements, nickname_elements, date_elements):
        reviews.append({
            '작성자': nickname.text,
            '리뷰내용': review.text,
            '작성일': date.text
        })

    # 저장
    if reviews:
        df = pd.DataFrame(reviews)
        df.to_csv('naver_place_reviews.csv', index=False, encoding='utf-8-sig')
        print(f"✅ 크롤링 완료! 리뷰 {len(reviews)}개를 'naver_place_reviews.csv'로 저장했어.")
    else:
        print("⚠️ 리뷰를 찾지 못했어. 페이지 구조가 달라졌을 수도 있어.")

    driver.quit()

if __name__ == "__main__":
    #여기서 그냥 아무 URL 넣으면 알아서 변환하고 크롤링
    input_url = input("리뷰 페이지 또는 지도 URL을 입력하세요: ").strip()
    converted_url = convert_map_to_place_url(input_url)
    crawl_naver_reviews(converted_url)
