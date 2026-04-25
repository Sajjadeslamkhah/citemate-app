import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(page_title="Citemate Citation Engine", page_icon="📖", layout="centered")

# 2. GÖRSEL TASARIM
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    .cite-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2e7d32;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #333;
    }
    .format-label { font-weight: bold; color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# 3. HAFIZA VE FONKSİYONLAR
if 'refs' not in st.session_state: st.session_state.refs = []

def get_metadata(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else url
        return title.strip()
    except:
        return url

# 4. ARAYÜZ
st.title("📖 Academic Citation Engine")
st.write("Linkleri ekleyin, akademik formatta çıktınızı anında alın.")

# FORMAT SEÇİCİ
selected_format = st.radio(
    "Hedef Formatı Seçin:",
    ["Vancouver (Sayısal)", "APA (Yazar-Tarih)", "MLA", "Harvard"],
    horizontal=True
)

st.divider()

# KAYNAK EKLEME ALANI
with st.container():
    col1, col2 = st.columns([8, 2])
    with col1:
        new_url = st.text_input("Makale, PDF veya Web Linki yapıştırın:", placeholder="https://doi.org/...")
    with col2:
        st.write("##") # Boşluk
        if st.button("Kaynağı Çek", type="primary", use_container_width=True):
            if new_url:
                with st.spinner('Veriler çekiliyor...'):
                    title = get_metadata(new_url)
                    # Mükerrer kontrolü
                    if not any(r['url'] == new_url for r in st.session_state.refs):
                        st.session_state.refs.append({
                            "url": new_url,
                            "title": title,
                            "date": datetime.now().strftime("%Y"),
                            "access_date": datetime.now().strftime("%d.%m.%Y")
                        })
                    else:
                        st.warning("Bu kaynak zaten ekli.")
            else:
                st.error("Lütfen bir link girin.")

st.divider()

# 5. LİSTELEME VE FORMATLAMA
st.subheader("📋 Kaynakça Listesi")

if st.session_state.refs:
    for i, ref in enumerate(st.session_state.refs):
        # Formatlara göre çıktı hazırlama
        if selected_format == "Vancouver (Sayısal)":
            citation = f"({i+1}) {ref['title']}. Available at: {ref['url']} (Accessed: {ref['access_date']})"
        elif selected_format == "APA (Yazar-Tarih)":
            citation = f"{ref['title']}. ({ref['date']}). Retrieved from {ref['url']}"
        else:
            citation = f"{ref['title']}, {ref['url']}, {ref['date']}."

        st.markdown(f"""
            <div class="cite-card">
                {citation}
            </div>
            """, unsafe_allow_html=True)
        st.code(citation, language="text") # Kolay kopyalama için

    if st.button("🗑️ Tüm Listeyi Temizle"):
        st.session_state.refs = []
        st.rerun()
else:
    st.info("Henüz kaynak eklenmedi. Yukarıdaki alana bir link yapıştırarak başlayın.")
