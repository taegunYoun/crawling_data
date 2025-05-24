from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from time import sleep
import requests
import os

# 파일명과 폴더명 입력받기
folder_name = input("저장할 폴더 이름을 입력하세요: ")
if not folder_name:
    folder_name = "instagram_post"

file_prefix = input("파일명 앞에 붙일 이름을 입력하세요 (예: piro_22): ")
if not file_prefix:
    file_prefix = "image"

# 폴더 생성
if not os.path.exists(folder_name):
    os.makedirs(folder_name)
    print(f"'{folder_name}' 폴더를 생성했습니다.")

# url 입력
url = input("Instagram 게시물 URL: ")

# 크롬드라이버 기본 설정
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=options)
driver.implicitly_wait(10)
driver.get(url)

print("페이지 로딩 중...")
sleep(5)  # 로딩 시간 증가

# 이미지 URL 저장용 리스트 (순서 유지)
img_urls = []

def get_current_image():
    """현재 보이는 메인 이미지 수집"""
    try:
        # 메인 게시물 이미지만 찾기 (더 구체적인 선택자)
        img_selectors = [
            "article img.x5yr21d.xu96u03.x10l6tqk.x13vifvy.x87ps6o.xh8yej3",
            "div[role='button'] img.x5yr21d.xu96u03.x10l6tqk.x13vifvy.x87ps6o.xh8yej3",
            "article div img"
        ]
        
        for selector in img_selectors:
            try:
                images = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"선택자 '{selector}'로 {len(images)}개 이미지 발견")
                
                for img in images:
                    src = img.get_attribute('src')
                    
                    # 이미지 필터링
                    if src and src not in img_urls:
                        # 실제 게시물 이미지인지 확인 (크기와 경로로)
                        if 'cdninstagram.com' in src and ('e35' in src or 'e15' in src):
                            # 이미지 크기 확인
                            try:
                                width = driver.execute_script("return arguments[0].naturalWidth;", img)
                                height = driver.execute_script("return arguments[0].naturalHeight;", img)
                                
                                if width > 200 and height > 200:  # 충분히 큰 이미지만
                                    img_urls.append(src)
                                    print(f"✓ 이미지 {len(img_urls)}번째 추가 ({width}x{height})")
                                    
                                    # 이미지 설명도 출력
                                    alt = img.get_attribute('alt')
                                    if alt:
                                        print(f"  설명: {alt[:80]}...")
                                    
                                    return True
                            except:
                                # 크기를 구할 수 없으면 그냥 추가
                                img_urls.append(src)
                                print(f"✓ 이미지 {len(img_urls)}번째 추가")
                                return True
                
            except Exception as e:
                continue
        
        return False
        
    except Exception as e:
        print(f"이미지 수집 중 오류: {e}")
        return False

def find_next_button():
    """다음 버튼을 찾는 함수"""
    # 확인된 선택자들 (우선순위대로)
    selectors = [
        "button[aria-label='다음']",
        "button[class*='_afxw'][class*='_al46'][class*='_al47']",
        "._afxw._al46._al47",
        "button[aria-label*='다음']",
        "button[aria-label*='Next']",
        "button[aria-label='Next']"
    ]
    
    for selector in selectors:
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, selector)
            for btn in buttons:
                if btn.is_displayed() and btn.is_enabled():
                    # 버튼 위치 확인 (게시물 영역 내부인지)
                    location = btn.location
                    size = btn.size
                    if location['y'] > 50 and size['width'] > 0:
                        print(f"다음 버튼 발견: {selector}")
                        return btn
        except:
            continue
    
    return None

# 첫 번째 이미지 수집
print("=== 게시물의 이미지들 수집 시작 ===")
get_current_image()

# 캐러셀이 있는지 확인하고 모든 이미지 수집
carousel_count = 0
max_attempts = 20

print(f"\n캐러셀 이미지 수집 시작...")

while carousel_count < max_attempts:
    print(f"\n--- {carousel_count + 1}번째 다음 버튼 클릭 시도 ---")
    
    # 다음 버튼 찾기
    next_button = find_next_button()
    
    if next_button:
        try:
            before_count = len(img_urls)
            
            # 버튼 클릭 (여러 방법 시도)
            click_success = False
            
            # 방법 1: 일반 클릭
            try:
                next_button.click()
                click_success = True
                print("✓ 일반 클릭 성공")
            except:
                pass
            
            # 방법 2: JavaScript 클릭
            if not click_success:
                try:
                    driver.execute_script("arguments[0].click();", next_button)
                    click_success = True
                    print("✓ JavaScript 클릭 성공")
                except:
                    pass
            
            # 방법 3: ActionChains 클릭
            if not click_success:
                try:
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(driver)
                    actions.move_to_element(next_button).click().perform()
                    click_success = True
                    print("✓ ActionChains 클릭 성공")
                except:
                    pass
            
            if click_success:
                sleep(2.5)  # 이미지 로딩 대기
                
                # 새 이미지 수집
                found_new = get_current_image()
                after_count = len(img_urls)
                
                if not found_new or after_count == before_count:
                    print("더 이상 새로운 이미지가 없습니다.")
                    break
                
                carousel_count += 1
            else:
                print("❌ 모든 클릭 방법 실패")
                break
                
        except Exception as e:
            print(f"버튼 클릭 처리 중 오류: {e}")
            break
    else:
        print("다음 버튼을 찾을 수 없습니다. 캐러셀 종료.")
        break

print(f"\n=== 수집 완료 ===")
print(f"총 {len(img_urls)}개의 이미지를 수집했습니다.")

# 이미지 다운로드
if len(img_urls) > 0:
    print(f"\n이미지 다운로드 시작...")
    print(f"저장 위치: {os.path.abspath(folder_name)}")
    print(f"파일명 형식: {file_prefix}_001.jpg")
    
    success_count = 0
    
    for i, img_url in enumerate(img_urls, 1):
        try:
            print(f"다운로드 중 ({i}/{len(img_urls)}): ", end="")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(img_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                filename = os.path.join(folder_name, f'{file_prefix}_{i:03d}.jpg')
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"성공 - {filename}")
                success_count += 1
            else:
                print(f"실패 (HTTP {response.status_code})")
                
        except Exception as e:
            print(f"실패 ({str(e)})")
    
    print(f"\n=== 다운로드 완료 ===")
    print(f"성공: {success_count}/{len(img_urls)}개")
    print(f"저장 위치: {os.path.abspath(folder_name)}")
    
    # URL 정보 저장
    info_file = os.path.join(folder_name, f"{file_prefix}_info.txt")
    with open(info_file, 'w', encoding='utf-8') as f:
        f.write(f"Instagram 게시물: {url}\n")
        f.write(f"수집 이미지 수: {len(img_urls)}\n")
        f.write(f"파일명 형식: {file_prefix}_XXX.jpg\n\n")
        f.write("=== 이미지 URL 목록 ===\n")
        for i, img_url in enumerate(img_urls, 1):
            f.write(f"{i:03d}: {img_url}\n")
    print(f"URL 정보가 {info_file}에 저장되었습니다.")
    
else:
    print("다운로드할 이미지가 없습니다.")

driver.quit()
print("\n🎉 작업 완료!")