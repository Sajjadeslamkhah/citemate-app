import streamlit as st

st.set_page_config(layout="wide", page_title="Citemate Alpha")

st.title("🔗 Citemate")
st.caption("Akademik Yazım ve Atıf Senkronizasyonu")

col1, col2 = st.columns([7, 3])

with col1:
    st.subheader("📝 Editör")
    st.text_area("Makalenizi yazmaya başlayın...", height=600)

with col2:
    st.subheader("📚 Kaynaklar")
    url = st.text_input("PubMed veya Scholar Linki")
    if st.button("Kaynağı Ekle"):
        if url:
            st.success("Kaynak eklendi!")
        else:
            st.warning("Link giriniz.")
