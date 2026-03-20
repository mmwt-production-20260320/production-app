import streamlit as st
import gspread
from datetime import datetime

# --- ページ設定 ---
st.set_page_config(page_title="生産管理システム", layout="centered", page_icon="🏭")

# --- Googleスプレッドシート接続関数 ---
def get_sheet():
    client = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    return client.open_by_key('1o6F0r3bo7cEtWM0PoaFcAyulY21_xIE_ItEq0EphmGI').get_worksheet(0)

# --- メイン画面 ---
st.title("🏭 生産管理入力フォーム")

# --- 入力エリア ---
# 工場情報
c1, c2 = st.columns(2)
with c1:
    factory = st.selectbox("工場名", ["滝沢", "都南", "南", "矢巾"])
with c2:
    staff = st.text_input("担当者", value="担当者名")

st.divider()

# 生産数入力（5項目）
st.subheader("📦 生産数入力")
col1, col2, col3 = st.columns(3)
with col1:
    ritai = st.number_input("立体", min_value=0, step=1, value=0)
    heimen = st.number_input("平面", min_value=0, step=1, value=0)
with col2:
    zubon = st.number_input("ズボン", min_value=0, step=1, value=0)
    yshirt = st.number_input("Yシャツ", min_value=0, step=1, value=0)
with col3:
    press = st.number_input("プレス", min_value=0, step=1, value=0)

st.divider()

# 労働時間
total_work_h = st.number_input("⏰ 総労働時間 (h)", min_value=0.0, step=0.1, value=0.0)

# --- 計算（自動計算してスプレッドシートに送る） ---
total_qty = ritai + heimen + zubon + yshirt + press # 当日合計
productivity = round(total_qty / total_work_h, 1) if total_work_h > 0 else 0 # 人時生産点数

# --- 保存処理 ---
if st.button("スプレッドシートに保存する 💾", use_container_width=True):
    try:
        with st.spinner("書き込み中..."):
            sheet = get_sheet()
            
            # 日付と曜日
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            # 日本語の曜日
            weekday_list = ["月", "火", "水", "木", "金", "土", "日"]
            day_of_week = weekday_list[now.weekday()]
            
            # スプレッドシートの列 AからL に対応するリスト
            # [日付, 曜日, 工場名, 担当者, 立体, 平面, ズボン, Yシャツ, プレス, 当日合計, 総労働時間, 人時生産点数]
            new_row = [
                date_str, day_of_week, factory, staff, 
                ritai, heimen, zubon, yshirt, press, 
                total_qty, total_work_h, productivity
            ]
            
            sheet.append_row(new_row)
            
            st.success(f"✅ 保存完了！ 合計: {total_qty} 点 / 生産性: {productivity}")
            st.balloons()
            
    except Exception as e:
        st.error(f"❌ エラー: {e}")

# 履歴表示
if st.button("📊 最新の履歴を表示"):
    try:
        data = get_sheet().get_all_values()
        st.table(data[-5:])
    except:
        st.error("履歴の読み込みに失敗しました。")
