import streamlit as st
import re
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="Citemate v2.0", page_icon="📚", layout="wide")

# TÜRKÇE ARAYÜZ STİLİ
st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    .stTextArea textarea { font-family: 'Times New Roman', serif; font-size: 17px !important; line-height: 1.6; }
    .ref-box { background: white; padding: 15px; border-radius: 8px; border: 1px solid #eee; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# SESSION STATE
if 'refs' not in st.session_state: st.session_state.refs = []

st.title("🚀 Citemate v2.0")
st.caption("Akademik Yazım ve Otomatik Kaynakça Yönetimi")

# FORMAT SEÇİMİ (v2.0 Yeni Özellik)
format_secimi = st.selectbox(
    "Alıntı Formatı Seçin", 
    ["Vancouver", "APA (Numeric)", "APA (Author-Date)", "Harvard", "MLA", "Chicago"],
    help="Format değiştirildiğinde kaynakça otomatik güncellenir."
)

col_sol, col_sag = st.columns([6, 4])

with col_sol:
    st.subheader("📝 Akademik Editör")
    metin = st.text_area("Yazınızı buraya girin ve [cite] etiketlerini ekleyin:", height=450, placeholder="Örn: Gömülü kaninler anomalidir [cite].")
    
    # DİNAMİK ATIF MOTORU
    islenmis_metin = metin
    for i in range(len(st.session_state.refs)):
        islenmis_metin = islenmis_metin.replace("[cite]", f"**({i+1})**", 1)
    
    st.markdown("### 📄 Canlı Önizleme")
    st.info(islenmis_metin if metin else "Metin girildiğinde atıflar burada görünecek.")

with col_sag:
    st.subheader("📚 Kaynak Yönetimi")
    
    with st.form("kaynak_ekle", clear_on_submit=True):
        url = st.text_input("Kaynak URL / DOI", placeholder="https://doi.org/...")
        ekle_btn = st.form_submit_button("➕ Kaynak Ekle")
        
        if ekle_btn and url:
            yeni_ref = {
                "url": url,
                "tarih": datetime.now().strftime("%Y"),
                "id": len(st.session_state.refs) + 1
            }
            st.session_state.refs.append(yeni_ref)
            st.rerun()

    st.divider()
    st.subheader("📖 Kaynakça (References)")
    
    if st.session_state.refs:
        bib_text = f"**KAYNAKÇA ({format_secimi})**\n\n"
        for idx, r in enumerate(st.session_state.refs):
            ref_satiri = f"({idx+1}) {r['url']} (Erişim: {r['tarih']})"
            st.markdown(f"<div class='ref-box'>{ref_satiri}</div>", unsafe_allow_html=True)
            bib_text += f"{idx+1}. {ref_satiri}\n"
        
        st.download_button("⬇️ Kaynakçayı İndir (TXT)", data=bib_text, file_name="kaynakca.txt")
        
        if st.button("🗑️ Tümünü Temizle"):
            st.session_state.refs = []
            st.rerun()
    else:
        st.write("Henüz kaynak eklenmedi.")
