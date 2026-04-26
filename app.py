import streamlit as st
import requests
import re
from datetime import datetime

# DOI ayıklama için güçlü Regex
DOI_REGEX = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'

def fetch_metadata(input_data):
    # 1. ADIM: Girdinin içinde DOI var mı bak (İster link olsun ister saf DOI)
    doi_match = re.search(DOI_REGEX, input_data, re.I)
    
    if doi_match:
        doi = doi_match.group()
        # Crossref API'den çekmeye çalış
        api_url = f"https://api.crossref.org/works/{doi}"
        try:
            res = requests.get(api_url, timeout=10)
            if res.status_code == 200:
                data = res.json()['message']
                title = data.get('title', ['Başlık Bulunamadı'])[0]
                authors = data.get('author', [])
                author_name = authors[0].get('family', 'Anonim') if authors else "Anonim"
                year = data.get('created', {}).get('date-parts', [[2024]])[0][0]
                return title, author_name, year, doi
        except:
            pass
            
    # 2. ADIM: DOI yoksa veya API hata verdiyse linkten başlık çekmeyi dene
    # (Buraya daha önce yazdığımız BeautifulSoup kodu gelecek)
    return "Bilinmeyen Başlık", "Manuel Kontrol", 2026, input_data

# ARAYÜZ GÜNCELLEMESİ
st.info("💡 **İpucu:** En kesin sonuç için sadece DOI numarasını (Örn: 10.1016/j.oto...) veya makalenin DOI içeren linkini yapıştırın.")
