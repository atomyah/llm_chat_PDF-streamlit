# homy.py
import streamlit as st
import hmac  # ログイン機能に必要


##################################### タイトルのCSSを良しなに設定 ############################################
# Google FontsからNoto Sans JPフォントをロードする
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP&display=swap" rel="stylesheet">
    """,
    unsafe_allow_html=True,
)

# Robotoフォントをタイトル文字に使用するためのHTMLスタイル
st.markdown(
    """
    <style>
    .jp-san-serif {
        font-family: 'Noto Sans JP', sans-serif;
        font-size: 28px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
##################################### タイトルのCSSを良しなに設定～ここまで ############################################
st.markdown(
    "<h1 class='jp-san-serif'>PDF文書-質問回答AIチャットWeb ホーム</h1>",
    unsafe_allow_html=True,
)


##################################### ログイン機能 ############################################
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "パスワード", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.
##################################### ログイン機能～ここまで ############################################

st.write(
    '<span style="color:blue;">ログイン中...:sunglasses:</span>', unsafe_allow_html=True
)
# サイドバーにページ選択のセレクトボックスを作成
# page = st.sidebar.selectbox(
#     "ページを選択してください", ["ホーム", "管理画面", "チャットページ"]
# )


# # メインエリアに選択結果を表示
# st.write(f"選んだフルーツ:", page)

# 認証機能の追加
# def auth():
#     # ユーザー認証の設定
#     st.authentication.authenticate()

#     # 認証されたユーザーごとにセッション状態を分ける
#     if "session_state" not in st.session_state:
#         st.session_state["session_state"] = {}

#     session_state = st.session_state["session_state"]

#     # ページの切り替え
#     pages = {
#         "PDF管理画面": admin,
#         "PDF Q&A チャット": chat,
#     }

#     st.sidebar.title("ナビゲーション")
#     selection = st.sidebar.radio("移動先を選択してください", list(pages.keys()))

#     # 選択されたページを表示
#     pages[selection]()


# if __name__ == "__main__":
#     auth()
