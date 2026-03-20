import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- ページ設定 (スマホで見やすく) ---
st.set_page_config(page_title="生産管理システム", layout="centered")

# --- Googleスプレッドシート接続関数 ---
def get_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    return client.open_by_key('1o6F0r3bo7cEtWM0PoaFcAyulY21_xIE_ItEq0EphmGI').get_worksheet(0)

# --- 画面作成 ---
st.title("🏭 生産管理システム (Web版)")
st.write("スマホから今日の数値を入力してください。")

# 入力フォーム
with st.form("input_form"):
    factory = st.selectbox("🏭 工場名", ["矢巾", "南", "都南", "滝沢"])
    name = st.text_input("👤 担当者名")
    
    col1, col2 = st.columns(2)
    with col1:
        ritai = st.number_input("👕 立体", min_value=0, step=1)
        heimen = st.number_input("🧺 平面", min_value=0, step=1)
        zubon = st.number_input("👖 ズボン", min_value=0, step=1)
    with col2:
        yshirts = st.number_input("👔 Yシャツ", min_value=0, step=1)
        press = st.number_input("⚡ プレス", min_value=0, step=1)
        work_time = st.number_input("⏰ 総労働時間 (h)", min_value=0.0, step=0.1)

    # 送信ボタン
    submitted = st.form_submit_button("保存する 💾")

    if submitted:
        if not name:
            st.error("担当者名を入力してください！")
        else:
            try:
                sheet = get_sheet()
                total = ritai + heimen + zubon + yshirts + press
                efficiency = round(total / work_time, 2) if work_time > 0 else 0
                now = datetime.now()
                
                # スプレッドシートへ書き込み
                data = [
                    now.strftime('%Y-%m-%d'), "曜", factory, name,
                    ritai, heimen, zubon, yshirts, press,
                    total, work_time, efficiency
                ]
                sheet.append_row(data)
                st.success(f"保存完了！ 合計: {total} 点 / 生産性: {efficiency}")
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

# --- 過去のデータ表示 (簡易版) ---
if st.button("📊 最新の履歴を表示"):
    sheet = get_sheet()
    df = sheet.get_all_records()
    st.table(df[-5:]) # 直近5件を表示
