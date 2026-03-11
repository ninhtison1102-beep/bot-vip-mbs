import requests
from bs4 import BeautifulSoup
import time
import datetime
import os
from flask import Flask
from threading import Thread

# --- HỆ THỐNG CHỐNG NGỦ GẬT (KEEP ALIVE) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Chứng Khoán đang thức và chạy rất mượt!"

def run():
    # Lấy port Render tự động cấp, nếu không có thì mặc định 8080
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive() # Gọi hàm đánh thức Bot ngay lập tức

# ==========================================================
# --- CODE GỐC BẮT ĐẦU TỪ ĐÂY ---
# ==========================================================

# --- CẤU HÌNH ---
TELEGRAM_TOKEN = '8262052565:AAHCs6M3HIo2R4-uljDAMKVbVPOYllTthQ8'
YOUR_GROUP_ID = '-4998239976'
HISTORY_FILE = "tin_da_gui.txt"

# --- DANH SÁCH URL CẦN QUÉT ---
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

# --- TỪ KHÓA BỘ LỌC ---
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

# --- CÁC HÀM XỬ LÝ ---
def load_history():
    if not os.path.exists(HISTORY_FILE): return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]

def save_history(link):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(link + "\n")

sent_links = load_history()

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

# THÊM BIẾN is_first_run ĐỂ KIỂM SOÁT ĐỌC THẦM
def check_news(is_first_run=False):
    if not is_first_run:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Đang quét CafeF, VNEco, VTC, Gov, VOV, MekongASEAN... (10s/lần)")
    headers = {'User-Agent': 'Mozilla/5.0'}

    for url in URLS_TO_SCAN:
        try:
            domain = ""
            source_name = ""
            if "cafef.vn" in url: 
                domain = "https://cafef.vn"
                source_name = "CafeF"
            elif "vneconomy.vn" in url: 
                domain = "https://vneconomy.vn"
                source_name = "VnEconomy"
            elif "nguoiquansat.vn" in url: 
                domain = "https://nguoiquansat.vn"
                source_name = "Người Quan Sát"
            elif "vtcnews.vn" in url:
                domain = "https://vtcnews.vn"
                source_name = "VTC News"
            elif "baochinhphu.vn" in url:
                domain = "https://baochinhphu.vn"
                source_name = "Báo Chính Phủ"
            elif "vov.vn" in url:
                domain = "https://vov.vn"
                source_name = "VOV"
            elif "f319.com" in url:
                domain = "https://f319.com"
                source_name = "F319"
            elif "mekongasean.vn" in url:
                domain = "https://mekongasean.vn"
                source_name = "Mekong ASEAN"

            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            news_items = []
            if source_name == "F319":
                news_items = soup.find_all('h3', class_='title')
            elif source_name == "CafeF":
                news_items = soup.find_all('h3')
            elif source_name == "VnEconomy":
                news_items = soup.find_all('h3', class_='story__title')
            elif source_name == "VTC News":
                news_items = soup.find_all('h3') 
            else:
                news_items = soup.find_all(['h2', 'h3'])

            for item in news_items:
                link_tag = item.find('a')
                if not link_tag: continue

                title = link_tag.get_text().strip()
                link = link_tag['href']

                if not link.startswith("http"):
                    if not link.startswith("/") and not domain.endswith("/"):
                        link = domain + "/" + link
                    else:
                        link = domain + link

                if link in sent_links: continue

                title_upper = title.upper()
                is_match = False
                prefix = ""

                for ticker in VIP_TICKERS:
                    if ticker in title_upper:
                        is_match = True
                        prefix = f"🔥 CP VIP {ticker}: "
                        break

                if not is_match:
                    for sector in SECTOR_KEYWORDS:
                        if sector in title_upper:
                            for hot in HOT_KEYWORDS:
                                if hot in title_upper:
                                    is_match = True
                                    prefix = f"📢 TIN HOT {sector}: "
                                    break
                        if is_match: break

                if is_match:
                    if is_first_run:
                        # NẾU LÀ VÒNG ĐẦU TIÊN: Chỉ ghi vào sổ, không báo lên Telegram
                        print(f"--> [ĐỌC THẦM BỎ QUA SPAM] ({source_name}): {title}")
                        sent_links.append(link)
                        save_history(link)
                    else:
                        # TỪ VÒNG THỨ 2 TRỞ ĐI: Bắn tin ầm ầm
                        print(f"--> Tin mới ({source_name}): {title}")
                        summary = get_sapo(link, source_name)
                        warning_icon = "⚠️" if source_name == "F319" else "📰"
                        msg = f"{warning_icon} NGUỒN: {source_name}\n{prefix}\n{title.upper()}\n\n{summary}\n\n👉 Link gốc: {link}"
                        
                        send_telegram(msg)
                        sent_links.append(link)
                        save_history(link)

        except Exception as e:
            pass

print("--- TOOL SIÊU GIÁN ĐIỆP ĐÃ KHỞI ĐỘNG ---")

# THÊM CỜ ĐÁNH DẤU LẦN CHẠY ĐẦU TIÊN
is_first_run = True 

while True:
    try:
        check_news(is_first_run)
        
        if is_first_run:
            print("--- ĐÃ ĐỌC THẦM XONG TIN CŨ, BẮT ĐẦU CANH TIN MỚI ---")
            is_first_run = False # Hủy cờ đọc thầm, từ giờ sẽ hú còi
            
        time.sleep(10) 
    except KeyboardInterrupt:
        break
