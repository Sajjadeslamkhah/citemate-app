import streamlit as st
import requests
import fitz  # PyMuPDF
import re
from datetime import datetime

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Citemate AI v8.5", page_icon="⚡", layout="wide")

# 2. CSS (Performans için minimalist stil)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1, h2, h3, label, span { color: white !important; }
    .stAlert { background-color: #1a1a1a !important; color: white !important; }
    code { color: #10b981 !important; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

if 'refs' not in st.session_state: st.session_state.refs = []

# 3. HIZLANDIRILMIŞ FONKSİYONLAR
def fetch_metadata(doi):
    """Sadece gerekli veriyi çeken optimize API sorgusu."""
    try:
        res = requests.get(f"https://api.crossref.org/works/{doi}", timeout=5)
        if res.status_code == 200:
            msg = res.json()['message']
            title = msg.get('title', ['Başlık Bulunamadı'])[0]
            author = msg.get('author', [{'family': 'Anonim'}])[0].get('family')
            year = msg.get('created', {}).get('date-parts', [[2026]])[0][0]
            return title, author, year
    except: return None

@st.cache_data(show_spinner=False) # Önbellekleme ekleyerek aynı dosyayı tekrar okumayı engelliyoruz
def fast_process_pdf(file_bytes, filename):
    """Tüm sayfaları değil, sadece kritik alanları tarayan hızlı PDF okuyucu."""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        # Sadece ilk 3 sayfayı oku (DOI genellikle buradadır)
        search_text = ""
        for i in range(min(len(doc), 3)):
            search_text += doc[i].get_text()
        
        # DOI Bulma (En hızlı yöntem)
        doi_match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', search_text, re.I)
        if doi_match:
            data = fetch_metadata(doi_match.group().strip("/"))
            if data: return data[0], data[1], data[2], f"DOI: {doi_match.group()}"
        
        # Metadata Kontrolü
        if doc.metadata.get("title"):
            return doc.metadata["title"], doc.metadata.get("author", "Anonim"), 2026, filename
        
        # İlk satırı başlık al (Protokol/Deney dosyaları için)
        lines = [l.strip() for l in search_text.split('\n') if len(l.strip()) > 10]
        return (lines[0], "Doküman", 2026, filename) if lines else (filename, "Dosya", 2026, filename)
    except: return filename, "Hata", 2026, filename

# 4. ARAYÜZ
st.title("⚡ Citemate AI v8.5")
style = st.selectbox("Format:", ["Vancouver", "APA 7th", "IEEE", "Harvard"])

c1, c2 = st.columns([4, 6])

with c1:
    st.header("📥 Hızlı Yükle")
    # Dosya boyutu uyarısı
    st.caption("Not: 5MB altındaki PDF'ler daha hızlı işlenir.")
    pdf_file = st.file_uploader("PDF Seçin", type="pdf")
    
    if pdf_file:
        # Spinner (yükleniyor simgesi) sadece işlem sırasında görünür
        if st.button("Hızlı Analiz Et"):
            with st.spinner("AI Dosyayı okuyor..."):
                t, a, y, src = fast_process_pdf(pdf_file.read(), pdf_file.name)
                st.session_state.refs.append({"title": t, "author": a, "year": y, "url": src})
                st.rerun()

with c2:
    tab_bib, tab_intext = st.tabs(["📋 Kaynakça", "🖋️ Metin İçi"])
    if st.session_state.refs:
        with tab_bib:
            for i, r in enumerate(st.session_state.refs, 1):
                cite = f"{i}. {r['author']}. {r['title']}. ({r['year']}). {r['url']}" if style == "Vancouver" else f"{r['author']} ({r['year']}). {r['title']}. {r['url']}"
                st.code(cite)
        with tab_intext:
            for i, r in enumerate(st.session_state.refs, 1):
                intext = f"({i})" if style == "Vancouver" else f"({r['author']}, {r['year']})"
                st.markdown(f"**{r['title'][:50]}...** → `{intext}`")
        
        if st.button("🗑️ Temizle"):
            st.session_state.refs = []
            st.rerun()
