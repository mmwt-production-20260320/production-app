import streamlit as st
import gspread
from datetime import datetime
import time

# --- 1. ページ設定 ---
st.set_page_config(page_title="生産管理入力", layout="centered", page_icon="🏭")

# --- 2. デザイン (外部の style.css を読み込む) ---
try:
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass # style.cssがない場合のエラー回避

# --- 3. セッション状態の初期化（リセットのために重要） ---
# 画面が読み込まれたとき、入力欄の初期値をセットします
initial_values = {
    "立体": 0, "平面": 0, "ズボン": 0, "Yシャツ": 0, "プレス": 0, 
    "work_h": 0.5, "confirm": False
}
for key, value in initial_values.items():
    if key not in st.session_state:
        st.session_state[key] = value

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
    input_date = st.date_input("入力日", datetime.now(), key="input_date")
with col_d2:
    weekday = ["月","火","水","木","金","土","日"][input_date.weekday()]
    st.markdown("曜日")
    st.markdown(f'<div class="result-box">{weekday}</div>', unsafe_allow_html=True)

# エリア・工場
area_options = {"盛岡": ["滝沢", "都南", "南", "矢巾"], "花巻": ["桜木", "藤沢", "北上", "江釣子", "水沢", "一関"]}
col_a1, col_a2 = st.columns(2)
with col_a1:
    sel_area = st.selectbox("エリア", list(area_options.keys()), key="area_select")
with col_a2:
    sel_factory = st.selectbox("工場名", area_options[sel_area], key="factory_select")

st.divider()

# 生産数入力（valueを指定することでプログラムからリセット可能にします）
c1, c2, c3 = st.columns(3)
with c1:
    val_ritai = st.number_input("立体", min_value=0, key="立体", value=st.session_state["立体"])
    val_heimen = st.number_input("平面", min_value=0, key="平面", value=st.session_state["平面"])
with c2:
    val_zubon = st.number_input("ズボン", min_value=0, key="ズボン", value=st.session_state["ズボン"])
    val_yshirt = st.number_input("Yシャツ", min_value=0, key="Yシャツ", value=st.session_state["Yシャツ"])
with c3:
    val_press = st.number_input("プレス", min_value=0, key="プレス", value=st.session_state["プレス"])
    total_val = val_ritai + val_heimen + val_zubon + val_yshirt + val_press
    st.markdown("5項目合計")
    st.markdown(f'<div class="result-box">{total_val}</div>', unsafe_allow_html=True)

st.divider()

# 労働時間
col_l, col_r = st.columns(2)
with col_l:
    # 選択肢のリストを作成
    work_h_options = [round(x*0.5, 1) for x in range(1, 21)]
    # 現在のセッション状態がリストにあればその位置、なければ0番目
    default_index = work_h_options.index(st.session_state["work_h"]) if st.session_state["work_h"] in work_h_options else 0
    val_work_h = st.selectbox("総労働時間 (h)", work_h_options, index=default_index, key="work_h_select")
    # セレクトボックスの値をセッションに反映
    st.session_state["work_h"] = val_work_h

with col_r:
    val_prod = round(total_val / val_work_h, 2) if val_work_h > 0 else 0
    st.markdown("人時生産点数")
    st.markdown(f'<div class="result-box">{val_prod}</div>', unsafe_allow_html=True)

st.divider()

# --- 6. 保存・確認ボタンのロジック ---

if not st.session_state.confirm:
    # 通常の保存ボタン
    if st.button("保存する", use_container_width=True):
        if total_val > 0:
            st.session_state.confirm = True
            st.rerun()
        else:
            st.error("数値を入力してください")
else:
    # 確認画面
    st.warning("⚠️ この内容でスプレッドシートに保存しますか？")
    conf1, conf2 = st.columns(2)
    
    with conf1:
        if st.button("はい（確定）", use_container_width=True, key="save_final"):
            new_row = [str(input_date), weekday, sel_area, sel_factory, 
                       val_ritai, val_heimen, val_zubon, val_yshirt, 
                       val_press, total_val, val_work_h, val_prod]
            
            if save_to_sheets(new_row):
                # 1. 成功メッセージを表示
                st.success("✅ 保存完了！")
                st.balloons()
                
                # 2. データをリセット（セッション状態を直接書き換え）
                for key in ["立体", "平面", "ズボン", "Yシャツ", "プレス"]:
                    st.session_state[key] = 0
                st.session_state["work_h"] = 0.5
                st.session_state.confirm = False
                
                # 3. 風船を見せるために少し待ち、その後リフレッシュ
                time.sleep(2)
                st.rerun()

    with conf2:
        if st.button("いいえ（戻る）", use_container_width=True):
            st.session_state.confirm = False
            st.rerun()
