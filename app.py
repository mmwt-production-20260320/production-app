import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- ページ設定（スマホで見やすく） ---
st.set_page_config(page_title="生産管理システム", layout="centered")

# --- Googleスプレッドシート接続関数 ---
def get_sheet():
    # Streamlit CloudのSecrets（保管庫）から認証情報を読み込む最新の書き方
    client = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    # あなたのスプレッドシートIDで開く
    return client.open_by_key('1o6F0r3bo7cEtWM0PoaFcAyulY21_xIE_ItEq0EphmGI').get_worksheet(0)

# --- メイン画面作成 ---
st.title("🏭 生産管理入力フォーム")
st.write("現場から数値を入力して保存してください。")

# 入力項目
val = st.number_input("⏰ 総労働時間 (h)", min_value=0.0, step=0.1, value=50.0)

# 保存ボタン
if st.button("保存する 💾"):
    try:
        sheet = get_sheet()
        
        # 保存するデータ（日付と数値）
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = [date_str, val]
        
        # スプレッドシートの最後に追記
        sheet.append_row(new_row)
        
        st.success(f"✅ 保存しました！ ({date_str})")
        st.balloons() # お祝いの風船
        
    except Exception as e:
        st.error(f"❌ エラーが発生しました: {e}")

# --- 履歴表示（おまけ機能） ---
if st.button("📊 最新の履歴を表示"):
    try:
        sheet = get_sheet()
        data = sheet.get_all_values()
        if len(data) > 1:
            st.table(data[-5:]) # 直近5件を表示
        else:
            st.info("データがまだありません。")
    except:
        st.error("データの読み込みに失敗しました。")
