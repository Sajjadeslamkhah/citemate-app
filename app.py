import streamlit as st

# Sayfa Ayarları
st.set_page_config(layout="wide", page_title="Citemate Pro")

st.title("🔬 Citemate Pro")
st.caption("Akademik Yazım ve Otomatik Atıf Sistemi")

# Kaynakları hafızada tutmak için (Session State)
if 'references' not in st.session_state:
    st.session_state.references = []

# EKRAN TASARIMI: Sol (Yazı) - Sağ (Kaynak Yönetimi)
col1, col2 = st.columns([6, 4])

with col1:
    st.subheader("📝 Akademik Editör")
    st.info("İpucu: Atıf eklemek istediğiniz yere [cite] yazın.")
    
    # 1. Ham Metin Giriş Alanı
    raw_text = st.text_area("Makalenizi Buraya Yazın", height=400, placeholder="Gömülü kaninler üzerine yazınız...")
    
    # 2. İşleme Mantığı: [cite] etiketlerini numaralarla değiştir
    processed_text = raw_text
    for i in range(len(st.session_state.references)):
        processed_text = processed_text.replace("[cite]", f"**({i+1})**", 1)
    
    st.divider()
    
    # 3. NİHAİ METİN ALANI (Burada atıflar ekli görünür)
    st.subheader("📄 Nihai Makale (Atıflar Eklenmiş)")
    if raw_text:
        st.markdown(processed_text)
    else:
        st.write("Editöre yazı yazdığınızda atıflar burada işlenecek.")

with col2:
    st.subheader("📚 Kaynak Yönetimi")
    
    # Format Seçimi ve Link Girişi
    with st.container():
        st.write("📥 **Yeni Kaynak Tanımla**")
        citation_format = st.selectbox("Atıf Formatı Seçin", ["Vancouver (Sayısal)", "APA", "Harvard", "MLA"])
        new_url = st.text_input("Link veya DOI yapıştırın", key="new_ref_input")
        
        if st.button("Kaynağı Listeye Ekle"):
            if new_url:
                st.session_state.references.append({"url": new_url, "format": citation_format})
                st.rerun() # Sayfayı anında günceller
            else:
                st.warning("Lütfen bir link giriniz.")

    st.divider()
    
    # 4. KAYNAKÇA LİSTESİ
    st.subheader("📖 Kaynakça (References)")
    if st.session_state.references:
        for idx, ref in enumerate(st.session_state.references):
            st.markdown(f"**({idx+1})** {ref['url']} — *[{ref['format']}]*")
        
        if st.button("Kütüphaneyi Temizle"):
            st.session_state.references = []
            st.rerun()
    else:
        st.info("Henüz kaynak eklenmedi. Metne [cite] ekleyip buradan kaynağı tanımlayın.")
