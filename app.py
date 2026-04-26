import streamlit as st
import requests
import fitz  # PyMuPDF
import re
from datetime import datetime

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Citemate Ultimate v8.7", page_icon="🎓", layout="wide")

# 2. GÖRSEL DÜZENLEMELER
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
    .cite-card { background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #34d399; margin-bottom: 15px; }
    .intext-box { background-color: #002b36; color: #93a1a1; padding: 10px; border-radius: 5px; border-left: 5px solid #268bd2; }
    .guide-step { background-color: #262730; padding: 10px; border-radius: 5px; border-left: 4px solid #ff4b4b; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

if 'refs' not in st.session_state: st.session_state.refs = []
if 'temp_search' not in st.session_state: st.session_state.temp_search = None

# 3. AKILLI FONKSİYONLAR
def fetch_crossref(query, is_doi=False):
    url = f"https://api.crossref.org/works/{query}" if is_doi else f"https://api.crossref.org/works?query={query}&rows=1"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()['message']
            item = data['items'][0] if 'items' in data else data
            title = item.get('title', ['Başlık Bulunamadı'])[0]
            authors = item.get('author', [])
            author_str = authors[0].get('family', 'Anonim') if authors else "Anonim"
            try: year = item.get('created', {}).get('date-parts', [[2026]])[0][0]
            except: year = 2026
            doi = f"https://doi.org/{item.get('DOI', '')}" if item.get('DOI') else "Link Yok"
            return {"title": title, "author": author_str, "year": year, "url": doi}
    except: return None

# 4. ARAYÜZ
st.title("🎓 Citemate Ultimate v8.7")

# --- KULLANIM KILAVUZU SEKİSİ ---
with st.expander("📖 SİTE KULLANIM KILAVUZU (Nasıl Kullanılır?)", expanded=False):
    st.markdown('<div class="guide-step"><b>1. Format Seçin:</b> Sayfanın başındaki menüden akademik formatı (Vancouver, APA vb.) belirleyin.</div>', unsafe_allow_html=True)
    st.markdown('<div class="guide-step"><b>2. Kaynak Ekleyin:</b><br>- <b>Arama:</b> Makale adını yazıp "AI ile Ara" deyin. Sonucu onaylamadan kütüphaneye eklemez.<br>- <b>Link:</b> DOI numarasını veya URL yapıştırın.<br>- <b>PDF:</b> Dosyayı sürükleyin, AI içeriği tarasın.</div>', unsafe_allow_html=True)
    st.markdown('<div class="guide-step"><b>3. Atıfları Alın:</b> Sağ taraftaki "Metin İçi" sekmesinden makale içine yapıştıracağınız (1) veya (Yazar, 2026) kodlarını kopyalayın.</div>', unsafe_allow_html=True)
    st.markdown('<div class="guide-step"><b>4. Dışa Aktar:</b> Tüm liste bittiğinde "Kaynakça İndir" butonuyla Word/LaTeX için hazır listeyi alın.</div>', unsafe_allow_html=True)

style = st.selectbox("Format Seçin:", ["Vancouver", "APA 7th", "IEEE", "MLA 9th", "Harvard"])
st.divider()

col_in, col_out = st.columns([4, 6], gap="large")

with col_in:
    st.header("📥 Kaynak Ekle")
    t_search, t_link, t_pdf = st.tabs(["🔍 Başlık ile Ara", "🔗 DOI / Link", "📄 PDF Yükle"])
    
    with t_search:
        title_q = st.text_input("Makale Adını Yazın:", key="q_search")
        if st.button("AI ile Ara"):
            if len(title_q.strip()) > 5: # Boş veya çok kısa aramayı önle
                with st.spinner("Aranıyor..."):
                    res = fetch_crossref(title_q)
                    if res: st.session_state.temp_search = res
                    else: st.error("Sonuç bulunamadı.")
            else: st.warning("Lütfen geçerli bir başlık girin.")
        
        # ONAY MEKANİZMASI (Yanlış eklemeyi önler)
        if st.session_state.temp_search:
            st.markdown("---")
            st.warning(f"**Bulunan Kaynak:**\n\n{st.session_state.temp_search['title']}")
            if st.button("✅ Bu Doğru, Kütüphaneye Ekle"):
                st.session_state.refs.append(st.session_state.temp_search)
                st.session_state.temp_search = None
                st.rerun()
            if st.button("❌ Yanlış, İptal Et"):
                st.session_state.temp_search = None
                st.rerun()

    with t_link:
        url_in = st.text_input("DOI veya Link:")
        if st.button("Linkten Teşhis Et"):
            if url_in.strip():
                doi_match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', url_in, re.I)
                with st.spinner("Analiz ediliyor..."):
                    res = fetch_crossref(doi_match.group().strip("/"), is_doi=True) if doi_match else {"title": url_in, "author": "Web", "year": 2026, "url": url_in}
                    st.session_state.refs.append(res)
                    st.rerun()

with col_out:
    tab_bib, tab_intext = st.tabs(["📋 Kaynakça", "🖋️ Metin İçi"])
    all_bib = ""
    all_intext = ""

    if st.session_state.refs:
        with tab_bib:
            for i, r in enumerate(st.session_state.refs, 1):
                cite = f"{i}. {r['author']}. {r['title']}. ({r['year']}). {r['url']}" if style == "Vancouver" else f"{r['author']} ({r['year']}). {r['title']}. {r['url']}"
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
        with col_d1: st.download_button("📥 Kaynakçayı İndir", data=all_bib, file_name="kaynakca.txt", use_container_width=True)
        with col_d2: 
            if st.button("🗑️ Tümünü Sil", use_container_width=True):
                st.session_state.refs = []
                st.rerun()
