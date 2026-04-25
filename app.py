import streamlit as st
import re

# Sayfa Ayarları
st.set_page_config(layout="wide", page_title="Citemate Pro")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTextArea textarea { font-size: 16px !important; font-family: 'Times New Roman', serif; }
    .reference-item { padding: 8px; border-bottom: 1px solid #ddd; margin-bottom: 5px; }
    </style>
    """, unsafe_content_safe=True)

st.title("🔬 Citemate Pro")
st.caption("Akademik Atıf ve Kaynakça Otomasyonu")

# Kaynakları session_state içinde tutalım
if 'references' not in st.session_state:
    st.session_state.references = []

col1, col2 = st.columns([6, 4])

with col1:
    st.subheader("📝 Akademik Editör")
    st.info("Atıf yapmak istediğiniz yere [cite] yazın.")
    
    # Metin Girişi
    input_text = st.text_area("Makale Metni", 
                            placeholder="Metninizi buraya yazın ve atıf yerlerine [cite] ekleyin...",
                            height=400)
    
    # DİNAMİK DÖNÜŞTÜRME: [cite] yazılarını (1), (2) vb. ile değiştirme
    processed_text = input_text
    count = input_text.count("[cite]")
    
    # Kaynak sayısı kadar [cite] etiketini sırayla değiştir
    for i in range(len(st.session_state.references)):
        processed_text = processed_text.replace("[cite]", f"({i+1})", 1)
    
    st.divider()
    st.subheader("📄 Nihai Metin (Atıflar İşlenmiş)")
    if input_text:
        st.write(processed_text)
    else:
        st.write("Editöre yazı yazdığınızda atıflar burada görünecek.")

with col2:
    st.subheader("📚 Kaynak Yönetimi")
    
    # Yeni Kaynak Ekleme Formu
    with st.form("ref_form", clear_on_submit=True):
        new_ref = st.text_input("Link veya DOI (PubMed, Scholar, vb.)")
        format_choice = st.selectbox("Format", ["Vancouver (Sayısal)", "APA", "Harvard"])
        submit_button = st.form_submit_button("Kaynağı Ekle")
        
        if submit_button:
            if new_ref:
                st.session_state.references.append({"link": new_ref, "format": format_choice})
                st.rerun() # Sayfayı yenileyerek metni günceller
            else:
                st.error("Lütfen bir link girin.")

    st.divider()
    st.subheader("📖 Kaynakça (References)")
    
    if st.session_state.references:
        for idx, ref in enumerate(st.session_state.references):
            st.markdown(f"<div class='reference-item'><b>({idx+1})</b> {ref['link']}</div>", unsafe_allow_html=True)
        
        if st.button("Tümünü Temizle"):
            st.session_state.references = []
            st.rerun()
    else:
        st.info("Henüz kaynak eklenmedi. Metne [cite] ekleyip buradan kaynağı tanımlayın.")
