import streamlit as st
import requests
from bs4 import BeautifulSoup

# 設定頁面
st.set_page_config(page_title="F306 掃描器", layout="centered")

st.title("🎒 F306 HAZZARD 掃描器")
st.write("連線狀態檢查...")

def fetch_data():
    # 嘗試最直接的網址
    url = "https://www.freitag.ch/en/f306"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return f"網站回傳錯誤代碼: {response.status_code}"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        products = []
        
        # 使用最寬鬆的抓取條件
        items = soup.select('.product-item')
        for item in items:
            img_tag = item.find('img')
            if img_tag:
                img = img_tag.get('data-src') or img_tag.get('src')
                if img and img.startswith('/'):
                    img = "https://www.freitag.ch" + img
                
                link_tag = item.find('a', href=True)
                link = "https://www.freitag.ch" + link_tag['href'] if link_tag else url
                
                price_tag = item.select_one('.price')
                price = price_tag.get_text().strip() if price_tag else "查看售價"
                
                if img and "placeholder" not in img:
                    products.append({"img": img, "price": price, "link": link})
        
        return products
    except Exception as e:
        return f"發生意外錯誤: {str(e)}"

# 按鈕觸發
if st.button('🚀 開始掃描最新現貨'):
    result = fetch_data()
    
    if isinstance(result, str):
        st.error(result)
    elif len(result) == 0:
        st.warning("成功連線官網，但目前頁面上沒有顯示任何 F306 產品。")
    else:
        st.success(f"找到 {len(result)} 款現貨！")
        for p in result:
            with st.container():
                st.image(p['img'], use_container_width=True)
                st.write(f"**價格: {p['price']}**")
                st.link_button("👉 前往官網", p['link'])
                st.write("---")
