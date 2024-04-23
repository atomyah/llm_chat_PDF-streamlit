# japanese_pages.py 参考：https://discuss.streamlit.io/t/is-it-possible-to-set-different-names-for-multipage-in-the-sidebar-and-url/38908/2

import streamlit as st


def titles():
    return st.markdown(
        """
    <style>
:root {
  --text-color: #808495; /* Light text color */
  --bg-color: transparent; /* Dark background color */
}
a[href="http://localhost:8501/"] span:first-child {
    z-index: 1;
    color: transparent;
}
a[href="http://localhost:8501/"] span:first-child::before {
    content: "🏠ホーム";
    left: 0;
    z-index: 2;
    color: var(--text-color);
    background-color: var(--bg-color);
}
a[href="http://localhost:8501/admin"] span:first-child {
    z-index: 1;
    color: transparent;
}
a[href="http://localhost:8501/admin"] span:first-child::before {
    content: "💻管理画面";
    left: 0;
    z-index: 2;
    color: var(--text-color);
    background-color: var(--bg-color);
}
a[href="http://localhost:8501/chat"] span:first-child {
    z-index: 1;
    color: transparent;
}
a[href="http://localhost:8501/chat"] span:first-child::before {
    content: "💬チャット";
    left: 0;
    z-index: 2;
    color: var(--text-color);
    background-color: var(--bg-color);
}
</style>
    """,
        unsafe_allow_html=True,
    )
