import streamlit as st
import requests
import re
from datetime import datetime
import fitz  # PyMuPDF

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Citemate Pro v9.2", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
    .stTextInput input { color: #ffffff !important; background-color: #262730 !important; border: 1px solid #34d399 !important; }
    .cite-card { background-color: #1e1e1e; padding: 15px; border-radius: 10px; border-left: 4px solid #34d399; margin-bottom: 15px; }
    .result-box { background-color: #1a1a1a; padding: 20px; border: 2px solid #34d399; border-radius: 10px; margin: 15px 0; }
    .intext-box { background-color: #002b36; color: #93a1a1; padding: 10px; border-radius: 5px; border-left: 5px solid #268bd2; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

# 2. SESSION STATE
if 'refs' not in st.session_state: st.session_state.refs = []
if 'temp_search' not in st.session_state: st.session_state.temp_search = None

# 3. GÜVENLİ VERİ ÇEKME FONKSİYONLARI
def fetch_crossref(query, is_doi=False):
    url = f"https://api.crossref.org/works/{query}" if is_doi else f"https://api.crossref.org/works?query={query}&rows=1"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code != 200: return None
        data = res.json()['message']
        item = data['items'][0] if 'items' in data else data
        
        # Verileri güvenli şekilde al (None hatasını önler)
        title = item.get('title', ['Başlık Bulunamadı'])[0]
        authors = item.get('author', [])
        
        author_str = "Anonim"
        if authors:
            author_str = authors[0].get('family') or authors[0].get('literal') or "Anonim"
            if len(authors) > 1: author_str += " et al."
        
        try:
            # Farklı tarih formatlarını dene
            year = item.get('created', {}).get('date-parts', [[2026]])[0][0]
        except:
            year = datetime.now().year
            
        doi = f"https://doi.org/{item.get('DOI')}" if item.get('DOI') else item.get('URL', 'Link Yok')
        
        return {"title": str(title), "author": str(author_str), "year": str(year), "url": str(doi)}
    except Exception as e:
        return None

def process_pdf(file_bytes, filename):
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = "".join([doc[i].get_text() for i in range(min(len(doc), 2))])
        doi_match = re.search(r'10\.\d{4,}/[^\s\)]+', text, re.I)
        if doi_match:
            return fetch_crossref(doi_match.group().strip("/"), is_doi=True)
        lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 10]
        return {"title": lines[0] if lines else filename, "author": "Doküman", "year": "2026", "url": filename}
    except: return None

# 4. ARAYÜZ
st.title("🎓 Citemate Pro v9.2")
style = st.selectbox("📌 Atıf Formatı:", ["Vancouver", "APA 7th", "IEEE", "MLA 9th", "Harvard"])

col_in, col_out = st.columns([4, 6], gap="large")

with col_in:
    st.header("📥 Kaynak Ekle")
    t_search, t_link, t_pdf = st.tabs(["🔍 Başlık", "🔗 DOI/Link", "📄 PDF"])
    
    with t_search:
        title_q = st.text_input("Makale Adı:", key="q_search")
        if st.button("🔍 Bul"):
            if title_q.strip():
                res = fetch_crossref(title_q)
                if res: st.session_state.temp_search = res
                else: st.error("Bulunamadı.")
        
        if st.session_state.temp_search:
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.write(f"**Başlık:** {st.session_state.temp_search.get('title')}")
            st.write(f"**Yazar:** {st.session_state.temp_search.get('author')} | **Yıl:** {st.session_state.temp_search.get('year')}")
            st.markdown('</div>', unsafe_allow_html=True)
            if st.button("✅ Onayla"):
                st.session_state.refs.append(st.session_state.temp_search)
                st.session_state.temp_search = None
                st.rerun()

    with t_link:
        url_in = st.text_input("DOI veya URL:")
        if st.button("➕ Ekle"):
            doi_match = re.search(r'10\.\d{4,}/[^\s\)]+', url_in, re.I)
            res = fetch_crossref(doi_match.group().strip("/"), is_doi=True) if doi_match else {"title": url_in, "author": "Web", "year": "2026", "url": url_in}
            st.session_state.refs.append(res)
            st.rerun()

    with t_pdf:
        pdf_file = st.file_uploader("PDF Yükle", type="pdf")
        if pdf_file and st.button("📄 Analiz"):
            res = process_pdf(pdf_file.read(), pdf_file.name)
            if res: st.session_state.refs.append(res); st.rerun()

with col_out:
    st.header("📋 Kaynakça")
    if st.session_state.refs:
        tab_bib, tab_intext = st.tabs(["📋 Liste", "🖋️ Metin İçi"])
        all_bib = ""
        
        with tab_bib:
            for i, r in enumerate(st.session_state.refs, 1):
                # Hata önleyici güvenli veri çekimi (.get)
                auth = r.get('author', 'Anonim')
                titl = r.get('title', 'Başlık Yok')
                year = r.get('year', '2026')
                link = r.get('url', 'Link Yok')
                
                if style == "Vancouver": cite = f"{i}. {auth}. {titl}. {year}. {link}"
                elif style == "APA 7th": cite = f"{auth} ({year}). {titl}. {link}"
                else: cite = f"[{i}] {auth}, \"{titl}\", {year}. {link}"
                
                st.code(cite)
                all_bib += cite + "\n\n"
        
        with tab_intext:
            for i, r in enumerate(st.session_state.refs, 1):
                intext = f"({i})" if style == "Vancouver" else f"({r.get('author', 'Anonim')}, {r.get('year', '2026')})"
                st.markdown(f'<div class="intext-box">{intext}</div>', unsafe_allow_html=True)
        
        st.download_button("📥 İndir (.txt)", all_bib, "kaynakca.txt")
        if st.button("🗑️ Sıfırla"): st.session_state.refs = []; st.rerun()
    else:
        st.info("Kaynak ekleyin.")
