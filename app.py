import streamlit as st
import gspread
from datetime import datetime

# --- 1. ページ設定とデザイン (CSS) ---
st.set_page_config(page_title="生産管理入力", layout="centered", page_icon="🏭")

st.markdown("""
    <style>
    /* 全体の文字サイズと余白 */
    html, body, [data-testid="stWidgetLabel"] p { font-size: 15px !important; }
    h1 { font-size: 22px !important; text-align: center; margin-bottom: 20px; }
    
    /* 計算結果を表示する黒いボックス */
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
    
    /* 入力欄の高さを統一 */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        min-height: 42px !important;
    }
    
    /* 不要なメニュー類を隠してスッキリ */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. スプレッドシート保存関数 ---
def save_to_sheets(data_list):
    try:
        # スプレッドシートのID
        SPREADSHEET_KEY = '1o6F0r3bo7cEtWM0PoaFcAyulY21_xIE_ItEq0EphmGI'
        # Secretsから鍵を読み込む
        creds_dict = st.secrets["gcp_service_account"]
        client = gspread.service_account_from_dict(creds_dict)
        # 1枚目のシートを開く
        sheet = client.open_by_key(SPREADSHEET_KEY).sheet1
        sheet.append_row(data_list)
        return True
    except Exception as e:
        st.error(f"保存エラーが発生しました: {e}")
        return False

# --- 3. リセット関数 (画面上の項目とkeyを完全一致) ---
def reset_all_fields():
    # 入力項目の key と完全に一致させてエラーを防止
    target_keys = ["立体", "ズボン", "プレス", "平面", "Yシャツ", "work_h"]
    for k in target_keys:
        if k in st.session_state:
            # 労働時間だけ小数、他は整数
            st.session_state[k] = 0.0 if k == "work_h" else 0
    st.session_state.confirm = False

# --- 4. メイン画面の構成 ---
st.title("生産管理入力システム")

# 日付と曜日
col_d1, col_d2 = st.columns(2)
with col_d1:
    input_date = st.date_input("入力日", datetime.now(), key="input_date")
with col_d2:
    weekday_list = ["月","火","水","木","金","土","日"]
    weekday = weekday_list[input_date.weekday()]
    st.markdown("曜日")
    st.markdown(f'<div class="result-box">{weekday}</div>', unsafe_allow_html=True)

# エリア・工場名の連動
area_options = {
    "盛岡": ["滝沢", "都南", "南", "矢巾"],
    "花巻": ["桜木", "藤沢", "北上", "水沢", "一関"]
}
col_a1, col_a2 = st.columns(2)
with col_a1:
    sel_area = st.selectbox("エリア", list(area_options.keys()), key="area_select")
with col_a2:
    # 選んだエリアによって工場のリストを自動切り替え
    sel_factory = st.selectbox("工場名", area_options[sel_area], key="factory_select")

st.divider()

# 生産数の入力（3列で配置）
c1, c2, c3 = st.columns(3)
with c1:
    val_ritai = st.number_input("立体", min_value=0, key="立体")
    val_heimen = st.number_input("平面", min_value=0, key="平面")
with c2:
    val_zubon = st.number_input("ズボン", min_value=0, key="ズボン")
    val_yshirt = st.number_input("Yシャツ", min_value=0, key="Yシャツ")
with c3:
    val_press = st.number_input("プレス", min_value=0, key="プレス")
    # 合計計算
    total_val = val_ritai + val_heimen + val_zubon + val_yshirt + val_press
    st.markdown("5項目合計")
    st.markdown(f'<div class="result-box">{total_val}</div>', unsafe_allow_html=True)

st.divider()

# 労働時間と生産点数
col_l, col_r = st.columns(2)
with col_l:
    # 0.0〜10.0h まで 0.5刻みで選択
    val_work_h = st.selectbox("総労働時間 (h)", [round(x*0.5, 1) for x in range(0, 21)], key="work_h")
with col_r:
    # 生産性の計算 (0除算を防止)
    val_prod = round(total_val / val_work_h, 2) if val_work_h > 0 else 0
    st.markdown("人時生産点数")
    st.markdown(f'<div class="result-box">{val_prod}</div>', unsafe_allow_html=True)

st.divider()

# --- 5. 保存・キャンセルボタン ---
if not st.session_state.get('confirm', False):
    btn_save, btn_cancel = st.columns(2)
    with btn_save:
        # 合計または時間が0の場合は押せないようにチェック
        if st.button("保存する", use_container_width=True):
            if total_val > 0 and val_work_h > 0:
                st.session_state.confirm = True
                st.rerun()
            else:
                st.error("入力が不足しています")
    with btn_cancel:
        if st.button("キャンセル", use_container_width=True):
            reset_all_fields()
            st.rerun()

# 最終確認画面
if st.session_state.get('confirm', False):
    st.warning("この内容で保存してよろしいですか？")
    conf1, conf2 = st.columns(2)
    with conf1:
        if st.button("はい（確定）", use_container_width=True):
            # スプレッドシートへ送るデータの並び
            new_row_data = [
                str(input_date), weekday, sel_area, sel_factory,
                val_ritai, val_heimen, val_zubon, val_yshirt, val_press, 
                total_val, val_work_h, val_prod
            ]
            if save_to_sheets(new_row_data):
                st.success("✅ スプレッドシートに保存しました！")
                reset_all_fields()
                st.rerun()
    with conf2:
        if st.button("いいえ（戻る）", use_container_width=True):
            st.session_state.confirm = False
            st.rerun()
