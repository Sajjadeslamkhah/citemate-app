import streamlit as st
import requests
import fitz  # PyMuPDF
import re
from datetime import datetime
from bs4 import BeautifulSoup

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(page_title="Citemate AI Engine v8.3", page_icon="🧬", layout="wide")

# 2. GÖRSEL AYARLAR
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
    .stTextInput input { color: #ffffff !important; background-color: #262730 !important; }
    .cite-card { background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #34d399; margin-bottom: 10px; }
    code { color: #10b981 !important; font-size: 14px; white-space: pre-wrap !important; }
    </style>
    """, unsafe_allow_html=True)

if 'refs' not in st.session_state: st.session_state.refs = []

# 3. AKADEMİK VERİ ÇEKME MOTORU
def fetch_from_crossref(doi):
    url = f"https://api.crossref.org/works/{doi}"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()['message']
            title = data.get('title', ['Başlık Bulunamadı'])[0]
            authors = data.get('author', [])
            author_str = authors[0].get('family', 'Anonim') if authors else "Anonim"
            year = data.get('created', {}).get('date-parts', [[datetime.now().year]])[0][0]
            return title, author_str, year
    except: return None

def process_input(input_data):
    doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
    doi_match = re.search(doi_pattern, input_data, re.I)
    if doi_match:
        doi = doi_match.group().strip("/")
        api_data = fetch_from_crossref(doi)
        if api_data: return api_data[0], api_data[1], api_data[2], f"https://doi.org/{doi}"
    return input_data, "Web Kaynağı", datetime.now().year, input_data

def process_pdf(file_bytes, filename):
    """PDF içeriğini daha akıllı tarar."""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        # İlk 2 sayfadaki metni al
        full_text = ""
        for i in range(min(len(doc), 2)):
            full_text += doc[i].get_text()
        
        # 1. Strateji: DOI Ara
        doi_match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', full_text, re.I)
        if doi_match:
            api_data = fetch_from_crossref(doi_match.group().strip("/"))
            if api_data: return api_data[0], api_data[1], api_data[2], f"DOI: {doi_match.group()}"
        
        # 2. Strateji: PDF Meta verisinden çek
        if doc.metadata.get("title"):
            return doc.metadata["title"], doc.metadata.get("author", "Anonim"), 2026, filename

        # 3. Strateji: PDF'in en üstündeki ilk anlamlı satırı başlık al
        lines = [l.strip() for l in full_text.split('\n') if len(l.strip()) > 10]
        if lines:
            return lines[0], "Doküman", 2026, filename
            
        return filename.replace(".pdf", ""), "Dosya", 2026, filename
    except:
        return filename, "Hata", 2026, filename

# 4. ARAYÜZ
st.title("🧬 Citemate AI Engine v8.3")
style = st.selectbox("Format:", ["Vancouver", "APA 7th", "IEEE"])

col_in, col_out = st.columns([1, 1], gap="large")

with col_in:
    st.header("📥 Kaynak Yükle")
    t_link, t_pdf = st.tabs(["🔗 DOI veya Link", "📄 PDF Dosyası"])
    with t_link:
        url_in = st.text_input("DOI veya URL:")
        if st.button("Teşhis Et"):
            t, a, y, src = process_input(url_in)
            st.session_state.refs.append({"title": t, "author": a, "year": y, "url": src})
    with t_pdf:
        pdf_file = st.file_uploader("PDF Sürükleyin", type="pdf")
        if pdf_file and st.button("PDF Analiz Et"):
            t, a, y, src = process_pdf(pdf_file.read(), pdf_file.name)
            st.session_state.refs.append({"title": t, "author": a, "year": y, "url": src})

with col_out:
    st.header("📋 Çıktı")
    for i, r in enumerate(st.session_state.refs, 1):
        cite = f"{i}. {r['author']}. {r['title']}. ({r['year']}). {r['url']}" if style == "Vancouver" else f"{r['author']} ({r['year']}). {r['title']}. {r['url']}"
        st.code(cite)
    
    if st.session_state.refs:
        if st.button("🗑️ Temizle"):
            st.session_state.refs = []
            st.rerun()
