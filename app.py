import streamlit as st
import re
from datetime import datetime

# 1. TEMEL YAPILANDIRMA
st.set_page_config(layout="wide", page_title="Citemate Pro v3.0", page_icon="🧬")

# 2. PROFESYONEL CSS (Kesin Okunabilirlik Ayarı)
st.markdown("""
    <style>
    .stTextArea textarea { color: white !important; font-size: 18px !important; }
    .preview-box { 
        background-color: white !important; 
        color: black !important; 
        padding: 30px; 
        border-radius: 15px; 
        border: 5px solid #27ae60;
        font-family: 'Times New Roman', Times, serif;
        font-size: 18px;
        line-height: 1.8;
    }
    .cite-badge { color: #27ae60; font-weight: bold; background-color: #e8f5e9; padding: 2px 4px; border-radius: 4px; }
    </small>
    </style>
    """, unsafe_allow_html=True)

# 3. HAFIZA (SESSION STATE) YÖNETİMİ
if 'refs' not in st.session_state: st.session_state.refs = []
if 'paper_text' not in st.session_state: st.session_state.editor_content = ""

# 4. FONKSİYONLAR (Buton ve Mükerrer Kontrolü)
def insert_cite():
    st.session_state.editor_content += " [cite]"

def add_source(url):
    # Mükerrer Kontrolü
    if any(r['url'] == url for r in st.session_state.refs):
        st.warning("Bu kaynak zaten kütüphanenizde mevcut!")
        return
    st.session_state.refs.append({
        "url": url, 
        "title": url.split('/')[-1] if '/' in url else "Yeni Kaynak",
        "date": datetime.now().strftime("%Y-%m-%d")
    })

# 5. ARAYÜZ (Görsel Tasarım)
st.title("🧬 Citemate Pro v3.0")
st.write("Doktora ve Akademik Yazım İstasyonu")

col_left, col_right = st.columns([6, 4], gap="large")

with col_left:
    st.subheader("✍️ Akademik Editör")
    
    # Editör ve Hafıza Bağlantısı
    text_input = st.text_area("Makalenizi yazın:", value=st.session_state.editor_content, height=400, key="main_editor")
    st.session_state.editor_content = text_input

    # ATIF İŞLEME MOTORU
    processed = st.session_state.editor_content
    for i in range(len(st.session_state.refs)):
        processed = processed.replace("[cite]", f"<span class='cite-badge'>({i+1})</span>", 1)
    
    st.markdown("### 📄 Canlı Önizleme (Beyaz Arka Plan)")
    st.markdown(f'<div class="preview-box">{processed.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

with col_right:
    st.subheader("🛠️ Kontrol Paneli")
    
    # CITE BUTONU - Kesin Çalışan Formül
    st.button("➕ [cite] Etiketi Ekle", on_click=insert_cite, use_container_width=True)
    
    st.divider()
    
    st.subheader("📥 Kaynak Yükleme")
    new_url = st.text_input("Makale URL veya DOI:")
    if st.button("Kaynağı Kaydet", type="primary", use_container_width=True):
        if new_url:
            add_source(new_url)
            st.rerun()

    st.divider()
    st.subheader("📖 Kaynakça (References)")
    if st.session_state.refs:
        for idx, ref in enumerate(st.session_state.refs):
            st.markdown(f"**({idx+1})** {ref['url']} <br><small>Eklenme: {ref['date']}</small>", unsafe_allow_html=True)
        
        if st.button("🗑️ Her Şeyi Sıfırla"):
            st.session_state.refs = []
            st.session_state.editor_content = ""
            st.rerun()
    else:
        st.info("Kütüphane boş. Henüz kaynak eklemediniz.")
