import streamlit as st
import requests
import fitz  # PyMuPDF
import re
from datetime import datetime
from bs4 import BeautifulSoup

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(page_title="Citemate AI Engine v8.4", page_icon="🧬", layout="wide")

# 2. GELİŞMİŞ CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
    .stTextInput input { color: #ffffff !important; background-color: #262730 !important; }
    .cite-card { background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #34d399; margin-bottom: 15px; }
    code { color: #10b981 !important; font-size: 14px; white-space: pre-wrap !important; }
    .intext-box { background-color: #002b36; color: #93a1a1; padding: 10px; border-radius: 5px; font-weight: bold; border-left: 5px solid #268bd2; }
    </style>
    """, unsafe_allow_html=True)

if 'refs' not in st.session_state: st.session_state.refs = []

# 3. VERİ ÇEKME FONKSİYONLARI
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
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        full_text = "".join([doc[i].get_text() for i in range(min(len(doc), 2))])
        doi_match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', full_text, re.I)
        if doi_match:
            api_data = fetch_from_crossref(doi_match.group().strip("/"))
            if api_data: return api_data[0], api_data[1], api_data[2], f"DOI: {doi_match.group()}"
        lines = [l.strip() for l in full_text.split('\n') if len(l.strip()) > 10]
        title = lines[0] if lines else filename.replace(".pdf", "")
        return title, "Doküman", 2026, filename
    except: return filename, "Hata", 2026, filename

# 4. ARAYÜZ
st.title("🧬 Citemate AI Engine v8.4")
st.subheader("Atıf ve Metin İçi Referans Yönetimi")

# FORMAT SEÇİMİ (Dinamik Etki)
style = st.selectbox("Akademik Format Seçin:", ["Vancouver", "APA 7th", "IEEE", "MLA 9th", "Harvard"])

col_in, col_out = st.columns([4, 6], gap="large")

with col_in:
    st.header("📥 Kaynak Yükle")
    t_link, t_pdf = st.tabs(["🔗 DOI / Link", "📄 PDF Dosyası"])
    with t_link:
        url_in = st.text_input("Makale DOI veya URL:", key="url_in")
        if st.button("Teşhis Et"):
            if url_in:
                t, a, y, src = process_input(url_in)
                st.session_state.refs.append({"title": t, "author": a, "year": y, "url": src})
                st.rerun()
    with t_pdf:
        pdf_file = st.file_uploader("PDF Sürükleyin", type="pdf")
        if pdf_file and st.button("PDF Analiz Et"):
            t, a, y, src = process_pdf(pdf_file.read(), pdf_file.name)
            st.session_state.refs.append({"title": t, "author": a, "year": y, "url": src})
            st.rerun()

with col_out:
    # SONUÇ SEKME YAPISI
    tab_bib, tab_intext = st.tabs(["📋 Kaynakça Listesi", "🖋️ Metin İçi (In-text) Atıf"])
    
    all_bib_text = ""
    all_intext_text = ""

    if st.session_state.refs:
        with tab_bib:
            for i, r in enumerate(st.session_state.refs, 1):
                if style == "Vancouver":
                    res = f"{i}. {r['author']}. {r['title']}. ({r['year']}). {r['url']}"
                elif style == "APA 7th":
                    res = f"{r['author']} ({r['year']}). {r['title']}. {r['url']}"
                elif style == "IEEE":
                    res = f"[{i}] {r['author']}, \"{r['title']}\", {r['year']}. {r['url']}"
                else:
                    res = f"{r['author']}, {r['title']}, {r['year']}."
                
                st.markdown(f"**Kaynak {i}**")
                st.code(res)
                all_bib_text += res + "\n\n"

        with tab_intext:
            st.info(f"💡 {style} formatına göre makale içinde kullanmanız gereken gösterimler:")
            for i, r in enumerate(st.session_state.refs, 1):
                if style in ["Vancouver", "IEEE"]:
                    intext = f"({i})" if style == "Vancouver" else f"[{i}]"
                elif style == "APA 7th":
                    intext = f"({r['author']}, {r['year']})"
                elif style == "MLA 9th":
                    intext = f"({r['author']})"
                else: # Harvard
                    intext = f"({r['author']} {r['year']})"
                
                st.markdown(f"**{r['title'][:60]}...**")
                st.markdown(f'<div class="intext-box">{intext}</div>', unsafe_allow_html=True)
                all_intext_text += intext + " "
            
            st.divider()
            st.subheader("Toplu Metin İçi Kopyalama")
            st.text_area("Tüm atıf etiketleri:", value=all_intext_text, height=100)

        st.divider()
        st.download_button("📥 Kaynakçayı İndir", data=all_bib_text, file_name="kaynakca.txt")
        if st.button("🗑️ Tümünü Sil"):
            st.session_state.refs = []
            st.rerun()
    else:
        st.info("Henüz kaynak eklenmedi.")
