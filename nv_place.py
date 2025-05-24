from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import os

def extract_place_info(url):
    """네이버 플레이스 URL에서 정보 추출"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
    
    service = Service()
    driver = webdriver.Chrome(options=chrome_options, service=service)
    
    place_info = {
        "상호명": "정보 없음",
        "업종명": "정보 없음",
        "주소": "정보 없음",
        "찾아가는길": "정보 없음",
        "영업시간": "정보 없음",
        "전화번호": "정보 없음",
        "홈페이지": "정보 없음",
        "편의시설": "정보 없음",
    }
    
    try:
        driver.get(url)
        time.sleep(3)
        
        try:
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#entryIframe"))
            )
            driver.switch_to.frame(iframe)
        except:
            pass
        
        # 각 항목 추출
        try: place_info["상호명"] = driver.find_element(By.CSS_SELECTOR, "span.GHAhO").text.strip()
        except: pass
        try: place_info["업종명"] = driver.find_element(By.CSS_SELECTOR, "span.lnJFt").text.strip()
        except: pass
        try: place_info["주소"] = driver.find_element(By.CSS_SELECTOR, "span.LDgIH").text.strip()
        except: pass
        try: place_info["찾아가는길"] = driver.find_element(By.CSS_SELECTOR, "div.nZapA").text.strip()
        except: pass
        try: place_info["영업시간"] = driver.find_element(By.CSS_SELECTOR, "div.A_cdD").text.strip().replace('\n', ' ')
        except: pass
        try: place_info["전화번호"] = driver.find_element(By.CSS_SELECTOR, "span.xlx7Q").text.strip()
        except: pass
        try: place_info["홈페이지"] = driver.find_element(By.CSS_SELECTOR, "a.place_bluelink.CHmqa").get_attribute("href")
        except: pass
        try: place_info["편의시설"] = driver.find_element(By.CSS_SELECTOR, "div.xPvPE").text.strip()
        except: pass
        
    except Exception as e:
        print(f"전체 처리 중 오류 발생: {e}")
    
    finally:
        driver.quit()
    
    return place_info

def save_to_csv(data, filename="naver_place_data.csv"):
    """추출한 정보를 CSV 파일로 저장"""
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = data.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(data)
    
    print(f"\n데이터가 '{filename}' 파일에 저장되었습니다.")

def main():
    """메인 함수: URL 입력 받고 정보 추출"""
    print("\n===== 네이버 플레이스 정보 추출기 =====")
    print("종료하려면 'q' 또는 'exit'를 입력하세요.")
    
    while True:
        url = input("\n네이버 플레이스 URL을 입력하세요: ")
        
        if url.lower() in ['q', 'exit', 'quit']:
            print("프로그램을 종료합니다.")
            break
        
        if not url.startswith(("https://map.naver.com", "https://m.place.naver.com")):
            print("올바른 네이버 지도/플레이스 URL이 아닙니다.")
            continue
        
        place_data = extract_place_info(url)
        
        print("\n===== 추출 결과 요약 =====")
        for key, value in place_data.items():
            print(f"{key}: {value}")
        
        save_option = input("\n이 정보를 CSV 파일로 저장하시겠습니까? (y/n): ")
        if save_option.lower() == 'y':
            filename = input("저장할 파일명을 입력하세요 (기본: naver_place_data.csv): ")
            if not filename:
                filename = "naver_place_data.csv"
            if not filename.endswith('.csv'):
                filename += '.csv'
            
            save_to_csv(place_data, filename)

if __name__ == "__main__":
    main()
