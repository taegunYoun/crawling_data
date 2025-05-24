from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from time import sleep
import requests
import os

# 저장 폴더 생성
save_folder = "instagram_images"
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

# url 입력
url = input("url : ")

# 크롬드라이버 기본 설정
driver = webdriver.Chrome()
driver.implicitly_wait(10)
driver.get(url)

print("페이지 로딩 중...")
sleep(3)

# 이미지 URL 저장용 set (중복 방지)
img_urls = set()

def collect_current_images():
    """현재 페이지의 이미지들을 수집"""
    try:
        # 확인된 클래스명으로 이미지 찾기
        images = driver.find_elements(By.CLASS_NAME, "x5yr21d.xu96u03.x10l6tqk.x13vifvy.x87ps6o.xh8yej3")
        print(f"현재 페이지에서 {len(images)}개 이미지 발견")
        
        for img in images:
            src = img.get_attribute('src')
            if src and src not in img_urls:
                img_urls.add(src)
                print(f"이미지 추가: {len(img_urls)}번째")
        
        return len(images)
    except Exception as e:
        print(f"이미지 수집 중 오류: {e}")
        return 0

# 첫 번째 페이지에서 이미지 수집
print("첫 번째 페이지 이미지 수집...")
collect_current_images()

# 다음 버튼을 찾아서 계속 진행
try:
    page_count = 1
    max_pages = 20  # 최대 페이지 수 제한
    
    while page_count < max_pages:
        print(f"\n--- {page_count + 1}번째 페이지로 이동 시도 ---")
        
        try:
            # 다음 버튼 찾기 (여러 선택자 시도)
            next_button = None
            selectors_to_try = [
                "button[aria-label*='Next']",
                "button[aria-label*='다음']", 
                "._afxw._al46._al47",
                "[data-testid='right-chevron']",
                "svg[aria-label*='Next']",
                "svg[aria-label*='다음']"
            ]
            
            for selector in selectors_to_try:
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"다음 버튼 발견: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if next_button:
                # 버튼이 클릭 가능할 때까지 대기
                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(next_button)
                )
                next_button.click()
                print("다음 버튼 클릭 성공")
                sleep(2)  # 페이지 로딩 대기
                
                # 새 페이지에서 이미지 수집
                new_images_count = collect_current_images()
                
                if new_images_count == 0:
                    print("더 이상 새로운 이미지가 없습니다.")
                    break
                    
                page_count += 1
            else:
                print("다음 버튼을 찾을 수 없습니다. 마지막 페이지입니다.")
                break
                
        except TimeoutException:
            print("다음 버튼 클릭 대기 시간 초과")
            break
        except Exception as e:
            print(f"페이지 이동 중 오류: {e}")
            break

except KeyboardInterrupt:
    print("\n사용자가 중단했습니다.")

print(f"\n=== 수집 완료 ===")
print(f"총 {len(img_urls)}개의 고유한 이미지를 수집했습니다.")

# 이미지 다운로드
if len(img_urls) > 0:
    print("\n이미지 다운로드 시작...")
    success_count = 0
    
    for i, img_url in enumerate(img_urls, 1):
        try:
            print(f"다운로드 중 ({i}/{len(img_urls)}): ", end="")
            response = requests.get(img_url, timeout=10)
            
            if response.status_code == 200:
                filename = os.path.join(save_folder, f'image_{i:03d}.jpg')
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"성공 - {filename}")
                success_count += 1
            else:
                print(f"실패 (HTTP {response.status_code})")
                
        except Exception as e:
            print(f"실패 ({str(e)})")
    
    print(f"\n다운로드 완료: {success_count}/{len(img_urls)}개 성공")
    print(f"저장 위치: {os.path.abspath(save_folder)}")
else:
    print("다운로드할 이미지가 없습니다.")

driver.quit()
print("작업 완료!")