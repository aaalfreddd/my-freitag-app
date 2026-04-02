import streamlit as st
import requests
from bs4 import BeautifulSoup

# 基本頁面設定
st.set_page_config(page_title="F306 掃描器", layout="centered")

st.title("🎒 F306 HAZZARD 掃描器")
st.caption("連線狀態：準備就緒")

def fetch_data():
    url = "https://www.freitag.ch/en/f306"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return f"網站連線失敗，代碼: {response.status_code}"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        products = []
        
        # 尋找產品項目
        items = soup.select('.product-item')
        for item in items:
            try:
                img_tag = item.find('img')
                if not img_tag:
                    continue
                    
                img = img_tag.get('data-src') or img_tag.get('src')
                if img and img.startswith('/'):
                    img = "https://www.freitag.ch" + img
                
                link_tag = item.find('a', href=True)
                link = "https://www.freitag.ch" + link_tag['href'] if link_tag else url
                
                price_tag = item.select_one('.price')
                price = price_tag.get_text().strip() if price_tag else "查看售價"
                
                if img and "placeholder" not in img:
                    products.append({"img": img, "price": price, "link": link})
            except:
                continue # 忽略個別項目的解析錯誤
        
        return products
    except Exception as e:
        return f"連線錯誤: {str(e)}"

# 顯示介面
if st.button('🚀 執行掃描'):
    with st.spinner('掃描中...'):
        result = fetch_data()
        
        if isinstance(result, str):
            st.error(result)
        elif not result:
            st.warning("目前官網沒有顯示 F306 產品，或防爬蟲阻擋。")
        else:
            st.success(f"發現 {len(result)} 款產品！")
            for p in result:
                st.image(p['img'], use_container_width=True)
                st.write(f"**價格: {p['price']}**")
                st.link_button("👉 前往官網", p['link'])
                st.markdown("---")
