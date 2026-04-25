import streamlit as st
import re
from datetime import datetime

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Citemate Pro", page_icon="📚", layout="wide")

# Safari uyumlu temel stil
st.markdown("""
    <style>
    .stTextArea textarea { font-family: 'Times New Roman', serif; font-size: 16px !important; }
    .preview-box { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #ddd; line-height: 1.6; }
    .ref-item { padding: 10px; border-bottom: 1px solid #eee; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. SESSION STATE (Hafıza)
if 'references' not in st.session_state:
    st.session_state.references = []

st.title("📚 Citemate Pro")
st.caption("Profesyonel Akademik Yazım ve Atıf Sistemi")

# 3. EKRAN BÖLÜMLERİ
col_left, col_right = st.columns([6, 4])

with col_left:
    st.subheader("✍️ Akademik Editör")
    editor_text = st.text_area("Metninizi buraya yazın (Atıf yerlerine [cite] koyun)", 
                              placeholder="Gömülü kaninler üzerine yazmaya başlayın...",
                              height=400)
    
    # Atıf İşleme Mantığı
    processed_text = editor_text
    ref_count = len(st.session_state.references)
    
    for i in range(ref_count):
        processed_text = processed_text.replace("[cite]", f"({i+1})", 1)
    
    st.markdown("### 📖 Canlı Önizleme")
    st.markdown(f'<div class="preview-box">{processed_text}</div>', unsafe_allow_html=True)

with col_right:
    st.subheader("📋 Kaynak Yönetimi")
    
    with st.expander("➕ Yeni Kaynak Ekle", expanded=True):
        source_url = st.text_input("PubMed / Google Scholar / DOI Linki")
        cit_format = st.selectbox("Format", ["Vancouver", "APA", "Harvard", "MLA"])
        
        if st.button("Kaynağı İşle ve Listeye Ekle"):
            if source_url:
                timestamp = datetime.now().strftime("%Y")
                new_ref = {
                    "url": source_url,
                    "format": cit_format,
                    "display": f"{source_url} (Accessed: {timestamp})"
                }
                st.session_state.references.append(new_ref)
                st.rerun()
            else:
                st.error("Lütfen bir link girin.")

    st.divider()
    st.subheader("📖 Kaynakça (References)")
    
    if st.session_state.references:
        for idx, ref in enumerate(st.session_state.references):
            st.markdown(f"<div class='ref-item'><b>({idx+1})</b> {ref['display']} <br><small>Format: {ref['format']}</small></div>", unsafe_allow_html=True)
        
        if st.button("Kütüphaneyi Sıfırla"):
            st.session_state.references = []
            st.rerun()
    else:
        st.info("Henüz kaynak eklenmedi. [cite] kullanarak yazmaya başlayın.")
