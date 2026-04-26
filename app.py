import streamlit as st
import requests
import re
from datetime import datetime
import fitz  # PyMuPDF
import urllib.parse

# 1. SAYFA AYARLARI VE DİL SÖZLÜĞÜ
st.set_page_config(page_title="Citemate Ultimate v9.8", page_icon="🎓", layout="wide")

languages = {
    "Türkçe": {
        "welcome": "Hoş Geldiniz!",
        "sidebar_lang": "🌐 Dil Seçimi",
        "tutorial_title": "📖 Nasıl Kullanılır?",
        "tutorial_text": """
        1. **Kaynak Ekle:** DOI, Başlık veya PDF yükleyerek kaynaklarınızı sisteme tanıtın.
        2. **Format Seç:** Atıf stilinizi (Vancouver, APA vb.) yukarıdaki menüden belirleyin.
        3. **Kopyala:** Oluşan atıf kodunu tıklayarak doğrudan tezinize yapıştırın.
        4. **Paylaş:** Sitenin linkini arkadaşlarınızla paylaşmak için sağdaki butonu kullanın.
        """,
        "tab_doi": "🔗 DOI/Link",
        "tab_search": "🔍 Başlık",
        "tab_pdf": "📄 PDF",
        "add_btn": "➕ Kaynak Ekle",
        "cite_style": "📌 Atıf Formatı Seçin:",
        "share_text": "Citemate'i Paylaş",
        "footer_msg": "Dünya standartlarında akademik araç.",
        "confirm_btn": "✅ Evet, Doğru",
        "cancel_btn": "❌ Hayır, Yanlış"
    },
    "English": {
        "welcome": "Welcome!",
        "sidebar_lang": "🌐 Language Selection",
        "tutorial_title": "📖 How to Use?",
        "tutorial_text": """
        1. **Add Source:** Use DOI, Title, or PDF upload to add your references.
        2. **Select Format:** Choose your citation style (Vancouver, APA, etc.).
        3. **Copy:** Click and copy the generated code directly into your thesis.
        4. **Share:** Use the share button to recommend Citemate to colleagues.
        """,
        "tab_doi": "🔗 DOI/Link",
        "tab_search": "🔍 Search Title",
        "tab_pdf": "📄 PDF",
        "add_btn": "➕ Add Source",
        "cite_style": "📌 Select Citation Style:",
        "share_text": "Share Citemate",
        "footer_msg": "World-class academic tool.",
        "confirm_btn": "✅ Yes, Correct",
        "cancel_btn": "❌ No, Wrong"
    }
}

# Yan menüde dil seçimi
selected_lang = st.sidebar.selectbox("🌐 Language / Dil", list(languages.keys()))
L = languages[selected_lang]

# 2. ÖZEL CSS (TASARIM)
st.markdown(f"""
    <style>
    .main {{ background-color: #0e1117; }}
    h1, h2, h3, p, span, label {{ color: #ffffff !important; }}
    .stTextInput input {{ border: 1px solid #34d399 !important; color: white !important; background-color: #262730 !important; }}
    .share-btn {{
        background-color: #25D366; color: white !important; padding: 10px 20px;
        border-radius: 20px; text-decoration: none; font-weight: bold; display: inline-block;
    }}
    .tutorial-box {{
        background-color: #1a1a1a; border-left: 5px solid #34d399;
        padding: 15px; border-radius: 5px; margin-bottom: 20px;
    }}
    .result-box {{ background-color: #1a1a1a; padding: 20px; border: 2px solid #34d399; border-radius: 10px; margin: 15px 0; }}
    </style>
    """, unsafe_allow_html=True)

# 3. HAFIZA VE FONKSİYONLAR
if 'refs' not in st.session_state: st.session_state.refs = []
if 'temp_search' not in st.session_state: st.session_state.temp_search = None

def fetch_academic_data(query, is_doi=False):
    url = f"https://api.crossref.org/works/{query}" if is_doi else f"https://api.crossref.org/works?query={query}&rows=1"
    headers = {'User-Agent': 'CitemateGlobal/1.0'}
    try:
        res = requests.get(url, headers=headers, timeout=12)
        if res.status_code == 200:
            data = res.json().get('message', {})
            item = data['items'][0] if 'items' in data else data
            title = item.get('title', ['No Title'])[0]
            authors = item.get('author', [])
            author_str = authors[0].get('family') or authors[0].get('literal') or "Anonim"
            if len(authors) > 1: author_str += " et al."
            try: year = item.get('created', {}).get('date-parts', [[2026]])[0][0]
            except: year = datetime.now().year
            doi_link = f"https://doi.org/{item.get('DOI')}" if item.get('DOI') else item.get('URL', 'No Link')
            return {"title": str(title), "author": str(author_str), "year": str(year), "url": str(doi_link)}
    except: return None
    return None

def process_pdf(file_bytes, filename):
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = "".join([doc[i].get_text() for i in range(min(len(doc), 2))])
        doi_match = re.search(r'10\.\d{4,}/[^\s\)]+', text, re.I)
        if doi_match:
            return fetch_academic_data(doi_match.group().strip("/"), is_doi=True)
        lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 10]
        return {"title": lines[0] if lines else filename, "author": "PDF", "year": "2026", "url": filename}
    except: return None

# 4. ARAYÜZ ÜST KISIM (EĞİTİM VE PAYLAŞ BUTONU)
col_title, col_share = st.columns([8, 2])
with col_title:
    st.title(f"🎓 Citemate Ultimate v9.8")
    with st.expander(L["tutorial_title"]):
        st.markdown(f'<div class="tutorial-box">{L["tutorial_text"]}</div>', unsafe_allow_html=True)

with col_share:
    share_url = "https://citemate.streamlit.app"
    whatsapp_url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(L['share_text'] + ': ' + share_url)}"
    st.markdown(f'<br><a href="{whatsapp_url}" target="_blank" class="share-btn">📲 {L["share_text"]}</a>', unsafe_allow_html=True)

# 5. ANA İŞLEMLER
style = st.selectbox(L["cite_style"], ["Vancouver", "APA 7th", "IEEE", "MLA 9th", "Harvard"])

col_in, col_out = st.columns([4, 6], gap="large")

with col_in:
    st.header(L["welcome"])
    t_doi, t_search, t_pdf = st.tabs([L["tab_doi"], L["tab_search"], L["tab_pdf"]])
    
    with t_doi:
        url_in = st.text_input("DOI / URL:", key="doi_input")
        if st.button(L["add_btn"], key="add_doi_btn"):
            doi_match = re.search(r'10\.\d{4,}/[^\s\)]+', url_in, re.I)
            if doi_match:
                with st.spinner("AI analyzing..."):
                    res = fetch_academic_data(doi_match.group().strip("/"), is_doi=True)
                    if res: st.session_state.refs.append(res); st.rerun()
            else:
                st.session_state.refs.append({"title": url_in, "author": "Web", "year": "2026", "url": url_in})
                st.rerun()

    with t_search:
        title_q = st.text_input(L["tab_search"] + ":", key="search_input")
        if st.button("🔍 " + L["tab_search"]):
            if title_q.strip():
                with st.spinner("Searching..."):
                    res = fetch_academic_data(title_q)
                    if res: st.session_state.temp_search = res
                    else: st.error("No results found.")
        
        if st.session_state.temp_search:
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.write(f"**{st.session_state.temp_search['title']}**")
            st.write(f"{st.session_state.temp_search['author']} ({st.session_state.temp_search['year']})")
            st.markdown('</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button(L["confirm_btn"]):
                    st.session_state.refs.append(st.session_state.temp_search)
                    st.session_state.temp_search = None; st.rerun()
            with c2:
                if st.button(L["cancel_btn"]):
                    st.session_state.temp_search = None; st.rerun()

    with t_pdf:
        pdf_file = st.file_uploader(L["tab_pdf"], type="pdf")
        if pdf_file and st.button("📄 " + L["tab_pdf"] + " Analiz"):
            with st.spinner("Analyzing PDF..."):
                res = process_pdf(pdf_file.read(), pdf_file.name)
                if res: st.session_state.refs.append(res); st.rerun()

with col_out:
    st.header("📋 " + ("Kaynakça" if selected_lang == "Türkçe" else "Bibliography"))
    if st.session_state.refs:
        tab_list, tab_intext = st.tabs(["📋 List", "🖋️ In-text"])
        all_bib = ""
        with tab_list:
            for i, r in enumerate(st.session_state.refs, 1):
                auth, titl, year, link = r.get('author'), r.get('title'), r.get('year'), r.get('url')
                if style == "Vancouver": cite = f"{i}. {auth}. {titl}. {year}. {link}"
                elif style == "APA 7th": cite = f"{auth} ({year}). {titl}. {link}"
                else: cite = f"[{i}] {auth}, \"{titl}\", {year}. {link}"
                st.code(cite)
                all_bib += cite + "\n\n"
        
        with tab_intext:
            for i, r in enumerate(st.session_state.refs, 1):
                intext = f"({i})" if style == "Vancouver" else f"({r.get('author')}, {r.get('year')})"
                st.markdown(f"**{r.get('title')[:50]}...**")
                st.markdown(f'<div class="intext-box">{intext}</div>', unsafe_allow_html=True)

        st.download_button("📥 TXT", all_bib, "references.txt")
        if st.button("🗑️ " + ("Sıfırla" if selected_lang == "Türkçe" else "Clear")):
            st.session_state.refs = []; st.rerun()
    else: st.info("No sources yet.")

st.markdown(f"--- \n<center>{L['footer_msg']}</center>", unsafe_allow_html=True)
import streamlit as st
import requests
import re
from datetime import datetime
import fitz  # PyMuPDF
import urllib.parse

# 1. SAYFA VE DİL AYARLARI (Genişletilmiş Sözlük)
st.set_page_config(page_title="Citemate Ultimate v9.9", page_icon="🎓", layout="wide")

languages = {
    "Türkçe": {
        "share_results": "📋 Kaynakçayı Paylaş",
        "share_msg": "Hazırladığım Kaynakça Listesi:\n\n",
        "whatsapp_share": "WhatsApp ile Gönder",
        "email_share": "E-posta ile Gönder",
        "footer_msg": "Dünya standartlarında akademik araç.",
        # ... (diğer v9.8 metinleri aynen korunur)
    },
    "English": {
        "share_results": "📋 Share Bibliography",
        "share_msg": "My Bibliography List:\n\n",
        "whatsapp_share": "Send via WhatsApp",
        "email_share": "Send via Email",
        "footer_msg": "World-class academic tool.",
    }
}

selected_lang = st.sidebar.selectbox("🌐 Language / Dil", ["Türkçe", "English"])
L = languages[selected_lang]

# 2. SESSION STATE
if 'refs' not in st.session_state: st.session_state.refs = []

# 3. YARDIMCI FONKSİYONLAR (DOI, PDF, FETCH - Önceki koddan aynen korunur)
# (Kodun bu kısmında değişiklik yok, v9.8 ile aynı fonksiyonları kullanıyoruz)

# 4. ARAYÜZ (GÜNCELLENMİŞ ÇIKTI PANELİ)
style = st.selectbox("📌 Format:", ["Vancouver", "APA 7th", "IEEE", "MLA 9th", "Harvard"])

col_in, col_out = st.columns([4, 6], gap="large")

with col_in:
    st.header("📥 Kaynak Ekle")
    # (Giriş sekmeleri v9.8 ile aynı kalsın)

with col_out:
    st.header("📋 " + ("Kaynakça" if selected_lang == "Türkçe" else "Bibliography"))
    
    if st.session_state.refs:
        all_bib_text = ""
        for i, r in enumerate(st.session_state.refs, 1):
            auth, titl, year, link = r.get('author'), r.get('title'), r.get('year'), r.get('url')
            if style == "Vancouver": cite = f"{i}. {auth}. {titl}. {year}. {link}"
            elif style == "APA 7th": cite = f"{auth} ({year}). {titl}. {link}"
            else: cite = f"[{i}] {auth}, \"{titl}\", {year}. {link}"
            st.code(cite)
            all_bib_text += cite + "\n\n"

        st.divider()
        
        # --- YENİ: SONUÇLARI PAYLAŞMA ALANI ---
        st.subheader(L["share_results"])
        
        # Paylaşılacak metni hazırla
        raw_share_text = L["share_msg"] + all_bib_text
        encoded_text = urllib.parse.quote(raw_share_text)
        
        col_wa, col_mail = st.columns(2)
        
        with col_wa:
            wa_link = f"https://api.whatsapp.com/send?text={encoded_text}"
            st.markdown(f'<a href="{wa_link}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:10px; border-radius:5px; cursor:pointer; font-weight:bold;">🟢 {L["whatsapp_share"]}</button></a>', unsafe_allow_html=True)
            
        with col_mail:
            subject = urllib.parse.quote("Akademik Kaynakça Listesi")
            mail_link = f"mailto:?subject={subject}&body={encoded_text}"
            st.markdown(f'<a href="{mail_link}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#EA4335; color:white; border:none; padding:10px; border-radius:5px; cursor:pointer; font-weight:bold;">🔴 {L["email_share"]}</button></a>', unsafe_allow_html=True)
        
        st.divider()
        # (İndirme ve temizleme butonları v9.8'den devam eder)
    else:
        st.info("Henüz kaynak yok.")

st.markdown(f"--- \n<center><i>{L['footer_msg']}</i></center>", unsafe_allow_html=True)
