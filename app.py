import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(page_title="Citemate Pro v6", page_icon="🎓", layout="wide")

# 2. GELİŞMİŞ GÖRSEL AYARLAR (Okunabilirlik Odaklı)
st.markdown("""
    <style>
    h1, h2, h3, p, span, label { color: #ffffff !important; }
    .stTabs [data-baseweb="tab-list"] button { color: white; font-size: 16px; }
    .cite-card {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #34d399;
        margin-bottom: 10px;
    }
    .copy-area {
        background-color: #000000;
        color: #10b981 !important;
        padding: 15px;
        border-radius: 8px;
        border: 1px dashed #10b981;
        font-family: monospace;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. HAFIZA YÖNETİMİ
if 'refs' not in st.session_state: st.session_state.refs = []

# 4. YARDIMCI FONKSİYONLAR
def get_metadata(url):
    try:
        res = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup.title.string.strip() if soup.title else "Bilinmeyen Kaynak"
    except: return "Web Kaynağı"

def format_cite(ref, style, idx):
    title = ref['title']
    url = ref['url']
    date = ref['year']
    access = ref['access']
    
    if style == "Vancouver":
        return f"({idx}) {title}. Available at: {url} (Accessed: {access})"
    elif style == "APA 7th":
        return f"{title}. ({date}). Retrieved from {url}"
    elif style == "MLA 9th":
        return f'"{title}." {date}, {url}. Accessed {access}.'
    elif style == "Harvard":
        return f"{title} ({date}). Available at: {url} [Accessed {access}]."
    elif style == "IEEE":
        return f"[{idx}] {title}, {date}. [Online]. Available: {url}"
    elif style == "Chicago":
        return f"{title}. {date}. {url} (accessed {access})."
    return title

# 5. ARAYÜZ
st.title("🎓 Citemate Pro v6")
st.subheader("Gelişmiş Akademik Atıf Yönetimi")

# FORMAT SEÇİCİ (Tüm meşhur formatlar)
all_styles = ["Vancouver", "APA 7th", "MLA 9th", "Harvard", "IEEE", "Chicago"]
selected_style = st.selectbox("Atıf Formatını Seçin:", all_styles)

st.divider()

col_in, col_out = st.columns([1, 1], gap="large")

with col_in:
    st.header("📥 Kaynak Ekle")
    
    tab_link, tab_file = st.tabs(["🔗 Link ile Ekle", "📂 Cihazdan PDF Ekle"])
    
    with tab_link:
        link_input = st.text_input("URL / DOI Adresi:", placeholder="https://...")
        if st.button("Kaynağı Listeye Ekle", type="primary"):
            if link_input and not any(r['url'] == link_input for r in st.session_state.refs):
                with st.spinner('Bilgiler çekiliyor...'):
                    t = get_metadata(link_input)
                    st.session_state.refs.append({
                        "url": link_input, "title": t, "year": datetime.now().year, 
                        "access": datetime.now().strftime("%d.%m.%Y"), "type": "Web"
                    })
                st.success("Eklendi!")
            elif any(r['url'] == link_input for r in st.session_state.refs):
                st.warning("Bu kaynak zaten ekli!")

    with tab_file:
        uploaded_file = st.file_uploader("PDF Dosyası Seçin", type="pdf")
        if uploaded_file is not None:
            if not any(r['url'] == uploaded_file.name for r in st.session_state.refs):
                st.session_state.refs.append({
                    "url": uploaded_file.name, "title": uploaded_file.name.replace(".pdf", ""), 
                    "year": datetime.now().year, "access": datetime.now().strftime("%d.%m.%Y"), "type": "Dosya"
                })
                st.success(f"{uploaded_file.name} listeye eklendi.")

with col_out:
    st.header("📋 Kaynakça Çıktısı")
    
    if st.session_state.refs:
        full_bibliography = ""
        for i, r in enumerate(st.session_state.refs, 1):
            formatted = format_cite(r, selected_style, i)
            full_bibliography += formatted + "\n\n"
            
            with st.container():
                st.markdown(f"**[{i}] {r['title']}**")
                st.code(formatted, language="text")
        
        st.divider()
        st.subheader("📤 Toplu Kopyala")
        st.text_area("Tüm kaynakçayı buradan kopyalayabilirsiniz:", value=full_bibliography, height=200)
        
        if st.button("🗑️ Listeyi Sıfırla"):
            st.session_state.refs = []
            st.rerun()
    else:
        st.info("Henüz kaynak eklenmedi.")

# NASIL KULLANILIR
with st.expander("ℹ️ Yardım ve Kullanım"):
    st.write("""
    - **Link:** Web siteleri veya online makaleler için URL girip ekleyin.
    - **Cihazdan Ekle:** Bilgisayarınızdaki PDF'leri sürükleyip bırakın.
    - **Mükerrer:** Aynı linki/dosyayı sistem iki kez eklemez.
    - **Toplu Kopyalama:** Sağ taraftaki metin alanından tüm listeyi tek seferde alabilirsiniz.
    """)
