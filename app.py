import streamlit as st
import requests
import re
from datetime import datetime
from typing import Optional
import html
from urllib.parse import quote

try:
    import fitz
except ImportError:
    fitz = None

# ==========================================
# LANGUAGE DICTIONARY
# ==========================================

LANGUAGES = {
    "TR": {
        "app_title": "Citemate Pro",
        "sidebar_brand": "Citemate Pro",
        "contact_title": "Bize Ulasin",
        "contact_desc": "Akademik islbirligi icin bize ulasin.",
        "menu_label": "MENU",
        "menu_citation_engine": "Atif Motoru",
        "menu_services": "Hizmetler",
        "format_label": "Format:",
        "tab_doi": "DOI",
        "tab_search": "Arama",
        "tab_pdf": "PDF",
        "doi_label": "DOI:",
        "doi_placeholder": "10.1016/j.cell...",
        "doi_button": "Ekle",
        "search_label": "Baslık:",
        "search_placeholder": "Yayin basligi...",
        "search_button": "Ara",
        "pdf_label": "PDF Yukle",
        "pdf_button": "Yukle",
        "download_button": "Indir",
        "error_empty_input": "Lütfen bilgi girin",
        "error_invalid_doi": "Gecersiz DOI formatı",
        "error_no_results": "Sonuc bulunamadi",
        "error_timeout": "Timeout (10s)",
        "error_connection": "Baglanti hatasi",
        "error_pdf": "PDF hatasi",
        "error_pymupdf": "PyMuPDF gerekli: pip install pymupdf",
        "success_added": "Eklendi!",
        "warning_duplicate": "Bu kaynak zaten var!",
        "searching": "Aranıyor...",
        "reading": "Okunuyor...",
        "delete": "Sil",
        "no_sources": "Kaynak yok",
    },
    "EN": {
        "app_title": "Citemate Pro",
        "sidebar_brand": "Citemate Pro",
        "contact_title": "Contact Us",
        "contact_desc": "Reach out for academic collaboration.",
        "menu_label": "MENU",
        "menu_citation_engine": "Citation Engine",
        "menu_services": "Services",
        "format_label": "Format:",
        "tab_doi": "DOI",
        "tab_search": "Search",
        "tab_pdf": "PDF",
        "doi_label": "DOI:",
        "doi_placeholder": "10.1016/j.cell...",
        "doi_button": "Add",
        "search_label": "Title:",
        "search_placeholder": "Publication title...",
        "search_button": "Search",
        "pdf_label": "Upload PDF",
        "pdf_button": "Upload",
        "download_button": "Download",
        "error_empty_input": "Please provide input",
        "error_invalid_doi": "Invalid DOI format",
        "error_no_results": "No results found",
        "error_timeout": "Timeout (10s)",
        "error_connection": "Connection error",
        "error_pdf": "PDF error",
        "error_pymupdf": "PyMuPDF required: pip install pymupdf",
        "success_added": "Added!",
        "warning_duplicate": "This source already exists!",
        "searching": "Searching...",
        "reading": "Reading...",
        "delete": "Delete",
        "no_sources": "No sources",
    }
}

st.set_page_config(page_title="Citemate Pro", page_icon="🎓", layout="wide")

# ==========================================
# SESSION STATE
# ==========================================

def init_session_state():
    if 'refs' not in st.session_state:
        st.session_state.refs = []
    if 'page' not in st.session_state:
        st.session_state.page = "citation_engine"
    if 'lang' not in st.session_state:
        st.session_state.lang = "TR"

init_session_state()

def get_text(key: str) -> str:
    lang = st.session_state.lang
    if lang not in LANGUAGES:
        lang = "TR"
    return LANGUAGES[lang].get(key, key)

# ==========================================
# STYLING
# ==========================================

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .main-title { font-size: 48px !important; font-weight: 900 !important; color: #34d399; margin-bottom: 10px; }
    .subtitle { color: #94a3b8; font-size: 14px; margin-bottom: 30px; }
    .ref-box { background-color: #161b22; padding: 15px; border-radius: 8px; border-left: 3px solid #34d399; margin: 10px 0; }
    .ref-title { font-weight: bold; color: #e2e8f0; }
    .ref-author { color: #94a3b8; font-size: 13px; }
    .ref-source { color: #64748b; font-size: 12px; font-style: italic; }
    .error-box { background-color: rgba(239, 68, 68, 0.1); border-left: 3px solid #ef4444; color: #fca5a5; padding: 10px; border-radius: 5px; margin: 10px 0; }
    .success-box { background-color: rgba(34, 197, 94, 0.1); border-left: 3px solid #22c55e; color: #86efac; padding: 10px; border-radius: 5px; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def is_valid_doi(doi_str: str) -> bool:
    if not isinstance(doi_str, str):
        return False
    return bool(re.match(r'^10\.\d{4,}/[^\s]+$', doi_str.strip()))

def extract_doi_from_text(text: str) -> Optional[str]:
    if not isinstance(text, str):
        return None
    match = re.search(r'10\.\d{4,}/[^\s\)]+', text, re.I)
    return match.group().strip("/") if match else None

def sanitize(s: str, max_len: int = 300) -> str:
    if not isinstance(s, str):
        return ""
    return html.escape(s.strip())[:max_len]

def get_author(item: dict) -> str:
    try:
        authors = item.get('author', [])
        if not authors:
            return "Anonim"
        author = authors[0].get('family') or authors[0].get('literal', 'Anonim')
        if len(authors) > 1:
            return f"{author} et al."
        return sanitize(str(author))
    except:
        return "Anonim"

def get_year(item: dict) -> str:
    try:
        for key in ['published-online', 'published-print', 'created', 'issued']:
            if key in item and isinstance(item[key], dict):
                parts = item[key].get('date-parts')
                if parts and len(parts) > 0 and len(parts[0]) > 0:
                    year = parts[0][0]
                    if isinstance(year, int) and 1900 < year < 2100:
                        return str(year)
    except:
        pass
    return str(datetime.now().year)

def is_duplicate(new_ref: dict) -> bool:
    for existing in st.session_state.refs:
        if new_ref.get('url', '').lower() == existing.get('url', '').lower():
            return True
        if (new_ref.get('title', '').lower()[:50] == existing.get('title', '').lower()[:50]):
            return True
    return False

def format_citation(ref: dict, style: str, index: int) -> str:
    author = sanitize(str(ref.get('author', 'Anonim')))
    title = sanitize(str(ref.get('title', 'No Title')))
    year = ref.get('year', '2026')
    url = sanitize(str(ref.get('url', '')))
    
    if style == "Vancouver":
        return f"{index}. {author}. {title}. {year}. {url}"
    elif style == "APA 7th":
        return f"{author} ({year}). {title}. {url}"
    elif style == "IEEE":
        return f"[{index}] {author}, \"{title},\" {year}. {url}"
    elif style == "MLA":
        return f"{author}. {title}. {year}. {url}"
    return f"{author} ({year}). {title}."

# ==========================================
# API FUNCTIONS
# ==========================================

def get_cite(query: str, is_doi: bool = False) -> Optional[dict]:
    if not isinstance(query, str) or not query.strip():
        st.markdown(f'<div class="error-box">{get_text("error_empty_input")}</div>', unsafe_allow_html=True)
        return None
    
    query = sanitize(query, max_len=200)
    
    try:
        if is_doi:
            url = f"https://api.crossref.org/works/{quote(query, safe='')}"
        else:
            url = f"https://api.crossref.org/works?query={quote(query, safe='')}&rows=1"
        
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        if 'message' not in data:
            return None
        
        msg = data['message']
        item = msg if is_doi else (msg['items'][0] if msg.get('items') else None)
        
        if not item:
            st.markdown(f'<div class="error-box">{get_text("error_no_results")}</div>', unsafe_allow_html=True)
            return None
        
        title = item.get('title', ['No Title'])
        if isinstance(title, list):
            title = title[0] if title else 'No Title'
        
        return {
            "title": sanitize(str(title), 200),
            "author": get_author(item),
            "year": get_year(item),
            "url": f"https://doi.org/{item['DOI']}" if 'DOI' in item else item.get('URL', ''),
            "source": "Crossref"
        }
    
    except requests.exceptions.Timeout:
        st.markdown(f'<div class="error-box">{get_text("error_timeout")}</div>', unsafe_allow_html=True)
    except requests.exceptions.ConnectionError:
        st.markdown(f'<div class="error-box">{get_text("error_connection")}</div>', unsafe_allow_html=True)
    except Exception:
        st.markdown(f'<div class="error-box">{get_text("error_connection")}</div>', unsafe_allow_html=True)
    
    return None

def process_pdf(file_bytes: bytes, filename: str) -> Optional[dict]:
    if fitz is None:
        st.markdown(f'<div class="error-box">{get_text("error_pymupdf")}</div>', unsafe_allow_html=True)
        return None
    
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = "".join([doc[i].get_text() for i in range(min(len(doc), 3))])
        
        doi = extract_doi_from_text(text)
        if doi and is_valid_doi(doi):
            return get_cite(doi, is_doi=True)
        
        lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 15]
        return {
            "title": sanitize(lines[0] if lines else filename, 200),
            "author": "PDF",
            "year": str(datetime.now().year),
            "url": sanitize(filename),
            "source": "PDF"
        }
    except Exception:
        st.markdown(f'<div class="error-box">{get_text("error_pdf")}</div>', unsafe_allow_html=True)
        return None

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:
    st.title("Citemate Pro")
    
    lang_cols = st.columns(2)
    if lang_cols[0].button("TR", use_container_width=True):
        st.session_state.lang = "TR"
        st.rerun()
    if lang_cols[1].button("EN", use_container_width=True):
        st.session_state.lang = "EN"
        st.rerun()

# ==========================================
# MAIN PAGE
# ==========================================

st.markdown('<p class="main-title">Citemate Pro</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Akademik Atif Yonetimi | Academic Citation Management</p>', unsafe_allow_html=True)

style = st.selectbox(get_text("format_label"), ["Vancouver", "APA 7th", "IEEE", "MLA"], index=0)

t1, t2, t3 = st.tabs([get_text("tab_doi"), get_text("tab_search"), get_text("tab_pdf")])

# ==========================================
# TAB 1: DOI
# ==========================================

with t1:
    col1, col2 = st.columns([3, 1])
    with col1:
        doi_in = st.text_input(get_text("doi_label"), placeholder=get_text("doi_placeholder"), key="doi_input")
    with col2:
        if st.button(get_text("doi_button"), use_container_width=True):
            if not doi_in.strip():
                st.markdown(f'<div class="error-box">{get_text("error_empty_input")}</div>', unsafe_allow_html=True)
            elif not is_valid_doi(doi_in):
                st.markdown(f'<div class="error-box">{get_text("error_invalid_doi")}</div>', unsafe_allow_html=True)
            else:
                with st.spinner(get_text("searching")):
                    res = get_cite(doi_in, is_doi=True)
                    if res:
                        if is_duplicate(res):
                            st.markdown(f'<div class="error-box">{get_text("warning_duplicate")}</div>', unsafe_allow_html=True)
                        else:
                            st.session_state.refs.append(res)
                            st.markdown(f'<div class="success-box">{get_text("success_added")}</div>', unsafe_allow_html=True)
                            st.rerun()

# ==========================================
# TAB 2: SEARCH
# ==========================================

with t2:
    col1, col2 = st.columns([3, 1])
    with col1:
        q_in = st.text_input(get_text("search_label"), placeholder=get_text("search_placeholder"), key="query_input")
    with col2:
        if st.button(get_text("search_button"), use_container_width=True):
            if not q_in.strip():
                st.markdown(f'<div class="error-box">{get_text("error_empty_input")}</div>', unsafe_allow_html=True)
            else:
                with st.spinner(get_text("searching")):
                    res = get_cite(q_in, is_doi=False)
                    if res:
                        if is_duplicate(res):
                            st.markdown(f'<div class="error-box">{get_text("warning_duplicate")}</div>', unsafe_allow_html=True)
                        else:
                            st.session_state.refs.append(res)
                            st.markdown(f'<div class="success-box">{get_text("success_added")}</div>', unsafe_allow_html=True)
                            st.rerun()

# ==========================================
# TAB 3: PDF
# ==========================================

with t3:
    pdf_file = st.file_uploader(get_text("pdf_label"), type="pdf")
    
    if pdf_file:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"📄 {pdf_file.name}")
        with col2:
            if st.button(get_text("pdf_button"), use_container_width=True):
                with st.spinner(get_text("reading")):
                    res = process_pdf(pdf_file.read(), pdf_file.name)
                    if res:
                        if is_duplicate(res):
                            st.markdown(f'<div class="error-box">{get_text("warning_duplicate")}</div>', unsafe_allow_html=True)
                        else:
                            st.session_state.refs.append(res)
                            st.markdown(f'<div class="success-box">{get_text("success_added")}</div>', unsafe_allow_html=True)
                            st.rerun()

# ==========================================
# OUTPUT SECTION
# ==========================================

st.divider()

if len(st.session_state.refs) == 0:
    st.info(f"📌 {get_text('no_sources')}")
else:
    # Bibliography
    bib_output = ""
    for i, ref in enumerate(st.session_state.refs, 1):
        bib_output += format_citation(ref, style, i) + "\n"
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.text_area("Cikti / Output", value=bib_output, height=min(150, len(st.session_state.refs) * 40), disabled=True)
    with col2:
        st.download_button(
            label=get_text("download_button"),
            data=bib_output,
            file_name=f"kaynakca_{style.lower()}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )
    
    # Sources with delete buttons
    st.subheader(f"Kaynaklar / Sources ({len(st.session_state.refs)})")
    
    for idx, ref in enumerate(st.session_state.refs):
        col1, col2 = st.columns([5, 1])
        
        with col1:
            st.markdown(f'<div class="ref-box">', unsafe_allow_html=True)
            st.markdown(f'<div class="ref-title">#{idx+1} - {ref["author"]} ({ref["year"]})</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="ref-title">{ref["title"][:80]}...</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="ref-source">{ref["source"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            if st.button(get_text("delete"), key=f"del_{idx}", use_container_width=True):
                st.session_state.refs.pop(idx)
                st.rerun()
