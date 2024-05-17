import tkinter as tk
from tkinter import simpledialog, ttk  # ttk 모듈 추가
from pixivpy3 import *
from PIL import Image, ImageTk
import requests
from io import BytesIO

# Pixiv API에 로그인
def login_to_pixiv():
    api = AppPixivAPI()
    api.auth(refresh_token="픽시브 api 토큰번호")
    return api

def show_image(idx, images_url):
    progress['maximum'] = len(images_url)  # 진행바 최대값 설정
    if idx < len(images_url):
        image_url = images_url[idx]

        headers = {
            'Referer': 'https://app-api.pixiv.net/',
        }
        response = requests.get(image_url, headers=headers)
        img_data = response.content

        if response.status_code == 200:
            img = Image.open(BytesIO(img_data))
            
            # 이미지 크기 조정
            img = img.resize((400, 400), Image.Resampling.LANCZOS)
            
            img.save(f"{illust_id}_{idx}.png")
            img_tk = ImageTk.PhotoImage(img)
            panel.configure(image=img_tk)
            panel.image = img_tk
            
            # 진행바 업데이트
            progress['value'] = idx + 1
            progress.update()

            # 5초 후에 다음 이미지 표시
            window.after(5000, lambda: show_image(idx + 1, images_url))
        else:
            print(f"이미지 {idx}를 다운로드하지 못했습니다. 상태 코드:", response.status_code)
    else:
        # 모든 이미지를 표시한 후 다시 작품번호 입력 받기
        request_illust_id()

# 이미지 다운로드 및 표시
def download_image(api, illust_id):
    json_result = api.illust_detail(illust_id)
    illust = json_result.illust
    
    if illust.meta_pages:  # 연작 이미지가 있는 경우
        images_url = [page.image_urls.original for page in illust.meta_pages]
    else:  # 단일 이미지만 있는 경우
        images_url = [illust.meta_single_page.get('original_image_url', illust.image_urls.large)]

    show_image(0, images_url)

# 작품번호 입력 받기
def request_illust_id():
    global illust_id
    illust_id = simpledialog.askstring("입력", "작품번호를 입력하세요:", parent=window)
    if illust_id:
        # 다운로드 시작 시 진행바 초기화
        progress['value'] = 0
        download_image(api, illust_id)
    else:
        print("프로그램을 종료합니다.")
        window.quit()

# GUI 설정
window = tk.Tk()
window.geometry("400x450")  # 창 크기 조정

panel = tk.Label(window)  # panel을 전역 변수로 초기화
panel.pack()

# 진행바 추가
progress = ttk.Progressbar(window, length=100, mode='determinate')
progress.pack(pady=20)

api = login_to_pixiv()

illust_id = None  # illust_id를 전역 변수로 선언

# 최초로 작품번호 입력 받기
request_illust_id()

window.mainloop()