import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="F306 Hazzard 助手", layout="centered")

st.markdown("""
    <style>
    .product-box { border: 1px solid #eee; border-radius: 12px; padding: 15px; margin-bottom: 20px; text-align: center; background: white; color: black; }
    .price-text { color: #d32f2f; font-weight: bold; font-size: 1.3rem; margin: 10px 0; }
    img { border-radius: 8px; width: 100%; height: auto; background: #f0f0f0; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎒 F306 HAZZARD 實時掃描")

def fetch_data():
    # 使用 F306 專屬網址
    url = "https://www.freitag.ch/en/f306"
    
    # 模擬非常真實的 iPhone 瀏覽器 Header
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
        "DNT": "1"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200:
            st.error(f"網站拒絕連線 (錯誤碼: {response.status_code})")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        products = []
        
        # 1. 嘗試尋找產品列表容器
        items = soup.find_all(['li', 'div'], class_=re.compile("product-item|product_item"))
        
        if not items:
            # 備用方案：如果 class 沒對上，直接抓所有包含連結和圖片的方塊
            items = soup.select('li[class*="item"]')

        for item in items:
            try:
                # 抓取圖片：嘗試所有可能的屬性 (src, data-src, data-original)
                img_tag = item.find('img')
                if not img_tag: continue
                
                img_url = (img_tag.get('data-src') or 
                           img_tag.get('data-original') or 
                           img_tag.get('src'))
                
                # 如果圖片是相對路徑，補全它
                if img_url and img_url.startswith('/'):
                    img_url = "https://www.freitag.ch" + img_url

                # 抓取連結
                link_tag = item.find('a', href=True)
                link = link_tag['href']
                if not link.startswith('http'):
                    link = "https://www.freitag.ch" + link
                
                # 抓取價格
                price_tag = item.find(class_=re.compile("price|amount"))
                price = price_tag.get_text().strip() if price_tag else "Check on site"
                
                # 排除一些沒意義的佔位圖
                if img_url and "base64" not in img_url:
                    products.append({"img": img_url, "price": price, "link": link})
            except:
                continue
                
        return products
    except Exception as e:
