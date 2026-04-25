import streamlit as st
import re

# Sayfa Ayarları
st.set_page_config(layout="wide", page_title="Citemate Pro")

# Profesyonel Arayüz Tasarımı
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTextArea textarea { font-size: 16px !important; font-family: 'Times New Roman', serif; line-height: 1.6; }
    .ref-card { padding: 10px; border-radius: 5px; background: white; border: 1px solid #ddd; margin-bottom: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .citation-num { color: #007bff; font-weight: bold; }
    </style>
    """, unsafe_content_safe=True)

st.title("🔬 Citemate Pro")
st.caption("Akademik Yazım ve Otomatik Atıf Sistemi")

# Kaynakları session_state içinde saklayalım
if 'references' not in st.session_state:
    st.session_state.references = []

col1, col2 = st.columns([6, 4])

with col1:
    st.subheader("📝 Akademik Editör")
    st.info("İpucu: Atıf yapacağınız yere [cite] yazın. Sağdan kaynak ekledikçe bunlar (1), (2)... olacaktır.")
    
    # KULLANICI GİRİŞİ
    text_input = st.text_area("Yazım Alanı", placeholder="Metninizi buraya yazın...", height=400)
    
    # ATIF İŞLEME MANTIĞI
    processed_text = text_input
    for i in range(len(st.session_state.references)):
        # Her bir [cite] etiketini sırayla değiştiriyoruz
        processed_text = processed_text.replace("[cite]", f"**({i+1})**", 1)
    
    st.divider()
    st.subheader("📄 Nihai Makale Görünümü")
    if text_input:
        # Markdown kullanarak numaraların kalın görünmesini sağlıyoruz
        st.markdown(processed_text)
    else:
        st.write("Editöre metin girdiğinizde işlenmiş hali burada belirecek.")

with col2:
    st.subheader("📚 Kaynak Yönetimi")
    
    # Yeni Kaynak Ekleme
    with st.container():
        st.write("📥 **Yeni Kaynak Tanımla**")
        new_url = st.text_input("Link (PubMed, Scholar, DOI)", key="url_input")
        format_type = st.selectbox("Format", ["Vancouver (Sayısal)", "APA", "Harvard"])
        
        if st.button("Kaynağı Listeye Ekle"):
            if new_url:
                st.session_state.references.append({"url": new_url, "type": format_type})
                st.rerun() # DEĞİŞİKLİĞİ ANINDA GÖRMEK İÇİN ŞART
            else:
                st.warning("Lütfen geçerli bir adres girin.")

    st.divider()
    st.subheader("📖 Kaynakça (References)")
    
    if st.session_state.references:
        for idx, item in enumerate(st.session_state.references):
            st.markdown(f"""
                <div class="ref-card">
                    <span class="citation-num">({idx+1})</span> {item['url']} <br>
                    <small><i>Format: {item['type']}</i></small>
                </div>
            """, unsafe_allow_html=True)
        
        if st.button("Kütüphaneyi Sıfırla"):
            st.session_state.references = []
            st.rerun()
    else:
        st.info("Henüz kaynak eklenmedi. Metne [cite] ekleyip sağ panelden kaynak yükleyin.")
