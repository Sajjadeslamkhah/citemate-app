import streamlit as st
import requests
import fitz  # PyMuPDF
import re
from datetime import datetime
from bs4 import BeautifulSoup

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(page_title="Citemate AI Engine v8.1", page_icon="🧬", layout="wide")

# 2. GÖRSEL AYARLAR
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
    .cite-card { background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #34d399; margin-bottom: 10px; }
    code { color: #10b981 !important; font-size: 14px; white-space: pre-wrap !important; }
    </style>
    """, unsafe_allow_html=True)

if 'refs' not in st.session_state: st.session_state.refs = []

# 3. AKADEMİK VERİ ÇEKME MOTORU
def fetch_metadata_from_doi(doi):
    url = f"https://api.crossref.org/works/{doi}"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()['message']
            title = data.get('title', ['Bilinmeyen Başlık'])[0]
            # Yazar bilgisi çekme
            authors = data.get('author', [])
            author_str = authors[0].get('family', 'Anonim') if authors else "Anonim"
            year = data.get('created', {}).get('date-parts', [[datetime.now().year]])[0][0]
            return title, author_str, year
    except: return None

def get_web_metadata(url):
    """Linkten DOI veya Meta Tag kullanarak akademik veri çeker."""
    # 1. Adım: Link içinde DOI ara
    doi_match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', url, re.I)
    if doi_match:
        api_data = fetch_metadata_from_doi(doi_match.group())
        if api_data: return api_data

    # 2. Adım: Linke gidip HTML Meta Tag'leri tara
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        res = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Akademik meta etiketlerini dene (citation_title, dc.title vb.)
        title = (soup.find("meta", attrs={"name": "citation_title"}) or 
                 soup.find("meta", attrs={"name": "dc.title"}) or 
                 soup.find("meta", property="og:title") or 
                 soup.title)
        
        title_text = title["content"] if hasattr(title, "content") else (title.string if title else url)
        
        author = (soup.find("meta", attrs={"name": "citation_author"}) or 
                  soup.find("meta", attrs={"name": "dc.creator"}))
        author_text = author["content"] if hasattr(author, "content") else "Web Kaynağı"
        
        return title_text.strip(), author_text, datetime.now().year
    except:
        return url, "Web Kaynağı", datetime.now().year

def get_pdf_info(file_bytes):
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        first_page = doc[0].get_text()
        # PDF içinde DOI ara
        doi_match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', first_page, re.I)
        if doi_match:
            api_data = fetch_metadata_from_doi(doi_match.group())
            if api_data: return api_data
        
        # Metadata'ya bak
        meta = doc.metadata
        return meta.get("title") or "Bilinmeyen PDF", meta.get("author") or "Anonim", 2026
    except: return "Hatalı PDF", "Bilinmeyen", 2026

# 4. ARAYÜZ
st.title("🧬 Citemate AI Engine v8.1")
st.subheader("Gelişmiş Link ve PDF Teşhis İstasyonu")

style = st.selectbox("Format:", ["Vancouver", "APA 7th", "IEEE", "Harvard", "MLA 9th"])

col_in, col_out = st.columns([1, 1], gap="large")

with col_in:
    st.header("📥 Kaynak Yükle")
    t_link, t_pdf = st.tabs(["🔗 Gelişmiş Akıllı Link", "📄 Akıllı PDF Okuyucu"])
    
    with t_link:
        url_in = st.text_input("Makale URL veya DOI:")
        if st.button("Kaynağı AI ile Tara", key="link_btn"):
            if url_in:
                with st.spinner('Link analiz ediliyor...'):
                    t, a, y = get_web_metadata(url_in)
                    if not any(r['url'] == url_in for r in st.session_state.refs):
                        st.session_state.refs.append({"title": t, "author": a, "year": y, "url": url_in})
                        st.success("Başarıyla Teşhis Edildi!")
                    else: st.warning("Bu kaynak zaten ekli.")

    with t_pdf:
        pdf_file = st.file_uploader("PDF Dosyasını Sürükleyin", type="pdf")
        if pdf_file and st.button("PDF İçeriğini Çözümle"):
            t, a, y = get_pdf_info(pdf_file.read())
            st.session_state.refs.append({"title": t, "author": a, "year": y, "url": pdf_file.name})
            st.success("PDF Analiz Edildi!")

with col_out:
    st.header("📋 Profesyonel Çıktı")
    full_bib = ""
    for i, r in enumerate(st.session_state.refs, 1):
        if style == "Vancouver":
            cite = f"{i}. {r['author']}. {r['title']}. ({r['year']}). {r['url']}"
        elif style == "APA 7th":
            cite = f"{r['author']} ({r['year']}). {r['title']}. Retrieved from {r['url']}"
        else: # IEEE vb.
            cite = f"[{i}] {r['author']}, \"{r['title']}\", {r['year']}. [Online]. Available: {r['url']}"
        
        st.code(cite, language="text")
        full_bib += cite + "\n\n"
    
    if st.session_state.refs:
        st.download_button("⬇️ Tüm Kaynakçayı İndir", data=full_bib, file_name="kaynakca.txt")
        if st.button("🗑️ Temizle"):
            st.session_state.refs = []
            st.rerun()
