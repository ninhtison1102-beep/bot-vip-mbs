import requests
from bs4 import BeautifulSoup
import time
import datetime
import os
import json
from flask import Flask
from threading import Thread

# --- HỆ THỐNG CHỐNG NGỦ GẬT ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Chứng Khoán đang thức và chạy rất mượt!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive() 

# ==========================================================
# --- CẤU HÌNH NHÀ KHO ĐÁM MÂY VÀ BỘ LỌC ---
# ==========================================================

# 🔴 ANH DÁN CÁI MÃ BUCKET VỪA COPY VÀO ĐÂY NHÉ:
KVDB_BUCKET = 'CRbYngwJV8ydx7UrWrgRcm'
KVDB_URL = f"https://kvdb.io/bucket/{KVDB_BUCKET}/history"

TELEGRAM_TOKEN = '8262052565:AAHCs6M3HIo2R4-uljDAMKVbVPOYllTthQ8'
YOUR_GROUP_ID = '-4998239976'

URLS_TO_SCAN = [
    "https://cafef.vn/tai-chinh-ngan-hang.chn",
    "https://cafef.vn/thi-truong-chung-khoan.chn",
    "https://cafef.vn/doanh-nghiep.chn",
    "https://cafef.vn/kinh-te-vi-mo-dau-tu.chn",
    "https://vneconomy.vn/tai-chinh.htm",
    "https://vneconomy.vn/chung-khoan.htm",
    "https://nguoiquansat.vn/tai-chinh",
    "https://nguoiquansat.vn/chung-khoan",
    "https://vtcnews.vn/kinh-te-c167.html",
    "https://baochinhphu.vn/kinh-te.htm",
    "https://vov.vn/kinh-te",
    "https://f319.com/forums/thi-truong-chung-khoan.3/", 
    "https://mekongasean.vn/",                            
    "https://mekongasean.vn/dien-dan-dau-tu/chung-khoan"
]

SECTOR_KEYWORDS = [
    'NGÂN HÀNG', 'LÃI SUẤT', 'TÍN DỤNG', 'NỢ XẤU', 
    'CHỨNG KHOÁN', 'TRÁI PHIẾU', 'ROOM',
    'BẤT ĐỘNG SẢN', 'DẦU KHÍ', 'XĂNG DẦU', 
    'THỦ TƯỚNG', 'CHÍNH PHỦ', 'BỘ CÔNG THƯƠNG', 'THUẾ',
    'GDP', 'CPI', 'LẠM PHÁT', 'NHNN', 'TỶ GIÁ',
    'CAO TỐC', 'DỰ ÁN', 'SÂN BAY', 'HẠ TẦNG', 'BOT'
]

VIP_TICKERS = ['EIB','ABB', 'SHB', 'MBS', 'STB', 'SSI', 'HCM', 'VCB', 'BID', 'CTG', 'VPB', 'TCB', 'CTD', 'ABC', 'DDV', 'PVT', 'SHS', 'KBC', 'MBB', 'BVS', 'OIL', 'PLX', 'PVP', 'PVT','DRI','PGB','GVR','PC1','POW','VHM','VIC','HAH','DPR','VND','VGC','FPT','VCI','ANV','MSN','DGW','PGV','HAX','TV1','MWG']

HOT_KEYWORDS = [
    'LỢI NHUẬN', 'LÃI', 'LỖ', 'DOANH THU', 'EPS', 'BOOK VALUE', 'CỔ TỨC', 
    'BÁO CÁO TÀI CHÍNH', 'BCTC', 'KẾ HOẠCH', 'ĐẠT', 'VƯỢT', 'KỲ VỌNG',
    'HỢP ĐỒNG', 'KÝ KẾT', 'DỰ ÁN', 'MỞ RỘNG', 'ĐỘI TÀU', 'KHỞI CÔNG', 
    'THÂU TÓM', 'M&A', 'TĂNG VỐN', 'PHÁT HÀNH',
    'XĂNG', 'ĐIỆN', 'GIÁ', 'THUẾ', 'QUY HOẠCH', 'PHÊ DUYỆT',
    'TĂNG TRƯỞNG', 'DỰ BÁO', 'CHỈ ĐẠO',
    'BẮT BỚ', 'KHỞI TỐ', 'TIN ĐỒN', 'RUMOR',
    'RÚT', 'DỪNG', 'HỦY', 'ĐÌNH CHỈ', 'THU HỒI'
]

# --- HỆ THỐNG TRÍ NHỚ VĨNH CỬU ---
def load_history():
    print("☁️ Đang tải trí nhớ từ Đám Mây...")
    try:
        r = requests.get(KVDB_URL)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

def save_history(links_list):
    try:
        # Chỉ nhớ 500 tin gần nhất để kho chứa luôn nhẹ và chạy nhanh
        links_to_save = links_list[-500:] 
        requests.post(KVDB_URL, json=links_to_save)
    except Exception as e:
        print(f"Lỗi lưu kho: {e}")

# Kéo lịch sử về RAM khi vừa bật máy
sent_links = load_history()
is_database_empty = len(sent_links) == 0

def get_sapo(link_detail, source_name):
    if source_name == "F319":
        return "⚠️ CẢNH BÁO: Đây là tin từ diễn đàn F319 (Tin đồn). Vui lòng kiểm chứng kỹ."
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(link_detail, headers=headers, timeout=10)
        soup = BeautifulSoup(r.content, 'html.parser')
        sapo = soup.find(class_='sapo') 
        if not sapo: sapo = soup.find(class_='detail__summary') 
        if not sapo: sapo = soup.find(class_='cms-desc') 
        if not sapo: sapo = soup.find('h2') 
        if sapo: return sapo.get_text().strip()
    except: return "Không lấy được tóm tắt."
    return ""

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": YOUR_GROUP_ID, "text": message}
        requests.post(url, data=data)
    except Exception as e: print(f"Lỗi gửi tin: {e}")

def check_news(silent_mode=False):
    if not silent_mode:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Đang quét các đầu báo... (10s/lần)")
    headers = {'User-Agent': 'Mozilla/5.0'}

    for url in URLS_TO_SCAN:
        try:
            domain = ""
            source_name = ""
            if "cafef.vn" in url: 
                domain, source_name = "https://cafef.vn", "CafeF"
            elif "vneconomy.vn" in url: 
                domain, source_name = "https://vneconomy.vn", "VnEconomy"
            elif "nguoiquansat.vn" in url: 
                domain, source_name = "https://nguoiquansat.vn", "Người Quan Sát"
            elif "vtcnews.vn" in url:
                domain, source_name = "https://vtcnews.vn", "VTC News"
            elif "baochinhphu.vn" in url:
                domain, source_name = "https://baochinhphu.vn", "Báo Chính Phủ"
            elif "vov.vn" in url:
                domain, source_name = "https://vov.vn", "VOV"
            elif "f319.com" in url:
                domain, source_name = "https://f319.com", "F319"
            elif "mekongasean.vn" in url:
                domain, source_name = "https://mekongasean.vn", "Mekong ASEAN"

            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            news_items = []
            if source_name == "F319": news_items = soup.find_all('h3', class_='title')
            elif source_name in ["CafeF", "VTC News"]: news_items = soup.find_all('h3')
            elif source_name == "VnEconomy": news_items = soup.find_all('h3', class_='story__title')
            else: news_items = soup.find_all(['h2', 'h3'])

            for item in news_items:
                link_tag = item.find('a')
                if not link_tag: continue

                title = link_tag.get_text().strip()
                link = link_tag['href']

                if not link.startswith("http"):
                    if not link.startswith("/") and not domain.endswith("/"): link = domain + "/" + link
                    else: link = domain + link

                if link in sent_links: continue

                title_upper = title.upper()
                is_match = False
                prefix = ""

                for ticker in VIP_TICKERS:
                    if ticker in title_upper:
                        is_match, prefix = True, f"🔥 CP VIP {ticker}: "
                        break

                if not is_match:
                    for sector in SECTOR_KEYWORDS:
                        if sector in title_upper:
                            for hot in HOT_KEYWORDS:
                                if hot in title_upper:
                                    is_match, prefix = True, f"📢 TIN HOT {sector}: "
                                    break
                        if is_match: break

                if is_match:
                    if silent_mode:
                        print(f"--> [KHỞI TẠO KHO] Nạp: {title}")
                        sent_links.append(link)
                    else:
                        print(f"--> Tin mới ({source_name}): {title}")
                        summary = get_sapo(link, source_name)
                        warning_icon = "⚠️" if source_name == "F319" else "📰"
                        msg = f"{warning_icon} NGUỒN: {source_name}\n{prefix}\n{title.upper()}\n\n{summary}\n\n👉 Link gốc: {link}"
                        
                        send_telegram(msg)
                        sent_links.append(link)
                        save_history(sent_links) # Vừa báo Telegram là cất luôn vào kho Đám Mây

        except Exception as e:
            pass

print("--- TOOL SIÊU GIÁN ĐIỆP ĐÃ LÊN MÂY KHỞI ĐỘNG ---")

# Nếu kho trắng tinh (chạy lần đầu tiên trong đời), cho quét 1 vòng im lặng để nạp sổ
if is_database_empty:
    print("--- KHO ĐANG TRỐNG! CHẠY VÒNG ĐẦU ĐỂ KHỞI TẠO TRÍ NHỚ ---")
    check_news(silent_mode=True)
    save_history(sent_links)
    print("--- NẠP XONG TRÍ NHỚ. BẮT ĐẦU CHẾ ĐỘ SĂN TIN CẢNH GIÁC CAO ĐỘ ---")

# Vòng lặp vĩnh cửu đi săn
while True:
    try:
        check_news(silent_mode=False)
        time.sleep(10) 
    except KeyboardInterrupt:
        break
