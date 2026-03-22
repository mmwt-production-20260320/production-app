import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
# --- 0. 設定情報 (GitHubのSecretsに登録した名前と合わせる) ---
SPREADSHEET_KEY = '1o6F0r3bo7cEtWM0PoaFcAyulY21_xIE_ItEq0EphmGI'

def save_to_sheets(data_list):
    """Secretsを使ってスプレッドシートに保存する"""
    try:
        # スプレッドシートのID（URLのd/〜/editの間にある文字）
        SPREADSHEET_KEY = '1o6F0r3bo7cEtWM0PoaFcAyulY21_xIE_ItEq0EphmGI'
        
        # Secretsに登録した [gcp_service_account] を読み込む
        creds_dict = st.secrets["gcp_service_account"]
        client = gspread.service_account_from_dict(creds_dict)
        
        # シートを開いて末尾に追加
        sheet = client.open_by_key(SPREADSHEET_KEY).sheet1
        sheet.append_row(data_list)
        return True
    except Exception as e:
        st.error(f"保存エラーが発生しました: {e}")
        return False
        
# --- 2. ページ設定とCSS ---
st.set_page_config(page_title="生産管理システム", layout="centered")

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

# --- 3. セッション状態の初期化 ---
if 'confirm' not in st.session_state:
    st.session_state.confirm = False

def reset_all_fields():
    # 書き換えたい項目のリスト
    keys = ["立体", "ズボン", "プレス", "平面", "Yシャツ", "総労働時間"]
    for key in keys:
        # その項目が今、画面上に存在するか確認してからリセットする（これが大事！）
        if key in st.session_state:
            if key == "総労働時間":
                st.session_state[key] = 0.0
            else:
                st.session_state[key] = 0
    # 確認フラグもオフにする
    st.session_state.confirm = False

# --- 4. 画面構成 ---
st.markdown('<p class="main-title">生産管理入力</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    input_date = st.date_input("入力日", datetime.now())
with col2:
    weekday_map = ["月", "火", "水", "木", "金", "土", "日"]
    current_weekday = weekday_map[input_date.weekday()]
    st.text_input("曜日", value=current_weekday, disabled=True)

col3, col4 = st.columns(2)
with col3:
    area = st.selectbox("エリア", ["盛岡", "滝沢", "北上"], key="area_select")
with col4:
    factory = st.selectbox("工場名", ["滝沢", "盛岡中央", "青山"], key="factory_select")

st.markdown("---")

col5, col6, col7 = st.columns(3)
with col5:
    ritai = st.number_input("立体", min_value=0, key="立体")
with col6:
    zubon = st.number_input("ズボン", min_value=0, key="ズボン")
with col7:
    press = st.number_input("プレス", min_value=0, key="プレス")

col8, col9, col10 = st.columns(3)
with col8:
    heimen = st.number_input("平面", min_value=0, key="平面")
with col9:
    yshirt = st.number_input("Yシャツ", min_value=0, key="Yシャツ")
with col10:
    total_val = ritai + zubon + press + heimen + yshirt
    st.number_input("5項目合計", value=total_val, disabled=True)

col11, col12 = st.columns(2)
with col11:
    hour_list = [round(x * 0.1, 1) for x in range(0, 241, 5)]
    work_hours = st.selectbox("総労働時間 (h)", hour_list, key="総労働時間")
with col12:
    productivity = round(total_val / work_hours, 2) if work_hours > 0 else 0
    st.number_input("人時生産点数", value=productivity, disabled=True)

st.markdown("---")

# --- 5. 保存・キャンセルボタンの制御 ---
if not st.session_state.confirm:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("保存する"):
            if total_val == 0 or work_hours == 0:
                st.error("入力が不足しているため保存できません。")
            else:
                st.session_state.confirm = True
                st.rerun()
    with c2:
        if st.button("キャンセル"):
            reset_all_fields()
            st.rerun()

# --- 6. 確認メッセージと保存実行 ---
if st.session_state.confirm:
    st.warning("この内容で保存してよろしいですか？")
    conf_c1, conf_c2 = st.columns(2)
    with conf_c1:
        if st.button("はい（確定）"):
            # 書き込むデータの並びを作成
            new_data = [
                str(input_date), current_weekday, area, factory, 
                ritai, zubon, press, heimen, yshirt, total_val, 
                work_hours, productivity
            ]
            
            # 保存実行
            if save_to_sheets(new_data):
                st.success("スプレッドシートに正常に追加されました。")
                reset_all_fields()
                st.rerun()
            
    with conf_c2:
        if st.button("いいえ（戻る）"):
            reset_all_fields()
            st.rerun()
