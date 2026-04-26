import streamlit as st
import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import urllib.parse

# ==========================================
# 1. SAYFA YAPILANDIRMASI & ANALYTICS
# ==========================================
st.set_page_config(page_title="Citemate Pro", page_icon="🎓", layout="wide")

def add_analytics():
    # Google Analytics Ölçüm Kimliğin
    ga_id = "G-90YJBXFY8W" 
    
    # Google Analytics Entegrasyonu
    ga_code = f"""
        <iframe src="https://www.googletagmanager.com/ns.html?id={ga_id}"
                height="0" width="0" style="display:none;visibility:hidden"></iframe>
        <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){{dataLayer.push(arguments);}}
            gtag('js', new Date());
            gtag('config', '{ga_id}');
        </script>
    """
    st.components.v1.html(ga_code, height=0)

# İstatistikleri başlat
add_analytics()

# ==========================================
# 2. HAFIZA VE DİL SİSTEMİ
# ==========================================
if 'lang' not in st.session_state: st.session_state.lang = "Türkçe"
if 'refs' not in st.session_state: st.session_state.refs = []
if 'temp_search' not in st.session_state: st.session_state.temp_search = None

languages = {
    "Türkçe": {
        "welcome": "Hoş Geldiniz!",
        "tutorial_title": "📖 Nasıl Kullanılır?",
        "tutorial_text": "1. DOI, Başlık veya PDF ekleyin. 2. Format seçin. 3. Kaynakçayı kopyalayın veya Paylaşın.",
        "tab_doi": "🔗 DOI/Link", "tab_search": "🔍 Başlık", "tab_pdf": "📄 PDF",
        "add_btn": "➕ Kaynak Ekle", "cite_style": "📌 Atıf Formatı Seçin:",
        "share_results": "📋 Kaynakçayı Paylaş", "download_btn": "📥 Kaynakçayı İndir (.txt)",
        "wa_share": "WhatsApp", "mail_share": "E-posta",
        "confirm_btn": "✅ Evet, Doğru", "cancel_btn": "❌ Hayır, Yanlış",
        "footer_msg": "Citemate.org - Profesyonel akademik atıf aracı."
    },
    "English": {
        "welcome": "Welcome!",
        "tutorial_title": "📖 How to Use?",
        "tutorial_text": "1. Add DOI, Title or PDF. 2. Select format. 3. Copy, Download or Share bibliography.",
        "tab_doi": "🔗 DOI/Link", "tab_search": "🔍 Title", "tab_pdf": "📄 PDF",
        "add_btn": "➕ Add Source", "cite_style": "📌 Select Citation Style:",
        "share_results": "📋 Share Bibliography", "download_btn": "📥 Download Bibliography (.txt)",
        "wa_share": "WhatsApp", "mail_share": "Email",
        "confirm_btn": "✅ Yes, Correct", "cancel_btn": "❌ No, Wrong",
        "footer_msg": "Citemate.org - Professional academic tool."
    }
}

# ==========================================
# 3. TASARIM & ÜST PANEL
# ==========================================
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

col_header, col_lang = st.columns([7, 3])
with col_header:
    st.title("🎓 Citemate Pro")

with col_lang:
    st.write("") 
    c1, c2 = st.columns(2)
    if c1.button("🇹🇷 Türkçe", key="tr_btn"): st.session_state.lang = "Türkçe"; st.rerun()
    if c2.button("🇺🇸 English", key="en_btn"): st.session_state.lang = "English"; st.rerun()

L = languages[st.session_state.lang]

# ==========================================
# 4. VERİ ÇEKME MOTORU
# ==========================================
def fetch_academic_data(query, is_doi=False):
    doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
    doi_match = re.search(doi_pattern, query, re.I)
    doi = doi_match.group().strip("/") if doi_match else query
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        url = f"https://api.crossref.org/works/{doi}" if is_doi else f"https://api.crossref.org/works?query={query}&rows=1"
        res = requests.get(url, timeout=12, headers=headers)
        if res.status_code == 200:
            data = res.json().get('message', {})
            item = data['items'][0] if 'items' in data else data
            title = item.get('title', [''])[0]
            if title:
                authors = item.get('author', [])
                auth_str = authors[0].get('family') or authors[0].get('literal') or "Anonim"
                if len(authors) > 1: auth_str += " et al."
                year = datetime.now().year
                for field in ['published-print', 'published-online', 'issued', 'created']:
                    if field in item and item[field].get('date-parts'):
                        py = item[field]['date-parts'][0][0]
                        if py: year = str(py); break
                return {"title": str(title), "author": str(auth_str), "year": str(year), "url": f"https://doi.org/{doi}"}
    except: pass
    return None

def process_pdf(file_bytes, filename):
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = "".join([doc[i].get_text() for i in range(min(len(doc), 2))])
        doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
        doi_match = re.search(doi_pattern, text, re.I)
        if doi_match: return fetch_academic_data(doi_match.group().strip("/"), is_doi=True)
        lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 15]
        return {"title": lines[0] if lines else filename, "author": "PDF", "year": str(datetime.now().year), "url": filename}
    except: return None

# ==========================================
# 5. ARAYÜZ VE ÇIKTILAR
# ==========================================
with st.expander(L["tutorial_title"]): st.info(L["tutorial_text"])
style = st.selectbox(L["cite_style"], ["Vancouver", "APA 7th", "IEEE", "MLA 9th", "Harvard"], key="style_select")
st.divider()

col_in, col_out = st.columns([4, 6], gap="large")

with col_in:
    st.header(L["welcome"])
    t_doi, t_search, t_pdf = st.tabs([L["tab_doi"], L["tab_search"], L["tab_pdf"]])
    
    with t_doi:
        doi_in = st.text_input("DOI / URL:", key="doi_input")
        if st.button(L["add_btn"], key="add_doi_btn"):
            if doi_in.strip():
                with st.spinner("Analiz ediliyor..."):
                    res = fetch_academic_data(doi_in, is_doi=True)
                    if res: st.session_state.refs.append(res); st.rerun()
                    else:
                        st.session_state.refs.append({"title": doi_in, "author": "Web", "year": str(datetime.now().year), "url": doi_in})
                        st.warning("Link olarak eklendi."); st.rerun()

    with t_search:
        title_q = st.text_input(L["tab_search"] + ":", key="search_input")
        if st.button("🔍 Ara", key="search_btn"):
            res = fetch_academic_data(title_q, is_doi=False)
            if res: st.session_state.temp_search = res
        if st.session_state.temp_search:
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.write(f"**{st.session_state.temp_search['title']}**")
            st.write(f"{st.session_state.temp_search['author']} ({st.session_state.temp_search['year']})")
            st.markdown('</div>', unsafe_allow_html=True)
            cy, cn = st.columns(2)
            if cy.button(L["confirm_btn"], key="confirm_btn"):
                st.session_state.refs.append(st.session_state.temp_search)
                st.session_state.temp_search = None; st.rerun()
            if cn.button(L["cancel_btn"], key="cancel_btn"):
                st.session_state.temp_search = None; st.rerun()

    with t_pdf:
        pf = st.file_uploader(L["tab_pdf"], type="pdf", key="pdf_uploader")
        if pf and st.button("📄 PDF Analiz Et", key="pdf_btn"):
            res = process_pdf(pf.read(), pf.name)
            if res: st.session_state.refs.append(res); st.rerun()

with col_out:
    st.header("📋 Sonuçlar")
    if st.session_state.refs:
        all_txt = ""
        tab_l, tab_i = st.tabs(["📋 Kaynakça", "🖋️ Metin İçi"])
        with tab_l:
            for i, r in enumerate(st.session_state.refs, 1):
                auth, titl, yr, link = r.get('author'), r.get('title'), r.get('year'), r.get('url')
                if style == "Vancouver": cite = f"{i}. {auth}. {titl}. {yr}. {link}"
                elif style == "APA 7th": cite = f"{auth} ({yr}). {titl}. {link}"
                else: cite = f"[{i}] {auth}, \"{titl}\", {yr}. {link}"
                st.code(cite)
                all_txt += cite + "\n\n"
        with tab_i:
            for i, r in enumerate(st.session_state.refs, 1):
                intext = f"({i})" if style == "Vancouver" else f"({r.get('author')}, {r.get('year')})"
                st.markdown(f'<div class="intext-box">{intext} ({r.get("title")[:30]}...)</div>', unsafe_allow_html=True)

        st.divider()
        st.download_button(label=L["download_btn"], data=all_txt, file_name="references.txt", use_container_width=True)
        encoded_res = urllib.parse.quote(f"Citemate Sonuçları:\n\n" + all_txt)
        cw, cm = st.columns(2)
        cw.markdown(f'<a href="https://api.whatsapp.com/send?text={encoded_res}" target="_blank" class="share-wa">{L["wa_share"]}</a>', unsafe_allow_html=True)
        cm.markdown(f'<a href="mailto:?subject=Kaynakça&body={encoded_res}" class="share-mail">{L["mail_share"]}</a>', unsafe_allow_html=True)
        if st.button("🗑️ Tümünü Temizle", key="clear_all_btn", use_container_width=True):
            st.session_state.refs = []; st.rerun()
    else: st.info("Henüz kaynak eklenmedi.")

st.markdown(f"--- \n<center><i>{L['footer_msg']}</i></center>", unsafe_allow_html=True)
