import streamlit as st
import requests
import re
from datetime import datetime
import fitz  # PyMuPDF
import urllib.parse

# 1. SAYFA VE DİL YAPILANDIRMASI
st.set_page_config(page_title="Citemate Ultimate v10", page_icon="🎓", layout="wide")

# Dil Sözlüğü
languages = {
    "Türkçe": {
        "welcome": "Hoş Geldiniz!",
        "tutorial_title": "📖 Nasıl Kullanılır?",
        "tutorial_text": "1. Kaynak ekle (DOI/Başlık/PDF). 2. Format seç. 3. Atıfı kopyala. 4. Listeyi paylaş.",
        "tab_doi": "🔗 DOI/Link",
        "tab_search": "🔍 Başlık",
        "tab_pdf": "📄 PDF",
        "add_btn": "➕ Kaynak Ekle",
        "cite_style": "📌 Atıf Formatı Seçin:",
        "share_text": "Sistemi Paylaş",
        "share_results": "📋 Kaynakçayı Paylaş",
        "wa_share": "WhatsApp ile Gönder",
        "mail_share": "E-posta ile Gönder",
        "confirm_btn": "✅ Evet, Doğru",
        "cancel_btn": "❌ Hayır, Yanlış",
        "footer_msg": "Dünya standartlarında akademik araç."
    },
    "English": {
        "welcome": "Welcome!",
        "tutorial_title": "📖 How to Use?",
        "tutorial_text": "1. Add source (DOI/Title/PDF). 2. Select format. 3. Copy citation. 4. Share list.",
        "tab_doi": "🔗 DOI/Link",
        "tab_search": "🔍 Title",
        "tab_pdf": "📄 PDF",
        "add_btn": "➕ Add Source",
        "cite_style": "📌 Select Citation Style:",
        "share_text": "Share Citemate",
        "share_results": "📋 Share Bibliography",
        "wa_share": "Send via WhatsApp",
        "mail_share": "Send via Email",
        "confirm_btn": "✅ Yes, Correct",
        "cancel_btn": "❌ No, Wrong",
        "footer_msg": "World-class academic tool."
    }
}

# Sidebar: Tek bir dil seçici (Çakışmayı önlemek için benzersiz key)
selected_lang = st.sidebar.selectbox("🌐 Dil / Language", list(languages.keys()), key="global_lang_selector")
L = languages[selected_lang]

# 2. GÖRSEL TASARIM (Yüksek Okunabilirlik)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1, h2, h3, p, span, label { color: white !important; }
    .stTextInput input { border: 1px solid #34d399 !important; color: white !important; background-color: #262730 !important; }
    .intext-box { background-color: #002b36; color: #93a1a1; padding: 10px; border-radius: 5px; border-left: 5px solid #268bd2; font-family: monospace; }
    .result-box { background-color: #1a1a1a; padding: 20px; border: 2px solid #34d399; border-radius: 10px; margin: 15px 0; }
    .share-wa { background-color: #25D366; color: white !important; padding: 10px; border-radius: 5px; text-decoration: none; font-weight: bold; display: block; text-align: center; }
    .share-mail { background-color: #EA4335; color: white !important; padding: 10px; border-radius: 5px; text-decoration: none; font-weight: bold; display: block; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 3. SESSION STATE
if 'refs' not in st.session_state: st.session_state.refs = []
if 'temp_search' not in st.session_state: st.session_state.temp_search = None

# 4. FONKSİYONLAR
def fetch_academic_data(query, is_doi=False):
    url = f"https://api.crossref.org/works/{query}" if is_doi else f"https://api.crossref.org/works?query={query}&rows=1"
    try:
        res = requests.get(url, timeout=12, headers={'User-Agent': 'Citemate/1.0'})
        if res.status_code == 200:
            data = res.json().get('message', {})
            item = data['items'][0] if 'items' in data else data
            title = item.get('title', ['Başlık Yok'])[0]
            authors = item.get('author', [])
            auth_str = authors[0].get('family') or "Anonim"
            if len(authors) > 1: auth_str += " et al."
            year = datetime.now().year
            try: year = item.get('created', {}).get('date-parts', [[year]])[0][0]
            except: pass
            doi_link = f"https://doi.org/{item.get('DOI')}" if item.get('DOI') else item.get('URL', 'Link Yok')
            return {"title": str(title), "author": str(auth_str), "year": str(year), "url": str(doi_link)}
    except: return None
    return None

def process_pdf(file_bytes, filename):
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = "".join([doc[i].get_text() for i in range(min(len(doc), 2))])
        doi_match = re.search(r'10\.\d{4,}/[^\s\)]+', text, re.I)
        if doi_match:
            return fetch_academic_data(doi_match.group().strip("/"), is_doi=True)
        return {"title": filename, "author": "PDF", "year": "2026", "url": filename}
    except: return None

# 5. ARAYÜZ ÜST (REHBER VE PAYLAŞ)
col_t, col_s = st.columns([8, 2])
with col_t:
    st.title("🎓 Citemate Pro v10.0")
    with st.expander(L["tutorial_title"]): st.info(L["tutorial_text"])

with col_s:
    # Siteyi paylaş butonu
    encoded_site = urllib.parse.quote(f"Citemate: {L['footer_msg']} https://citemate.streamlit.app")
    st.markdown(f'<br><a href="https://api.whatsapp.com/send?text={encoded_site}" target="_blank" class="share-wa">📲 {L["share_text"]}</a>', unsafe_allow_html=True)

style = st.selectbox(L["cite_style"], ["Vancouver", "APA 7th", "IEEE", "MLA 9th", "Harvard"], key="style_sel")

st.divider()

# 6. GİRİŞ VE ÇIKTI
col_in, col_out = st.columns([4, 6], gap="large")

with col_in:
    st.header(L["welcome"])
    t_doi, t_search, t_pdf = st.tabs([L["tab_doi"], L["tab_search"], L["tab_pdf"]])
    
    with t_doi:
        u_in = st.text_input("DOI / URL:", key="doi_input_v10")
        if st.button(L["add_btn"], key="add_btn_doi"):
            dm = re.search(r'10\.\d{4,}/[^\s\)]+', u_in, re.I)
            if dm:
                res = fetch_academic_data(dm.group().strip("/"), is_doi=True)
                if res: st.session_state.refs.append(res); st.rerun()
            else:
                st.session_state.refs.append({"title": u_in, "author": "Web", "year": "2026", "url": u_in})
                st.rerun()

    with t_search:
        title_q = st.text_input(L["tab_search"] + ":", key="search_title_v10")
        if st.button("🔍 Search", key="btn_search_v10"):
            res = fetch_academic_data(title_q)
            if res: st.session_state.temp_search = res
            else: st.error("Not found.")
        
        if st.session_state.temp_search:
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.write(f"**{st.session_state.temp_search['title']}**")
            st.write(f"{st.session_state.temp_search['author']} ({st.session_state.temp_search['year']})")
            st.markdown('</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1: 
                if st.button(L["confirm_btn"], key="confirm_v10"):
                    st.session_state.refs.append(st.session_state.temp_search)
                    st.session_state.temp_search = None; st.rerun()
            with c2:
                if st.button(L["cancel_btn"], key="cancel_v10"):
                    st.session_state.temp_search = None; st.rerun()

    with t_pdf:
        pf = st.file_uploader(L["tab_pdf"], type="pdf", key="pdf_up_v10")
        if pf and st.button("📄 Analyze PDF", key="btn_pdf_v10"):
            res = process_pdf(pf.read(), pf.name)
            if res: st.session_state.refs.append(res); st.rerun()

with col_out:
    st.header("📋 Results")
    if st.session_state.refs:
        all_txt = ""
        tab_list, tab_intext = st.tabs(["📋 Bibliography", "🖋️ In-text"])
        
        with tab_list:
            for i, r in enumerate(st.session_state.refs, 1):
                if style == "Vancouver": cite = f"{i}. {r['author']}. {r['title']}. {r['year']}. {r['url']}"
                elif style == "APA 7th": cite = f"{r['author']} ({r['year']}). {r['title']}. {r['url']}"
                else: cite = f"[{i}] {r['author']}, \"{r['title']}\", {r['year']}. {r['url']}"
                st.code(cite)
                all_txt += cite + "\n\n"
        
        with tab_intext:
            for i, r in enumerate(st.session_state.refs, 1):
                intext = f"({i})" if style == "Vancouver" else f"({r['author']}, {r['year']})"
                st.markdown(f'<div class="intext-box">{intext}</div>', unsafe_allow_html=True)

        st.divider()
        st.subheader(L["share_results"])
        encoded_res = urllib.parse.quote(f"{selected_lang} {style} Bibliography:\n\n" + all_txt)
        col_w, col_m = st.columns(2)
        with col_w: st.markdown(f'<a href="https://api.whatsapp.com/send?text={encoded_res}" target="_blank" class="share-wa">🟢 WhatsApp</a>', unsafe_allow_html=True)
        with col_m: st.markdown(f'<a href="mailto:?subject=Bibliography&body={encoded_res}" class="share-mail">🔴 Email</a>', unsafe_allow_html=True)
        
        if st.button("🗑️ Clear All", key="clear_all_v10"): st.session_state.refs = []; st.rerun()
    else: st.info("No sources.")

st.markdown(f"--- \n<center><i>{L['footer_msg']}</i></center>", unsafe_allow_html=True)
