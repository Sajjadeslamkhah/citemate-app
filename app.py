import streamlit as st
import re
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="Citemate Pro", page_icon="📚", layout="wide")

# CSS GÜNCELLEME (Okunabilirlik ve Buton Tasarımı)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    /* Önizleme Metni Rengi - Koyu Gri/Siyah yaparak okunabilirliği artırdık */
    .editor-container { 
        background-color: #ffffff; 
        color: #1a1a1a !important; 
        padding: 20px; 
        border-radius: 8px; 
        border: 1px solid #ddd;
        font-size: 16px;
        line-height: 1.6;
    }
    .stTextArea textarea { color: #1a1a1a !important; }
    /* Cite etiketi görünümü */
    .citation-number { background-color: #d4edda; color: #155724; padding: 2px 5px; border-radius: 4px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# SESSION STATE
if 'references' not in st.session_state: st.session_state.references = []
if 'editor_text' not in st.session_state: st.session_state.editor_text = ""

st.title("📚 Citemate Pro")
st.caption("Profesyonel Akademik Kaynak Yönetimi")

# FORMAT SEÇİMİ
format_options = ["Vancouver", "APA (Numeric)", "APA (Author-Date)", "Harvard", "MLA", "Chicago"]
selected_format = st.selectbox("Alıntı Formatı Seçin", format_options, index=1)

col_left, col_right = st.columns([6, 4], gap="large")

with col_left:
    st.subheader("✍️ Akademik Editör")
    # Metin Girişi
    editor_input = st.text_area("Yazı yazın", value=st.session_state.editor_text, height=400, key="main_editor")
    st.session_state.editor_text = editor_input

    # Önizleme ve Atıf İşleme
    processed_text = editor_input
    for i in range(len(st.session_state.references)):
        processed_text = processed_text.replace("[cite]", f"<span class='citation-number'>({i+1})</span>", 1)
    
    st.markdown("### 📖 Canlı Önizleme")
    # Beyaz yazı sorununu div içine stil vererek kökten çözüyoruz
    st.markdown(f'<div class="editor-container">{processed_text.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

with col_right:
    st.subheader("📖 Kaynak Yönetimi")
    
    # Yeni Kaynak Ekleme
    with st.container():
        c1, c2 = st.columns([3, 2])
        with c1: url = st.text_input("Kaynak URL", placeholder="https://...")
        with c2: author = st.text_input("Yazar", placeholder="İsteğe bağlı")
        
        bc1, bc2 = st.columns(2)
        with bc1:
            if st.button("➕ Kaynak Ekle", use_container_width=True, type="primary"):
                if url:
                    st.session_state.references.append({"url": url, "author": author if author else "Anonim", "date": datetime.now().strftime("%Y")})
                    st.rerun()
        with bc2:
            # CITE EKLE BUTONU - Metnin sonuna [cite] ekler
            if st.button("[cite] Ekle", use_container_width=True):
                st.session_state.editor_text += " [cite]"
                st.rerun()

    st.divider()
    st.subheader("📋 Eklenen Kaynaklar")
    if st.session_state.references:
        for idx, ref in enumerate(st.session_state.references):
            st.write(f"**({idx+1})** {ref['url']} - {ref['author']} ({ref['date']})")
        
        if st.button("🗑️ Tümünü Temizle"):
            st.session_state.references = []
            st.session_state.editor_text = ""
            st.rerun()
