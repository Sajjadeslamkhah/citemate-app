import streamlit as st
import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import urllib.parse

# 1. SAYFA VE DİL YAPILANDIRMASI
st.set_page_config(page_title="Citemate Pro v10.3", page_icon="🎓", layout="wide")

languages = {
    "Türkçe": {
        "welcome": "Hoş Geldiniz!",
        "tutorial_title": "📖 Nasıl Kullanılır?",
        "tutorial_text": "1. DOI, Başlık veya PDF ekleyin. 2. Format seçin. 3. Kaynakçayı kopyalayın veya Paylaşın.",
        "tab_doi": "🔗 DOI/Link",
        "tab_search": "🔍 Başlık",
        "tab_pdf": "📄 PDF",
        "add_btn": "➕ Kaynak Ekle",
        "cite_style": "📌 Atıf Formatı Seçin:",
        "share_results": "📋 Kaynakçayı Paylaş",
        "wa_share": "WhatsApp",
        "mail_share": "E-posta",
        "confirm_btn": "✅ Evet, Doğru",
        "cancel_btn": "❌ Hayır, Yanlış",
        "footer_msg": "Dünya standartlarında akademik araç."
    },
    "English": {
        "welcome": "Welcome!",
        "tutorial_title": "📖 How to Use?",
        "tutorial_text": "1. Add DOI, Title or PDF. 2. Select format. 3. Copy bibliography or Share.",
        "tab_doi": "🔗 DOI/Link",
        "tab_search": "🔍 Title",
        "tab_pdf": "📄 PDF",
        "add_btn": "➕ Add Source",
        "cite_style": "📌 Select Citation Style:",
        "share_results": "📋 Share Bibliography",
        "wa_share": "WhatsApp",
        "mail_share": "Email",
        "confirm_btn": "✅ Yes, Correct",
        "cancel_btn": "❌ No, Wrong",
        "footer_msg": "World-class academic tool."
    }
}

selected_lang = st.sidebar.selectbox("🌐 Dil / Language", list(languages.keys()), key="lang_v103")
L = languages[selected_lang]

# 2. GÖRSEL TASARIM
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1, h2, h3, p, span, label { color: white !important; }
    .stTextInput input { border: 1px solid #34d399 !important; color: white !important; background-color: #262730 !important; }
    .intext-box { background-color: #002b36; color: #93a1a1; padding: 10px; border-radius: 5px; border-left: 5px solid #268bd2; font-family: monospace; margin: 5px 0; }
    .result-box { background-color: #1a1a1a; padding: 20px; border: 2px solid #34d399; border-radius: 10px; margin: 15px 0; }
    .share-wa { background-color: #075E54; color: white !important; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; display: block; text-align: center; border: 1px solid #128C7E; }
    .share-mail { background-color: #2c3e50; color: white !important; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; display: block; text-align: center; border: 1px solid #34495e; }
    </style>
    """, unsafe_allow_html=True)

if 'refs' not in st.session_state: st.session_state.refs = []
if 'temp_search' not in st.session_state: st.session_state.temp_search = None

# 3. GELİŞMİŞ AKADEMİK TEŞHİS MOTORU (Ultra-Precision DOI & Date)
def fetch_academic_data(query, is_doi=False):
    # KRİTİK: Parantez içeren DOI'ler için geliştirilmiş regex
    # Bu regex artık '10.1016/S0720-048X(02)00168-7' gibi yapıları tam yakalar.
    doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
    doi_match = re.search(doi_pattern, query, re.I)
    doi = doi_match.group().strip("/") if doi_match else query

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        url = f"https://api.crossref.org/works/{doi}" if is_doi else f"https://api.crossref.org/works?query={query}&rows=1"
        res = requests.get(url, timeout=12, headers=headers)
        if res.status_code == 200:
            data = res.json().get('message', {})
            item = data['items'][0] if 'items' in data else data
            
            title = item.get('title', [''])[0]
            if not title: return None
            
            # Yazarlar
            authors = item.get('author', [])
            auth_str = authors[0].get('family') or authors[0].get('literal') or "Anonim"
            if len(authors) > 1: auth_str += " et al."
            
            # Tarih Dedektifi (En doğru yılı bulana kadar tarar)
            year = "2026"
            date_fields = ['published-print', 'published-online', 'issued', 'created', 'indexed']
            for field in date_fields:
                if field in item and item[field].get('date-parts'):
                    potential_year = item[field]['date-parts'][0][0]
                    if potential_year:
                        year = str(potential_year)
                        break
            
            return {"title": str(title), "author": str(auth_str), "year": year, "url": f"https://doi.org/{doi}" if is_doi else item.get('URL', query)}
    except: pass

    # API başarısızsa Scraping (Fallback)
    if is_doi:
        try:
            web_res = requests.get(f"https://doi.org/{doi}", timeout=10, headers=headers)
            soup = BeautifulSoup(web_res.text, 'html.parser')
            title_tag = (soup.find("meta", attrs={"name": "citation_title"}) or soup.find("meta", property="og:title") or soup.title)
            title_text = title_tag["content"] if hasattr(title_tag, "content") else (title_tag.string if title_tag else None)
            year_tag = (soup.find("meta", attrs={"name": "citation_publication_date"}) or soup.find("meta", attrs={"name": "citation_date"}))
            year_val = re.search(r'\d{4}', year_tag["content"]).group() if year_tag else "2026"
            if title_text:
                return {"title": title_text.strip(), "author": "Academic Source", "year": year_val, "url": f"https://doi.org/{doi}"}
        except: pass
        
    return None

def process_pdf(file_bytes, filename):
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = "".join([doc[i].get_text() for i in range(min(len(doc), 2))])
        doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
        doi_match = re.search(doi_pattern, text, re.I)
        if doi_match:
            return fetch_academic_data(doi_match.group().strip("/"), is_doi=True)
        lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 15]
        return {"title": lines[0] if lines else filename, "author": "PDF", "year": "2026", "url": filename}
    except: return None

# 4. ARAYÜZ
st.title("🎓 Citemate Pro v10.3")
with st.expander(L["tutorial_title"]): st.info(L["tutorial_text"])

style = st.selectbox(L["cite_style"], ["Vancouver", "APA 7th", "IEEE", "MLA 9th", "Harvard"], key="style_v103")
st.divider()

col_in, col_out = st.columns([4, 6], gap="large")

with col_in:
    st.header(L["welcome"])
    t_doi, t_search, t_pdf = st.tabs([L["tab_doi"], L["tab_search"], L["tab_pdf"]])
    
    with t_doi:
        doi_in = st.text_input("DOI / URL:", key="doi_v103", placeholder="10.1016/S0720-048X(02)00168-7")
        if st.button(L["add_btn"], key="btn_doi_v103"):
            if doi_in.strip():
                with st.spinner("Analyzing..."):
                    res = fetch_academic_data(doi_in, is_doi=True)
                    if res:
                        st.session_state.refs.append(res); st.success("Found!"); st.rerun()
                    else:
                        st.session_state.refs.append({"title": doi_in, "author": "Web", "year": "2026", "url": doi_in})
                        st.warning("Details not found, added as raw link.")
                        st.rerun()

    with t_search:
        title_q = st.text_input(L["tab_search"] + ":", key="q_v103")
        if st.button("🔍 Search", key="btn_search_v103"):
            if title_q.strip():
                with st.spinner("Searching..."):
                    res = fetch_academic_data(title_q, is_doi=False)
                    if res: st.session_state.temp_search = res
                    else: st.error("Not found.")
        
        if st.session_state.temp_search:
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.write(f"**{st.session_state.temp_search['title']}**")
            st.write(f"{st.session_state.temp_search['author']} ({st.session_state.temp_search['year']})")
            st.markdown('</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1: 
                if st.button(L["confirm_btn"], key="conf_v103"):
                    st.session_state.refs.append(st.session_state.temp_search)
                    st.session_state.temp_search = None; st.rerun()
            with c2:
                if st.button(L["cancel_btn"], key="canc_v103"):
                    st.session_state.temp_search = None; st.rerun()

    with t_pdf:
        pf = st.file_uploader(L["tab_pdf"], type="pdf", key="up_v103")
        if pf and st.button("📄 Analyze PDF", key="btn_pdf_v103"):
            res = process_pdf(pf.read(), pf.name)
            if res: st.session_state.refs.append(res); st.rerun()

with col_out:
    st.header("📋 Results")
    if st.session_state.refs:
        all_bib_text = ""
        tab_list, tab_intext = st.tabs(["📋 Bibliography", "🖋️ In-text"])
        
        with tab_list:
            for i, r in enumerate(st.session_state.refs, 1):
                auth, titl, yr, link = r.get('author'), r.get('title'), r.get('year'), r.get('url')
                if style == "Vancouver": cite = f"{i}. {auth}. {titl}. {yr}. {link}"
                elif style == "APA 7th": cite = f"{auth} ({yr}). {titl}. {link}"
                else: cite = f"[{i}] {auth}, \"{titl}\", {yr}. {link}"
                st.code(cite)
                all_bib_text += cite + "\n\n"
        
        with tab_intext:
            for i, r in enumerate(st.session_state.refs, 1):
                intext = f"({i})" if style == "Vancouver" else f"({r.get('author')}, {r.get('year')})"
                st.markdown(f'<div class="intext-box">{intext} ({r.get("title")[:30]}...)</div>', unsafe_allow_html=True)

        st.divider()
        st.subheader(L["share_results"])
        encoded_res = urllib.parse.quote(f"Citemate Bibliography ({style}):\n\n" + all_bib_text)
        col_w, col_m = st.columns(2)
        with col_w: st.markdown(f'<a href="https://api.whatsapp.com/send?text={encoded_res}" target="_blank" class="share-wa">{L["wa_share"]}</a>', unsafe_allow_html=True)
        with col_m: st.markdown(f'<a href="mailto:?subject=Bibliography&body={encoded_res}" class="share-mail">{L["mail_share"]}</a>', unsafe_allow_html=True)
        
        if st.button("🗑️ Clear All", key="clear_v103"): st.session_state.refs = []; st.rerun()
    else: st.info("No sources.")

st.markdown(f"--- \n<center><i>{L['footer_msg']}</i></center>", unsafe_allow_html=True)
