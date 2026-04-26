import streamlit as st
import requests
import fitz  # PyMuPDF
import re
from datetime import datetime
from bs4 import BeautifulSoup

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(page_title="Citemate Ultimate v8.6", page_icon="🎓", layout="wide")

# 2. GELİŞMİŞ GÖRSEL AYARLAR
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
    .stTextInput input { color: #ffffff !important; background-color: #262730 !important; }
    .cite-card { background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #34d399; margin-bottom: 15px; }
    code { color: #10b981 !important; font-size: 14px; white-space: pre-wrap !important; }
    .intext-box { background-color: #002b36; color: #93a1a1; padding: 10px; border-radius: 5px; font-weight: bold; border-left: 5px solid #268bd2; margin: 5px 0; }
    </style>
    """, unsafe_allow_html=True)

if 'refs' not in st.session_state: st.session_state.refs = []

# 3. AKILLI AKADEMİK ARAMA VE ÇEKME FONKSİYONLARI
def fetch_from_crossref(query, is_doi=False):
    """DOI veya Başlık ile Crossref üzerinden arama yapar."""
    if is_doi:
        url = f"https://api.crossref.org/works/{query}"
    else:
        # Başlık araması için query parametresi kullanılır
        url = f"https://api.crossref.org/works?query={query}&rows=1"
    
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()['message']
            # Eğer başlık aramasıysa liste döner, DOI ise direkt obje
            item = data['items'][0] if 'items' in data else data
            
            title = item.get('title', ['Başlık Bulunamadı'])[0]
            authors = item.get('author', [])
            author_str = authors[0].get('family', 'Anonim') if authors else "Anonim"
            try:
                year = item.get('created', {}).get('date-parts', [[2026]])[0][0]
            except: year = 2026
            doi_link = f"https://doi.org/{item.get('DOI', '')}" if item.get('DOI') else ""
            return title, author_str, year, doi_link
    except: return None
    return None

def process_pdf(file_bytes, filename):
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = "".join([doc[i].get_text() for i in range(min(len(doc), 2))])
        doi_match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', text, re.I)
        if doi_match:
            return fetch_from_crossref(doi_match.group().strip("/"), is_doi=True)
        lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 15]
        return lines[0], "Doküman", 2026, filename
    except: return filename, "Hata", 2026, filename

# 4. ARAYÜZ
st.title("🎓 Citemate Ultimate v8.6")
st.subheader("Gelişmiş Atıf İstasyonu: Link, PDF ve Başlık ile Arama")

style = st.selectbox("Format Seçin:", ["Vancouver", "APA 7th", "IEEE", "MLA 9th", "Harvard"])

col_in, col_out = st.columns([4, 6], gap="large")

with col_in:
    st.header("📥 Kaynak Ekle")
    t_search, t_link, t_pdf = st.tabs(["🔍 Başlık ile Bul", "🔗 DOI / Link", "📄 PDF Yükle"])
    
    with t_search:
        title_q = st.text_input("Makale Adını Yazın:", placeholder="Örn: Effects of 3D scanning in dentistry...")
        if st.button("Makaleyi Bul ve Ekle"):
            if title_q:
                with st.spinner("Akademik veri tabanları taranıyor..."):
                    res = fetch_from_crossref(title_q)
                    if res:
                        st.session_state.refs.append({"title": res[0], "author": res[1], "year": res[2], "url": res[3]})
                        st.success(f"Bulundu: {res[0]}")
                        st.rerun()

    with t_link:
        url_in = st.text_input("DOI veya Tam URL:")
        if st.button("Teşhis Et ve Ekle"):
            doi_match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', url_in, re.I)
            with st.spinner("Analiz ediliyor..."):
                if doi_match:
                    res = fetch_from_crossref(doi_match.group().strip("/"), is_doi=True)
                else: # Scrapping dene
                    res = (url_in, "Web Kaynağı", 2026, url_in)
                st.session_state.refs.append({"title": res[0], "author": res[1], "year": res[2], "url": res[3]})
                st.rerun()

    with t_pdf:
        pdf_file = st.file_uploader("PDF Sürükleyin", type="pdf")
        if pdf_file and st.button("PDF Analiz Et"):
            with st.spinner("Okunuyor..."):
                res = process_pdf(pdf_file.read(), pdf_file.name)
                st.session_state.refs.append({"title": res[0], "author": res[1], "year": res[2], "url": res[3]})
                st.rerun()

with col_out:
    tab_bib, tab_intext = st.tabs(["📋 Kaynakça Listesi", "🖋️ Metin İçi (In-text)"])
    
    all_bib = ""
    all_intext = ""

    if st.session_state.refs:
        with tab_bib:
            for i, r in enumerate(st.session_state.refs, 1):
                if style == "Vancouver":
                    cite = f"{i}. {r['author']}. {r['title']}. ({r['year']}). {r['url']}"
                elif style == "APA 7th":
                    cite = f"{r['author']} ({r['year']}). {r['title']}. {r['url']}"
                elif style == "IEEE":
                    cite = f"[{i}] {r['author']}, \"{r['title']}\", {r['year']}. {r['url']}"
                else:
                    cite = f"{r['author']}, {r['title']}, {r['year']}."
                
                st.code(cite)
                all_bib += cite + "\n\n"

        with tab_intext:
            for i, r in enumerate(st.session_state.refs, 1):
                intext = f"({i})" if style == "Vancouver" else f"({r['author']}, {r['year']})"
                st.markdown(f"**{r['title'][:50]}...**")
                st.markdown(f'<div class="intext-box">{intext}</div>', unsafe_allow_html=True)
                all_intext += intext + " "

        st.divider()
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button("📥 Kaynakçayı TXT İndir", data=all_bib, file_name="kaynakca.txt", use_container_width=True)
        with col_d2:
            if st.button("🗑️ Tümünü Sil", use_container_width=True):
                st.session_state.refs = []
                st.rerun()
        
        st.subheader("Toplu Metin İçi Kopyalama")
        st.text_area("Atıf Etiketleri:", value=all_intext, height=100)
    else:
        st.info("Henüz kaynak eklenmedi.")    """Tüm sayfaları değil, sadece kritik alanları tarayan hızlı PDF okuyucu."""
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
