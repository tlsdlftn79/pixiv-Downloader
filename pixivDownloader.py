import tkinter as tk
from tkinter import simpledialog
from pixivpy3 import *
from PIL import Image, ImageTk
import requests
from io import BytesIO

# Pixiv API에 로그인
def login_to_pixiv():
    api = AppPixivAPI()
    api.auth(refresh_token="api키 입력")
    return api

# 이미지 다운로드 및 표시
def download_image(api, illust_id):
    json_result = api.illust_detail(illust_id)
    illust = json_result.illust
    
    # 연작 이미지 여부 확인
    if illust.meta_pages:  # 연작 이미지가 있는 경우
        images_url = [page.image_urls.original for page in illust.meta_pages]
    else:  # 단일 이미지만 있는 경우
        images_url = [illust.meta_single_page.get('original_image_url', illust.image_urls.large)]
    
    for idx, image_url in enumerate(images_url):
        # Referer 헤더 추가
        headers = {
            'Referer': 'https://app-api.pixiv.net/',
        }
        
        response = requests.get(image_url, headers=headers)
        img_data = response.content
        
        if response.status_code == 200:
            img = Image.open(BytesIO(img_data))
            
            # 이미지 저장 (연작 이미지의 경우 인덱스를 파일명에 추가)
            img.save(f"{illust_id}_{idx}.png")
            
            # tkinter에서 이미지 표시 준비
            img_tk = ImageTk.PhotoImage(img)
            panel = tk.Label(window, image=img_tk)
            panel.image = img_tk
            panel.pack()
        else:
            print(f"이미지 {idx}를 다운로드하지 못했습니다. 상태 코드:", response.status_code)
    
    # 다운로드 후 다시 작품번호 입력 받기
    request_illust_id()

# 작품번호 입력 받기
def request_illust_id():
    illust_id = simpledialog.askstring("입력", "작품번호를 입력하세요:", parent=window)
    if illust_id:  # 사용자가 입력을 취소하거나 빈 문자열을 입력하지 않았을 경우
        download_image(api, illust_id)
    else:  # 사용자가 입력을 취소하거나 빈 문자열을 입력했을 경우
        print("프로그램을 종료합니다.")
        window.quit()

# GUI 설정
window = tk.Tk()
window.geometry("800x600")

api = login_to_pixiv()

# 최초로 작품번호 입력 받기
request_illust_id()

window.mainloop()