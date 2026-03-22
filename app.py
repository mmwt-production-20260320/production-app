import streamlit as st
import pandas as pd
from datetime import datetime

# --- ページ設定 ---
st.set_page_config(page_title="生産管理システム", layout="centered")

# --- スタイル定義 (CSS) ---
st.markdown("""
    <style>
    /* 全体のフォントサイズ調整 */
    html, body, [data-testid="stWidgetLabel"] p {
        font-size: 16px !important; /* 他のテキストの文字サイズを統一 */
    }
    
    /* タイトルの文字サイズ (以前より1ptアップを想定) */
    .main-title {
        font-size: 26px !important; 
        font-weight: bold;
        text-align: center;
        margin-bottom: 30px;
    }

    /* テキストボックスの上位置を強制的に合わせる */
    [data-testid="stHorizontalBlock"] {
        align-items: flex-start !important;
    }

    /* 入力欄の高さと余白を統一 (5項目合計などのサイズ合わせ) */
    .stNumberInput input, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        min-height: 45px !important;
    }

    /* ボタンのスタイル */
    .stButton button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- タイトル表示 ---
st.markdown('<p class="main-title">生産管理入力</p>', unsafe_allow_html=True)

# --- データの初期化関数 ---
def reset_data():
    st.session_state.立体 = 0
    st.session_state.ズボン = 0
    st.session_state.プレス = 0
    st.session_state.平面 = 0
    st.session_state.Yシャツ = 0
    st.session_state.総労働時間 = 0.0
    st.session_state.confirm = False

if 'confirm' not in st.session_state:
    st.session_state.confirm = False

# --- 入力フォームレイアウト ---
# 1段目：日付と曜日
col1, col2 = st.columns(2)
with col1:
    input_date = st.date_input("入力日", datetime.now())
with col2:
    # 曜日の位置を日付に合わせる
    weekday_map = ["月", "火", "水", "木", "金", "土", "日"]
    current_weekday = weekday_map[input_date.weekday()]
    st.text_input("曜日", value=current_weekday, disabled=True)

# 2段目：エリアと工場名
col3, col4 = st.columns(2)
with col3:
    area = st.selectbox("エリア", ["盛岡", "その他"])
with col4:
    factory = st.selectbox("工場名", ["滝沢", "その他"])

st.markdown("---")

# 3段目：生産項目（上段）
col5, col6, col7 = st.columns(3)
with col5:
    ritai = st.number_input("立体", min_value=0, key="立体")
with col6:
    zubon = st.number_input("ズボン", min_value=0, key="ズボン")
with col7:
    press = st.number_input("プレス", min_value=0, key="プレス")

# 4段目：生産項目（下段）と合計
col8, col9, col10 = st.columns(3)
with col8:
    heimen = st.number_input("平面", min_value=0, key="平面")
with col9:
    yshirt = st.number_input("Yシャツ", min_value=0, key="Yシャツ")
with col10:
    total_items = ritai + zubon + press + heimen + yshirt
    st.number_input("5項目合計", value=total_items, disabled=True)

# 5段目：労働時間と人時生産点数
col11, col12 = st.columns(2)
with col11:
    work_hours = st.selectbox("総労働時間 (h)", [float(i/10) for i in range(0, 241, 5)], key="総労働時間")
with col12:
    productivity = round(total_items / work_hours, 2) if work_hours > 0 else 0
    st.number_input("人時生産点数", value=productivity, disabled=True)

st.markdown("---")

# --- 保存ロジック ---
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("保存する"):
        st.session_state.confirm = True

with col_btn2:
    if st.button("キャンセル"):
        reset_data()
        st.rerun()

# --- 確認ダイアログ ---
if st.session_state.confirm:
    st.warning("保存してよろしいですか？")
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        if st.button("はい (保存)"):
            # ここにスプレッドシート追加の処理を記述
            # (例: gspread等を使用した書き込み処理)
            st.success("スプレッドシートに保存しました！")
            st.session_state.confirm = False
            # 保存後にリセットする場合
            # reset_data()
            # st.rerun()
    with c_col2:
        if st.button("いいえ (戻る)"):
            reset_data()
            st.rerun()
