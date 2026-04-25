import streamlit as st
import re

# Sayfa Ayarları
st.set_page_config(layout="wide", page_title="Citemate Pro v1.0")

# Stil Dosyası (Daha profesyonel görünüm için)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTextArea textarea { font-size: 16px !important; font-family: 'Times New Roman', serif; }
    .cite-box { border-left: 5px solid #007bff; padding: 10px; background: #e9ecef; border-radius: 5px; }
    </style>
    """, unsafe_content_safe=True)

st.title("🔬 Citemate Pro")
st.caption("Gelişmiş Akademik Atıf ve Kaynakça Yönetim Sistemi")

# Kaynakları hafızada tutmak için session_state kullanalım
if 'references' not in st.session_state:
    st.session_state.references = []

col1, col2 = st.columns([6, 4])

with col1:
    st.subheader("📝 Akademik Editör")
    st.info("İpucu: Atıf eklemek istediğiniz yere [cite] yazın ve sağ panelden kaynağı yükleyin.")
    
    raw_text = st.text_area("Makale Metni", 
                            placeholder="Gömülü dişler üzerine çalışmanızı buraya yazın...",
                            height=500)
    
    # Otomatik Atıf Dönüştürücü
    processed_text = raw_text
    citation_slots = re.findall(r"\[cite\]", raw_text)
    
    for i, _ in enumerate(citation_slots):
        if i < len(st.session_state.references):
            processed_text = processed_text.replace("[cite]", f"({i+1})", 1)
    
    st.markdown("### 📄 Önizleme (Atıflar Eklenmiş Hali)")
    st.write(processed_text)

with col2:
    st.subheader("📚 Kaynak Yönetimi")
    
    with st.container():
        st.write("📥 **Yeni Kaynak Ekle**")
        new_ref = st.text_input("Link veya DOI (PubMed, Scholar, vb.)", key="ref_input")
        format_choice = st.selectbox("Format", ["APA", "Vancouver", "Harvard"])
        
        if st.button("Kaynağı İşle ve Ekle"):
            if new_ref:
                # Normalde burada PubMed/DOI API'leri çalışır, şimdilik simüle ediyoruz:
                st.session_state.references.append({"link": new_ref, "format": format_choice})
                st.toast("Kaynak başarıyla sıraya eklendi!", icon="✅")
            else:
                st.error("Lütfen geçerli bir kaynak girin.")

    st.divider()
    st.subheader("📖 Kaynakça (References)")
    
    if st.session_state.references:
        for idx, ref in enumerate(st.session_state.references):
            st.markdown(f"**[{idx+1}]** {ref['link']} — *({ref['format']} Formatında İşlendi)*")
    else:
        st.write("Henüz kaynak eklenmedi.")

    if st.button("Kütüphaneyi Temizle"):
        st.session_state.references = []
        st.rerun()
