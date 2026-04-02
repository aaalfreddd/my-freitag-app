import streamlit as st
import requests
import json

# 頁面基本設置
st.set_page_config(page_title="F306 Hazzard 監視器", page_icon="🎒", layout="centered")

st.markdown("""
    <style>
    .product-card {
        border: 1px solid #eee;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 25px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    .price-tag {
        color: #e63946;
        font-size: 1.4rem;
        font-weight: bold;
        margin: 10px 0;
    }
    img {
        border-radius: 10px;
        width: 100%;
        height: auto;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎒 F306 HAZZARD 現貨掃描")
st.caption("直接連線 Freitag 數據庫，獲取最準確庫存")

def fetch_f306_stock():
    # 嘗試使用通用的 API 接口，去掉 /en/ 路徑
    api_url = "https://www.freitag.ch/api/graphql"
    
    # 這是 F306 的產品 ID 2211
    # 我們加入更多參數確保 API 認為我們是合法用戶
    query = """
    query GetProductVariants($id: String!) {
      product(id: $id) {
        variants {
          price {
            formatted
          }
          url
          images {
            url
          }
        }
      }
    }
    """
    
    variables = {"id": "2211"}
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.freitag.ch/en/f306",
        "Origin": "https://www.freitag.ch"
    }

    try:
        # 使用 json 參數傳遞 query 和 variables
        response = requests.post(
            api_url, 
            json={'query': query, 'variables': variables}, 
            headers=headers, 
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'data' in result and result['data']['product']:
                return result['data']['product']['variants']
            else:
                st.warning("API 回傳成功但找不到產品數據，可能 ID 有變。")
                return []
        else:
            st.error(f"連線失敗，代碼：{response.status_code}。可能是 API 網址已更改。")
            return []
    except Exception as e:
        st.error(f"發生異常: {e}")
        return []
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
    }

    try:
        response = requests.post(api_url, json={'query': query}, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            # 提取產品列表
            variants = data['data']['product']['variants']
            return variants
        else:
            st.error(f"API 連線失敗，代碼：{response.status_code}")
            return []
    except Exception as e:
        st.error(f"發生錯誤: {e}")
        return []

if st.button('🚀 重新掃描最新 F306 庫存'):
    with st.spinner('正在與瑞士服務器通訊...'):
        stock = fetch_f306_stock()
        
        if stock:
            st.success(f"掃描完成！目前共有 {len(stock)} 款 F306 HAZZARD")
            
            for item in stock:
                # 取得圖片連結 (通常取第一張)
                img_url = item['images'][0]['url'] if item['images'] else ""
                price = item['price']['formatted']
                buy_url = "https://www.freitag.ch" + item['url']
                
                with st.container():
                    st.markdown(f"""
                    <div class="product-card">
                        <img src="{img_url}">
                        <div class="price-tag">{price}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.link_button("👉 直接進入購買頁面", buy_url)
                    st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.warning("暫時沒有找到庫存，請稍後再試。")
