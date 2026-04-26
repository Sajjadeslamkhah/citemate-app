import streamlit as st
import requests
import re
from datetime import datetime
from urllib.parse import urlparse
import fitz  # PyMuPDF

# ============================================================================
# 1. PAGE CONFIGURATION & STYLING
# ============================================================================
st.set_page_config(page_title="Citemate Pro v9.1", page_icon="🎓", layout="wide")

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

# ============================================================================
# 2. SESSION STATE
# ============================================================================
if 'refs' not in st.session_state: st.session_state.refs = []
if 'temp_search' not in st.session_state: st.session_state.temp_search = None

# ============================================================================
# 3. CORE FUNCTIONS (CLAUDE'S LOGIC + SEARCH)
# ============================================================================
def fetch_crossref(query, is_doi=False):
    url = f"https://api.crossref.org/works/{query}" if is_doi else f"https://api.crossref.org/works?query={query}&rows=1"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()['message']
        item = data['items'][0] if 'items' in data else data
        
        title = item.get('title', ['Başlık Bulunamadı'])[0]
        authors = item.get('author', [])
        author_str = authors[0].get('family', 'Anonim') if authors else "Anonim"
        if len(authors) > 1: author_str += " et al."
        
        try: year = item.get('created', {}).get('date-parts', [[2026]])[0][0]
        except: year = 2026
        
        doi = f"https://doi.org/{item.get('DOI')}" if item.get('DOI') else item.get('URL', 'Link Yok')
        
        return {"title": title, "author": author_str, "year": year, "url": doi}
    except: return None

def process_pdf(file_bytes, filename):
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = "".join([doc[i].get_text() for i in range(min(len(doc), 2))])
        doi_match = re.search(r'10\.\d{4,}/[^\s\)]+', text, re.I)
        if doi_match:
            return fetch_crossref(doi_match.group().strip("/"), is_doi=True)
        lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 15]
        return {"title": lines[0] if lines else filename, "author": "Doküman", "year": 2026, "url": filename}
    except: return None

# ============================================================================
# 4. UI DESIGN
# ============================================================================
st.title("🎓 Citemate Pro v9.1")
st.caption("Claude v9.0 Mimarisi + Gemini Onay Sistemi")

style = st.selectbox("📌 Akademik Format:", ["Vancouver", "APA 7th", "IEEE", "MLA 9th", "Harvard"], index=0)

col_in, col_out = st.columns([4, 6], gap="large")

with col_in:
    st.header("📥 Kaynak Ekle")
    t_search, t_link, t_pdf = st.tabs(["🔍 Başlık ile Ara", "🔗 DOI / Link", "📄 PDF Yükle"])
    
    with t_search:
        title_q = st.text_input("Makale Adını Yazın:", placeholder="Örn: 3D surgical guides in dentistry")
        if st.button("🔍 AI ile Bul"):
            if title_q.strip():
                with st.spinner("🔄 Akademik veritabanları taranıyor..."):
                    res = fetch_crossref(title_q)
                    if res: st.session_state.temp_search = res
                    else: st.error("Sonuç bulunamadı.")
            else: st.warning("Lütfen bir başlık girin.")
        
        # ONAY MEKANİZMASI (Gemini'nin eklediği kısım)
        if st.session_state.temp_search:
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown(f"### 📚 Bulunan Kaynak")
            st.markdown(f"**Başlık:** {st.session_state.temp_search['title']}")
            st.markdown(f"**Yazar:** {st.session_state.temp_search['author']} | **Yıl:** {st.session_state.temp_search['year']}")
            st.markdown('</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Evet, Doğru", use_container_width=True, type="primary"):
                    st.session_state.refs.append(st.session_state.temp_search)
                    st.session_state.temp_search = None
                    st.rerun()
            with c2:
                if st.button("❌ Hayır, Yanlış", use_container_width=True):
                    st.session_state.temp_search = None
                    st.rerun()

    with t_link:
        url_in = st.text_input("DOI veya URL yapıştırın:")
        if st.button("➕ Hızlı Ekle", use_container_width=True):
            doi_match = re.search(r'10\.\d{4,}/[^\s\)]+', url_in, re.I)
            res = fetch_crossref(doi_match.group().strip("/"), is_doi=True) if doi_match else {"title": url_in, "author": "Web", "year": 2026, "url": url_in}
            st.session_state.refs.append(res)
            st.rerun()

    with t_pdf:
        pdf_file = st.file_uploader("PDF Sürükleyin", type="pdf")
        if pdf_file and st.button("📄 PDF Analiz Et", use_container_width=True):
            res = process_pdf(pdf_file.read(), pdf_file.name)
            if res:
                st.session_state.refs.append(res)
                st.rerun()

with col_out:
    st.header("📋 Çıktı Paneli")
    if st.session_state.refs:
        tab_bib, tab_intext = st.tabs(["📋 Kaynakça", "🖋️ Metin İçi (In-text)"])
        
        all_bib = ""
        all_intext = ""

        with tab_bib:
            for i, r in enumerate(st.session_state.refs, 1):
                if style == "Vancouver": cite = f"{i}. {r['author']}. {r['title']}. {r['year']}. {r['url']}"
                elif style == "APA 7th": cite = f"{r['author']} ({r['year']}). {r['title']}. {r['url']}"
                else: cite = f"[{i}] {r['author']}, \"{r['title']}\", {r['year']}. {r['url']}"
                
                st.code(cite)
                all_bib += cite + "\n\n"
        
        with tab_intext:
            for i, r in enumerate(st.session_state.refs, 1):
                intext = f"({i})" if style == "Vancouver" else f"({r['author']}, {r['year']})"
                st.markdown(f"**{r['title'][:50]}...**")
                st.markdown(f'<div class="intext-box">{intext}</div>', unsafe_allow_html=True)
                all_intext += intext + " "

        st.divider()
        st.download_button("📥 Kaynakçayı İndir", data=all_bib, file_name="kaynakca.txt", use_container_width=True)
        if st.button("🗑️ Tümünü Sil", use_container_width=True):
            st.session_state.refs = []
            st.rerun()
    else:
        st.info("Henüz kaynak eklenmedi.")
