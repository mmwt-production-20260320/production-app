import streamlit as st
import gspread
from datetime import datetime

# --- 1. ページ設定 ---
st.set_page_config(page_title="生産管理入力", layout="centered", page_icon="🏭")

# --- 2. デザイン (CSS) ★ここを強化しました ---
st.markdown("""
    <style>
    /* 右上のメニューやヘッダーを消してスッキリさせる */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 全体の文字サイズ */
    html, body, [data-testid="stWidgetLabel"] p {
        font-size: 15px !important;
    }
    
    /* タイトルのデザイン */
    h1 {
        font-size: 22px !important;
        text-align: center;
        margin-bottom: 25px !important;
        color: #ffffff;
    }

    /* 計算結果を表示する黒いボックス（枠線と余白を調整） */
    .result-box {
        background-color: #262730; 
        color: #ffffff; 
        border: 1px solid rgba(250, 250, 250, 0.2); 
        border-radius: 0.5rem; 
        height: 42px; 
        display: flex; 
        align-items: center; 
        padding: 0px 12px; 
        font-size: 16px; 
        font-weight: bold; 
        width: 100%;
        box-sizing: border-box;
    }

    /* 入力欄の縦の高さを42pxで統一 */
    .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        height: 42px !important;
        min-height: 42px !important;
    }

    /* カラム間の余白調整 */
    div[data-testid="column"] {
        padding-bottom: 10px;
    }

    /* 区切り線の余白 */
    hr {
        margin: 1.5rem 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. スプレッドシート保存関数 ---
def save_to_sheets(data_list):
    try:
        SPREADSHEET_KEY = '1o6F0r3bo7cEtWM0PoaFcAyulY21_xIE_ItEq0EphmGI'
        creds_dict = st.secrets["gcp_service_account"]
        client = gspread.service_account_from_dict(creds_dict)
        sheet = client.open_by_key(SPREADSHEET_KEY).sheet1
        sheet.append_row(data_list)
        return True
    except Exception as e:
        st.error(f"保存エラー: {e}")
        return False

# --- 4. リセット関数 ---
def reset_all_fields():
    target_keys = ["立体", "ズボン", "プレス", "平面", "Yシャツ", "work_h"]
    for k in target_keys:
        if k in st.session_state:
            st.session_state[k] = 0.0 if k == "work_h" else 0
    st.session_state.confirm = False

# --- 5. メイン画面の構成 ---
st.title("生産管理入力システム")

# 日付と曜日（今日の日付を自動セット）
col_d1, col_d2 = st.columns(2)
with col_d1:
    input_date = st.date_input("入力日", datetime.now(), key="input_date")
with col_d2:
    weekday_list = ["月","火","水","木","金","土","日"]
    weekday = weekday_list[input_date.weekday()]
    st.markdown("曜日")
    st.markdown(f'<div class="result-box">{weekday}</div>', unsafe_allow_html=True)

# エリア・工場の連動
area_options = {
    "盛岡": ["滝沢", "都南", "南", "矢巾"],
    "花巻": ["桜木", "藤沢", "北上", "水沢", "一関"]
}
col_a1, col_a2 = st.columns(2)
with col_a1:
    sel_area = st.selectbox("エリア", list(area_options.keys()), key="area_select")
with col_a2:
    sel_factory = st.selectbox("工場名", area_options[sel_area], key="factory_select")

st.divider()

# 生産数入力（3列できれいに配置）
c1, c2, c3 = st.columns(3)
with c1:
    val_ritai = st.number_input("立体", min_value=0, key="立体")
    val_heimen = st.number_input("平面", min_value=0, key="平面")
with c2:
    val_zubon = st.number_input("ズボン", min_value=0, key="ズボン")
    val_yshirt = st.number_input("Yシャツ", min_value=0, key="Yシャツ")
with c3:
    val_press = st.number_input("プレス", min_value=0, key="プレス")
    total_val = val_ritai + val_heimen + val_zubon + val_yshirt + val_press
    st.markdown("5項目合計")
    st.markdown(f'<div class="result-box">{total_val}</div>', unsafe_allow_html=True)

st.divider()

# 労働時間と生産点数
col_l, col_r = st.columns(2)
with col_l:
    val_work_h = st.selectbox("総労働時間 (h)", [round(x*0.5, 1) for x in range(0, 21)], key="work_h")
with col_r:
    val_prod = round(total_val / val_work_h, 2) if val_work_h > 0 else 0
    st.markdown("人時生産点数")
    st.markdown(f'<div class="result-box">{val_prod}</div>', unsafe_allow_html=True)

st.divider()

# --- 6. ボタンエリア ---
if not st.session_state.get('confirm', False):
    btn_save, btn_cancel = st.columns(2)
    with btn_save:
        if st.button("保存する", use_container_width=True):
            if total_val > 0 and val_work_h > 0:
                st.session_state.confirm = True
                st.rerun()
            else:
                st.error("入力を確認してください")
    with btn_cancel:
        if st.button("キャンセル", use_container_width=True):
            reset_all_fields()
            st.rerun()

# 確認ダイアログ
if st.session_state.get('confirm', False):
    st.warning("この内容で保存してよろしいですか？")
    conf1, conf2 = st.columns(2)
    with conf1:
        if st.button("はい（確定）", use_container_width=True):
            new_row = [
                str(input_date), weekday, sel_area, sel_factory,
                val_ritai, val_heimen, val_zubon, val_yshirt, val_press, 
                total_val, val_work_h, val_prod
            ]
            if save_to_sheets(new_row):
                st.success("✅ 保存に成功しました！")
                reset_all_fields()
                st.rerun()
    with conf2:
        if st.button("いいえ（戻る）", use_container_width=True):
            st.session_state.confirm = False
            st.rerun()
