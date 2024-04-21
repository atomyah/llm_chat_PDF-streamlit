## 各モジュールバージョンリスト admin.py
# streamlit@1.25.0
# openai@0.27.8
# langchain@0.0.266
# llama-index@0.8.5
# pypdf@3.15.2
# nltk@3.8.1
# pydantic@1.10.12
import tempfile
import streamlit as st
from pathlib import Path
from llama_index import VectorStoreIndex, ServiceContext
from langchain.chat_models import ChatOpenAI
from llama_index.readers.file.docs_reader import PDFReader

index = st.session_state.get("index")


prev_uploaded_file = st.session_state.get("prev_uploaded_file", None)


# indexをst.session_stateから削除する．
def on_Change_file():
    if "index" in st.session_state:
        st.session_state.pop("index")
    if "prev_uploaded_file" in st.session_state:
        st.session_state.pop("prev_uploaded_file")


upload_file = st.file_uploader(
    label="Q&A対象ファイル",
    type="pdf",
    on_change=on_Change_file,  # ファイルがアップロードされたら（ベクトル化するPDFを新しくアップしたら）on_Change_file()でindexを削除する．
)


# PDFのアップロードとベクトル化
if upload_file and index is None:
    with st.spinner(text="準備中..."):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(upload_file.getbuffer())
            prev_uploaded_file = upload_file.name  # アップロードされたファイル名を保存

            documents = PDFReader().load_data(
                file=Path(f.name)
            )  # llama_indexのFileReader(PDFReader)からPDFファイルのテキストを読み込み複数のドキュメントに分割しdocumentsに格納．

            llm = ChatOpenAI(
                model_name="gpt-3.5-turbo", temperature=0
            )  # llama_indexはLanngChainに依存しておりlangchainのChatOpenAIクラスを使ってgpt-3.5-turboを使う準備をする．
            service_context = ServiceContext.from_defaults(
                llm=llm
            )  # ServiceContextはLangChainのllama-indexライブラリで使用されるクラス．from_defaultsメソッドでServiceContextオブジェクトを作成、llm=llmは前に設定したllmオブジェクトをServiceContextに渡している
            # 要はOpenAIのGPT-3.5-turbo言語モデルをLangChain経由で使用する準備をしている．ServiceContextオブジェクトはllama-indexライブラリで使用される様々な機能で必要となる

            index = VectorStoreIndex.from_documents(  # documents(PDFを複数のドキュメントに分割したもの)からベクトル化しindexに格納．
                documents=documents, service_context=service_context
            )

            st.session_state["index"] = index
            st.session_state["prev_uploaded_file"] = (
                prev_uploaded_file  # アップロードされたファイル名をセッションに保存
            )

            # indexの永続化
            index.storage_context.persist("index.json")
            st.success("PDFのベクトル化が完了しました。")

# 前回アップロードされたファイル名を表示
if prev_uploaded_file:
    st.write(f"前回アップロードされたファイル: {prev_uploaded_file}")
