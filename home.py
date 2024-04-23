# homy.py
import streamlit as st
import hmac  # ログイン機能に必要
from japanese_pages import titles


# ページ表示用関数
def main():

    # タイトル
    st.set_page_config(page_title="ホーム", page_icon="🏠")
    st.markdown(
        "<h1 class='jp-san-serif'>PDF文書-質問回答AIチャットWeb ホーム</h1>",
        unsafe_allow_html=True,
    )
    titles()

    st.write(
        '<span style="color:blue;">アップロードしたPDF文書の内容にもとづいてChatGPTが回答します！...:sunglasses:</span>',
        unsafe_allow_html=True,
    )

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
            font-size: 1.7rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    ##################################### タイトルのCSSを良しなに設定～ここまで ############################################

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


if __name__ == "__main__":
    main()
