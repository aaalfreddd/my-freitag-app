import streamlit as st
import requests
from bs4 import BeautifulSoup

# 設定手機顯示比例
st.set_page_config(page_title="F306 Hazzard 助手", layout="centered")

# 手機版美化界面
st.markdown("""
    <style>
    .product-box {
        border: 1px solid #eee;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .price-text {
        color: #d32f2f;
        font-weight: bold;
        font-size: 1.2rem;
    }
    img {
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎒 F306 HAZZARD 清單")
st.caption("直接獲取 Freitag 官網現貨圖片及價錢")

def fetch_data():
    url = "https://www.freitag.ch/en/f306"
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1"}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        products = []
        
        # 抓取產品方塊 (根據 Freitag 最新 HTML 結構)
        items = soup.select('.product-item') 
        for item in items:
            try:
                img = item.select_one('img')['data-src'] if item.select_one('img').has_attr('data-src') else item.select_one('img')['src']
                price = item.select_one('.price').text.strip()
                link = "https://www.freitag.ch" + item.select_one('a')['href']
                products.append({"img": img, "price": price, "link": link})
            except:
                continue
        return products
    except Exception as e:
        st.error(f"連線失敗: {e}")
        return []

if st.button('🔄 點擊刷新最新庫存'):
    data = fetch_data()
    if data:
        for p in data:
            with st.container():
                # 使用 HTML 讓手機排版更好看
                st.markdown(f"""
                <div class="product-box">
                    <img src="{p['img']}" style="width:100%">
                    <p class="price-text">{p['price']}</p>
                </div>
                """, unsafe_allow_html=True)
                st.link_button("👉 進入官網查看詳情", p['link'])
    else:
        st.write("目前沒有抓取到資料，請稍後再試。")
