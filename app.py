import streamlit as st
import gspread
from datetime import datetime
import time
import pandas as pd

# --- 1. ページ設定 ---
st.set_page_config(page_title="生産管理入力", layout="centered", page_icon="🏭")

# --- 2. デザイン読み込み ---
try:
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

# --- 3. セッション初期化 ---
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

# --- 5. メイン画面 ---
# タイトルに工場の絵文字を追加します
st.title("🏭 生産管理入力")

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

# --- 生産数入力（スマホの「index表示」を完全に封じ込める版） ---
col_p1, col_p2 = st.columns(2)

with col_p1:
    st.markdown('<p class="label-text">立体</p>', unsafe_allow_html=True)
    val_ritai = st.number_input("立体", min_value=0, step=1, label_visibility="collapsed", key=f"ritai_{st.session_state.form_id}")
    
    st.markdown('<p class="label-text">平面</p>', unsafe_allow_html=True)
    val_heimen = st.number_input("平面", min_value=0, step=1, label_visibility="collapsed", key=f"heimen_{st.session_state.form_id}")
    
    st.markdown('<p class="label-text">ズボン</p>', unsafe_allow_html=True)
    val_zubon = st.number_input("ズボン", min_value=0, step=1, label_visibility="collapsed", key=f"zubon_{st.session_state.form_id}")

with col_p2:
    st.markdown('<p class="label-text">Yシャツ</p>', unsafe_allow_html=True)
    val_yshirt = st.number_input("Yシャツ", min_value=0, step=1, label_visibility="collapsed", key=f"yshirt_{st.session_state.form_id}")
    
    st.markdown('<p class="label-text">プレス</p>', unsafe_allow_html=True)
    val_press = st.number_input("プレス", min_value=0, step=1, label_visibility="collapsed", key=f"press_{st.session_state.form_id}")
    
    total_val = val_ritai + val_heimen + val_zubon + val_yshirt + val_press
    st.markdown('<p class="label-text">5項目合計</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="result-box">{total_val}</div>', unsafe_allow_html=True)
    
st.divider()

# 労働時間
col_l, col_r = st.columns(2)
with col_l:
    val_work_h = st.number_input("総労働時間 (h)", min_value=0.0, step=0.25, format="%.2f", key=f"work_{st.session_state.form_id}")
with col_r:
    val_prod = round(total_val / val_work_h, 2) if val_work_h > 0 else 0.00
    st.markdown('<p class="label-text">人時生産点数</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="result-box">{val_prod:.2f}</div>', unsafe_allow_html=True)

st.divider()

# 保存ボタン
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
            new_row = [str(input_date), weekday, sel_area, sel_factory, val_ritai, val_heimen, val_zubon, val_yshirt, val_press, total_val, val_work_h, val_prod]
            if save_to_sheets(new_row):
                st.success("✅ 保存完了！")
                st.session_state.form_id += 1
                st.session_state.confirm = False
                time.sleep(1.2)
                st.rerun()
    with conf2:
        if st.button("いいえ（戻る）", use_container_width=True):
            st.session_state.confirm = False
            st.rerun()

# --- 7. 分析・グラフ表示 (エラー対策強化版) ---
st.divider()
st.header("📊 工場別・月別累計分析")

try:
    # データの読み込み
    creds_dict = st.secrets["gcp_service_account"]
    client = gspread.service_account_from_dict(creds_dict)
    sheet = client.open_by_key('1o6F0r3bo7cEtWM0PoaFcAyulY21_xIE_ItEq0EphmGI').sheet1
    
    # 全データを取得
    data = sheet.get_all_records()
    
    if data:
        df = pd.DataFrame(data)

        # 【重要】日付変換のエラー対策
        # errors='coerce' をつけることで、変な形式があっても止まらずに処理します
        df["入力日"] = pd.to_datetime(df["入力日"], errors='coerce')
        
        # 日付として読み込めなかった行（NaT）を削除
        df = df.dropna(subset=["入力日"])
        
        # 年月列の作成
        df["年月"] = df["入力日"].dt.strftime('%Y-%m')

        # 工場と月の選択
        target_factories = df["工場名"].unique()
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            sel_graph_factory = st.selectbox("工場を選択", target_factories, key="sel_f")
        
        with col_g2:
            # 選択された工場のデータから月を抽出
            factory_df = df[df["工場名"] == sel_graph_factory]
            target_months = sorted(factory_df["年月"].unique(), reverse=True)
            sel_month = st.selectbox("月を選択", target_months, key="sel_m")

        # データの絞り込みと集計
        df_filtered = factory_df[factory_df["年月"] == sel_month].copy()
        categories = ["立体", "平面", "ズボン", "Yシャツ", "プレス"]
        
        # 数値型に強制変換（文字列として入っている場合の対策）
        for cat in categories:
            df_filtered[cat] = pd.to_numeric(df_filtered[cat], errors='coerce').fillna(0)
            
        df_sum = df_filtered[categories].sum()

        # グラフ表示
        if not df_sum.empty and df_sum.sum() > 0:
            st.subheader(f"{sel_graph_factory}工場：{sel_month} の累計")
            st.bar_chart(df_sum)
            st.info(f"💡 {sel_month} の総生産点数： {int(df_sum.sum())} 点")
        else:
            st.warning("選択された条件のデータがありません。")
            
    else:
        st.info("スプレッドシートにデータがありません。")

except Exception as e:
    # どこで止まっているかデバッグ情報を表示
    st.error(f"グラフ表示でエラーが発生しました。詳細: {e}")


