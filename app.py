import streamlit as st
import pandas as pd
from datetime import datetime

# --- ページ設定 ---
st.set_page_config(page_title="生産管理システム", layout="centered")

# --- スタイル定義 (CSS) ---
st.markdown("""
    <style>
    html, body, [data-testid="stWidgetLabel"] p, .stNumberInput input, .stTextInput input {
        font-size: 16px !important;
    }
    .main-title {
        font-size: 26px !important; 
        font-weight: bold;
        text-align: center;
        margin-bottom: 30px;
    }
    [data-testid="stHorizontalBlock"] {
        align-items: flex-start !important;
    }
    div[data-baseweb="input"], div[data-baseweb="select"] {
        min-height: 45px !important;
        height: 45px !important;
    }
    .stButton button {
        width: 100%;
        height: 50px;
        font-size: 18px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- セッション状態の初期化 ---
if 'confirm' not in st.session_state:
    st.session_state.confirm = False

def reset_all_fields():
    """安全にすべての入力値を初期化する"""
    keys = ["立体", "ズボン", "プレス", "平面", "Yシャツ", "総労働時間"]
    for key in keys:
        if key in st.session_state:
            st.session_state[key] = 0.0 if key == "総労働時間" else 0
    st.session_state.confirm = False

# --- 画面構成 ---
st.markdown('<p class="main-title">生産管理入力</p>', unsafe_allow_html=True)

# 1段目：日付と曜日
col1, col2 = st.columns(2)
with col1:
    input_date = st.date_input("入力日", datetime.now())
with col2:
    weekday_map = ["月", "火", "水", "木", "金", "土", "日"]
    current_weekday = weekday_map[input_date.weekday()]
    st.text_input("曜日", value=current_weekday, disabled=True)

# 2段目：エリアと工場名
col3, col4 = st.columns(2)
with col3:
    area = st.selectbox("エリア", ["盛岡", "滝沢", "北上"], key="area_select")
with col4:
    factory = st.selectbox("工場名", ["滝沢", "盛岡中央", "青山"], key="factory_select")

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
    total_val = ritai + zubon + press + heimen + yshirt
    st.number_input("5項目合計", value=total_val, disabled=True)

# 5段目：労働時間と人時生産点数
col11, col12 = st.columns(2)
with col11:
    hour_list = [round(x * 0.1, 1) for x in range(0, 241, 5)]
    work_hours = st.selectbox("総労働時間 (h)", hour_list, key="総労働時間")
with col12:
    productivity = round(total_val / work_hours, 2) if work_hours > 0 else 0
    st.number_input("人時生産点数", value=productivity, disabled=True)

st.markdown("---")

# --- 保存・キャンセルボタンの制御 ---
if not st.session_state.confirm:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("保存する"):
            if total_val == 0:
                st.error("生産項目が入力されていないため保存できません。")
            elif work_hours == 0:
                st.error("総労働時間が入力されていないため保存できません。")
            else:
                st.session_state.confirm = True
                st.rerun()
    with c2:
        if st.button("キャンセル"):
            reset_all_fields()
            st.rerun()

# --- 確認メッセージと実行 ---
if st.session_state.confirm:
    st.warning("この内容で保存してよろしいですか？")
    conf_c1, conf_c2 = st.columns(2)
    with conf_c1:
        if st.button("はい（確定）"):
            # TODO: ここにスプレッドシートへの保存コードを記述
            st.success("スプレッドシートに追加しました！")
            reset_all_fields()
            st.rerun()
            
    with conf_c2:
        if st.button("いいえ（戻る）"):
            reset_all_fields()
            st.rerun()
