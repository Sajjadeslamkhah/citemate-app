import streamlit as st
import requests
import fitz  # PyMuPDF
import re
from datetime import datetime

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(page_title="Citemate AI Engine", page_icon="🧬", layout="wide")

# 2. CSS - OKUNABİLİRLİK ODAKLI
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
    .cite-card { background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #34d399; margin-bottom: 10px; }
    code { color: #10b981 !important; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

if 'refs' not in st.session_state: st.session_state.refs = []

# 3. AKILLI VERİ ÇEKME FONKSİYONLARI (AI & API)
def fetch_metadata_from_doi(doi):
    """DOI numarasını Crossref API üzerinden sorgular."""
    url = f"https://api.crossref.org/works/{doi}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()['message']
            title = data.get('title', ['Bilinmeyen Başlık'])[0]
            author = data.get('author', [{'family': 'Anonim'}])[0].get('family')
            year = data.get('created', {}).get('date-parts', [[datetime.now().year]])[0][0]
            return title, author, year
    except: return None

def get_pdf_info(file_bytes):
    """PDF içindeki metadata'yı AI/Programatik olarak tarar."""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        meta = doc.metadata
        title = meta.get("title") or "Bilinmeyen PDF Başlığı"
        author = meta.get("author") or "Anonim Yazar"
        # Eğer metadata boşsa ilk sayfadan DOI taraması yapar
        first_page = doc[0].get_text()
        doi_match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', first_page, re.I)
        if doi_match:
            api_data = fetch_metadata_from_doi(doi_match.group())
            if api_data: return api_data
        return title, author, datetime.now().year
    except: return "Hatalı PDF", "Bilinmeyen", 2026

def fetch_web_title(url):
    """Web linkinden DOI veya Title ayıklar."""
    doi_match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', url, re.I)
    if doi_match:
        api_data = fetch_metadata_from_doi(doi_match.group())
        if api_data: return api_data
    return url, "Web Kaynağı", datetime.now().year

# 4. ARAYÜZ
st.title("🧬 Citemate AI Engine v8")
st.subheader("Otomatik Akademik Teşhis ve Formatlama")

style = st.selectbox("Format:", ["Vancouver", "APA 7th", "IEEE", "Harvard"])

col_in, col_out = st.columns([1, 1], gap="large")

with col_in:
    st.header("📥 Kaynak Yükle")
    tab_link, tab_pdf = st.tabs(["🔗 Akıllı Link", "📄 Akıllı PDF Okuyucu"])
    
    with tab_link:
        url_in = st.text_input("URL veya DOI:")
        if st.button("Kaynağı AI ile Tara"):
            if url_in:
                t, a, y = fetch_web_title(url_in)
                st.session_state.refs.append({"title": t, "author": a, "year": y, "url": url_in})
                st.success(f"Teşhis Edildi: {t}")

    with tab_pdf:
        pdf_file = st.file_uploader("PDF Dosyasını Sürükleyin", type="pdf")
        if pdf_file:
            if st.button("PDF İçeriğini Çözümle"):
                t, a, y = get_pdf_info(pdf_file.read())
                st.session_state.refs.append({"title": t, "author": a, "year": y, "url": pdf_file.name})
                st.success(f"PDF Analiz Edildi: {t}")

with col_out:
    st.header("📋 Profesyonel Çıktı")
    full_bib = ""
    for i, r in enumerate(st.session_state.refs, 1):
        if style == "Vancouver":
            cite = f"{i}. {r['author']}. {r['title']}. ({r['year']}). {r['url']}"
        else:
            cite = f"{r['author']} ({r['year']}). {r['title']}. Retrieved from {r['url']}"
        
        st.code(cite, language="text")
        full_bib += cite + "\n\n"
    
    if st.session_state.refs:
        st.download_button("⬇️ Tüm Kaynakçayı İndir", data=full_bib, file_name="kaynakca.txt")
        if st.button("🗑️ Temizle"):
            st.session_state.refs = []
            st.rerun()
