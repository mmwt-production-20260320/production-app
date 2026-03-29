import streamlit as st
import gspread
from datetime import datetime
import time

# --- 1. ページ設定 ---
st.set_page_config(page_title="生産管理入力", layout="centered", page_icon="🏭")

# --- 2. デザイン読み込み ---
try:
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

# --- 3. セッション初期化（リセット用） ---
# 保存後に箱の名前を変えて強制リセットするためのID
if "form_id" not in st.session_state:
    st.session_state.form_id = 0
if "confirm" not in st.session_state:
    st.session_state.confirm = False

# --- 4. スプレッドシート保存関数 ---
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

# --- 5. メイン画面の構成 ---
st.title("生産管理入力")

# 日付と曜日
col_d1, col_d2 = st.columns(2)
with col_d1:
    input_date = st.date_input("入力日", datetime.now(), key=f"date_{st.session_state.form_id}")
with col_d2:
    weekday = ["月","火","水","木","金","土","日"][input_date.weekday()]
    st.markdown('<p class="label-text">曜日</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="result-box">{weekday}</div>', unsafe_allow_html=True)

# エリア・工場
area_options = {"盛岡": ["滝沢", "都南", "南", "矢巾"], "花巻": ["桜木", "藤沢", "北上", "江釣子", "水沢", "一関"]}
col_a1, col_a2 = st.columns(2)
with col_a1:
    sel_area = st.selectbox("エリア", list(area_options.keys()), key=f"area_{st.session_state.form_id}")
with col_a2:
    sel_factory = st.selectbox("工場名", area_options[sel_area], key=f"factory_{st.session_state.form_id}")

st.divider()

# 生産数入力
c1, c2, c3 = st.columns(3)
with c1:
    val_ritai = st.number_input("立体", min_value=0, key=f"ritai_{st.session_state.form_id}")
    val_heimen = st.number_input("平面", min_value=0, key=f"heimen_{st.session_state.form_id}")
with c2:
    val_zubon = st.number_input("ズボン", min_value=0, key=f"zubon_{st.session_state.form_id}")
    val_yshirt = st.number_input("Yシャツ", min_value=0, key=f"yshirt_{st.session_state.form_id}")
with c3:
    val_press = st.number_input("プレス", min_value=0, key=f"press_{st.session_state.form_id}")
    total_val = val_ritai + val_heimen + val_zubon + val_yshirt + val_press
    st.markdown('<p class="label-text">5項目合計</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="result-box">{total_val}</div>', unsafe_allow_html=True)

st.divider()

# 労働時間と生産点数
col_l, col_r = st.columns(2)
with col_l:
    val_work_h = st.number_input("総労働時間 (h)", min_value=0.0, step=0.25, format="%.2f", key=f"work_{st.session_state.form_id}")
with col_r:
    val_prod = round(total_val / val_work_h, 2) if val_work_h > 0 else 0.00
    st.markdown('<p class="label-text">人時生産点数</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="result-box">{val_prod:.2f}</div>', unsafe_allow_html=True)

st.divider()

# --- 6. 保存ロジック ---
if not st.session_state.confirm:
    if st.button("保存する", use_container_width=True):
        if total_val > 0:
            st.session_state.confirm = True
            st.rerun()
        else:
            st.error("数値を入力してください")
else:
    st.warning("⚠️ この内容で保存しますか？")
    conf1, conf2 = st.columns(2)
    with conf1:
        if st.button("はい（確定）", use_container_width=True):
            new_row = [str(input_date), weekday, sel_area, sel_factory, 
                       val_ritai, val_heimen, val_zubon, val_yshirt, 
                       val_press, total_val, val_work_h, val_prod]
            if save_to_sheets(new_row):
                st.success("✅ 保存完了！")
                st.balloons()
                # フォームIDを更新して全入力欄を強制リセット（0に戻す）
                st.session_state.form_id += 1
                st.session_state.confirm = False
                time.sleep(1.5)
                st.rerun()
    with conf2:
        if st.button("いいえ（戻る）", use_container_width=True):
            st.session_state.confirm = False
            st.rerun()
