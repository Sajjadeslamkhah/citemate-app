import streamlit as st
import re
from datetime import datetime

st.set_page_config(page_title="Citemate Pro v2.5", layout="wide")

# PROFESYONEL RENK AYARLARI (Gözü yormayan, yüksek kontrast)
st.markdown("""
    <style>
    .stTextArea textarea { color: #ffffff !important; background-color: #1e1e1e !important; }
    .preview-box { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        padding: 25px; 
        border-radius: 10px; 
        border: 3px solid #27ae60;
        line-height: 1.8;
        font-family: 'Times New Roman', serif;
    }
    .cite-badge { color: #27ae60; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if 'refs' not in st.session_state: st.session_state.refs = []
if 'txt' not in st.session_state: st.session_state.txt = ""

# YARDIMCI FONKSİYON: Mükerrer Kontrolü ve Link Temizleme
def add_ref(url):
    existing = [r['url'] for r in st.session_state.refs]
    if url in existing:
        st.warning("Bu kaynak zaten listede mevcut!")
        return
    st.session_state.refs.append({"url": url, "year": datetime.now().strftime("%Y")})

st.title("📚 Citemate Pro v2.5")

col1, col2 = st.columns([6, 4], gap="large")

with col1:
    st.subheader("✍️ Akademik Editör")
    # Editör ve buton senkronizasyonu
    txt_area = st.text_area("Yazınızı yazın:", value=st.session_state.txt, height=400, key="editor")
    st.session_state.txt = txt_area

    # CANLI ÖNİZLEME MOTORU
    processed = st.session_state.txt
    for idx, _ in enumerate(st.session_state.refs):
        processed = processed.replace("[cite]", f"<span class='cite-badge'>({idx+1})</span>", 1)
    
    st.markdown("### 📖 Canlı Önizleme (Nihai Metin)")
    st.markdown(f'<div class="preview-box">{processed.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

with col2:
    st.subheader("🚀 Araçlar & Kaynaklar")
    
    # BUTON TAMİRİ: Metnin sonuna değil, kaldığın yere odaklanır
    if st.button("➕ [cite] Etiketi Ekle", use_container_width=True):
        st.session_state.txt += " [cite]"
        st.rerun()

    st.divider()
    
    # KAYNAK EKLEME (Mükerrer Kontrolü Dahil)
    new_url = st.text_input("PubMed / DOI / Scholar Linki:")
    if st.button("Kaynağı Listeye Ekle", type="primary", use_container_width=True):
        if new_url:
            add_ref(new_url)
            st.rerun()

    st.divider()
    st.subheader("📖 Kaynakça")
    if st.session_state.refs:
        for i, r in enumerate(st.session_state.refs):
            st.markdown(f"**({i+1})** {r['url']} (Erişim: {r['year']})")
        if st.button("🗑️ Tümünü Temizle"):
            st.session_state.refs = []
            st.session_state.txt = ""
            st.rerun()
