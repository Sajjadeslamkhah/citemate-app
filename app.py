import streamlit as st
import requests
import re
import fitz  # PyMuPDF
import base64

import streamlit as st
import requests
import re
import fitz  # PyMuPDF
import base64

# ==========================================
# 1. SAYFA YAPILANDIRMASI & SEO
# ==========================================
st.set_page_config(page_title="Citemate Pro | Elite Academic Citation", page_icon="🎓", layout="wide")

# ==========================================
# 2. LOGO ENTEGRASYONU (DOĞRUDAN KODA GÖMÜLÜ)
# ==========================================
# Logonuz kodun içine gömüldü, dış linke veya dosyaya gerek kalmadı.
LOGO_BASE64 = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAEAAQADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc6R1dnd4eXq04yGVfWz93kD4GLP3n5mRkdTb1N2d5pZGVndW2pan20dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO00b3uLm6wsPExcbHyMnK0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn62dwcHFvENUx8nP0tPU1dbX2Nna4ePn
# ==========================================
# 1. SAYFA YAPILANDIRMASI & SEO
# ==========================================
st.set_page_config(page_title="Citemate Pro | Elite Academic Citation", page_icon="🎓", layout="wide")

# ==========================================
# 2. LOGO VE GÖRSEL YÖNETİMİ
# ==========================================
# Logonun GitHub üzerindeki doğrudan linki
LOGO_URL = "https://raw.githubusercontent.com/sajjadeslamkhah/citemate-app/main/Logo.jpg"

# ==========================================
# 3. KRİTİK HAFIZA BAŞLATMA
# ==========================================
if 'refs' not in st.session_state: st.session_state.refs = []
if 'lang' not in st.session_state: st.session_state.lang = "Türkçe"

# ==========================================
# 4. TASARIM (CSS)
# ==========================================
MY_EMAIL = "mbgsajjad@gmail.com"

st.markdown(f"""
    <style>
    .stApp {{ background-color: #0e1117; }}
    .main-title {{ font-size: 58px !important; font-weight: 900 !important; color: #34d399; margin-bottom: 0px; }}
    .info-box {{ background-color: rgba(52, 211, 153, 0.05); padding: 22px; border-radius: 12px; border: 1px dashed rgba(52, 211, 153, 0.3); margin-bottom: 35px; }}
    .service-card {{ background: #161b22; padding: 25px; border-radius: 18px; border-top: 4px solid #34d399; margin-bottom: 20px; min-height: 220px; }}
    .footer {{ color: #64748b; font-size: 14px; text-align: center; margin-top: 60px; padding: 20px; border-top: 1px solid #1e293b; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 5. YAN MENÜ (NAVİGASYON & LOGO ENTEGRASYONU)
# ==========================================
with st.sidebar:
    # BURASI GÜNCELLENDİ: Yazı silindi, yerine logo eklendi.
    st.image(LOGO_URL, use_container_width=True)
    
    st.divider()
    
    # Dil Seçimi
    l1, l2 = st.columns(2)
    if l1.button("🇹🇷 TR"): st.session_state.lang = "Türkçe"
    if l2.button("🇺🇸 EN"): st.session_state.lang = "English"
    
    st.divider()
    page_selection = st.radio("SİSTEM MENÜSÜ", ["🏠 Atıf Motoru", "💎 Profesyonel Hizmetler"], label_visibility="collapsed")
    
    st.divider()
    st.markdown(f"""
        <div style="background:#1e293b;padding:18px;border-radius:12px;border:1px solid #334155;text-align:center;">
            <p style="color:#34d399;font-weight:bold;margin-bottom:8px;">📩 Bize Ulaşın</p>
            <a href="mailto:{MY_EMAIL}" style="display:block;background:#34d399;color:black;padding:10px;border-radius:8px;font-weight:bold;text-decoration:none;">Mesaj Gönder</a>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 6. AKILLI VERİ MOTORU
# ==========================================
def get_metadata(query, is_doi=False):
    doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
    try:
        clean_q = re.search(doi_pattern, query, re.I).group() if is_doi else query
        url = f"https://api.crossref.org/works/{clean_q}" if is_doi else f"https://api.crossref.org/works?query={query}&rows=1"
        res = requests.get(url, timeout=10).json()
        item = res['message'] if is_doi else res['message']['items'][0]
        authors = item.get('author', [])
        fmt_authors = [f"{a.get('family', '')} {a.get('given', '')[:1]}" for a in authors[:6]]
        author_str = ", ".join(fmt_authors)
        if len(authors) > 6: author_str += " et al"
        return {
            "title": item.get('title', ['Untitled'])[0], "author": author_str,
            "year": str(item.get('published-print', item.get('created', {})).get('date-parts', [[2026]])[0][0]),
            "journal": item.get('container-title', [''])[0], "vol": item.get('volume', ''),
            "issue": item.get('issue', ''), "page": item.get('page', ''), "doi": item.get('DOI', '')
        }
    except: return None

# ==========================================
# 7. SAYFA İÇERİKLERİ
# ==========================================

if page_selection == "🏠 Atıf Motoru":
    st.markdown('<p class="main-title">🎓 Citemate Pro</p>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:#94a3b8; margin-bottom:30px;">{"Akademik Mükemmeliyet İçin Kusursuz Atıf Yönetimi" if st.session_state.lang == "Türkçe" else "Elite Academic Citation Engine"}</p>', unsafe_allow_html=True)

    # BİLGİLENDİRME
    st.markdown("""<div class="info-box"><b>Citemate Pro</b>, araştırmacıların kaynakça yükünü hafifletmek için tasarlanmış, yapay zeka destekli bir <b>atıf düzenleme motorudur.</b> DOI, başlık veya PDF kullanarak saniyeler içinde hatasız; Vancouver, APA ve IEEE formatlarında profesyonel referanslar oluşturur.</div>""", unsafe_allow_html=True)

    style = st.selectbox("Bibliyografik Format:", ["Vancouver (NLM)", "APA 7th Edition", "IEEE", "Nature", "AMA"])
    t1, t2, t3, t4 = st.tabs(["🔗 DOI / PMID", "🔍 Başlık Arama", "📄 PDF Analizi", "📖 Kullanım Kılavuzu"])
    
    with t1:
        doi_in = st.text_input("DOI:", key="f_doi")
        if st.button("Ekle", key="btn_d"):
            res = get_metadata(doi_in, True)
            if res: st.session_state.refs.append(res); st.rerun()

    with t2:
        q_in = st.text_input("Yayın Adı:", key="f_q")
        if st.button("Global Ara", key="btn_s"):
            res = get_metadata(q_in, False)
            if res: st.session_state.refs.append(res); st.rerun()

    with t3:
        f_pdf = st.file_uploader("PDF", type="pdf")
        if f_pdf and st.button("Veri Çek"):
            try:
                with fitz.open(stream=f_pdf.read(), filetype="pdf") as doc:
                    txt = "".join([p.get_text() for p in doc[:3]])
                    match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', txt, re.I)
                    if match:
                        res = get_metadata(match.group(), True)
                        if res: st.session_state.refs.append(res); st.rerun()
            except: st.error("Hata oluştu.")

    with t4:
        st.markdown("### 📖 Kullanım Kılavuzu")
        st.write("1. **Yöntem:** DOI, Arama veya PDF yüklemeden birini seçin.")
        st.write("2. **Stil:** Üstteki listeden derginize uygun formatı seçin.")
        st.write("3. **İndir:** Listenin altındaki butona basarak kaynakçayı TXT olarak kaydedin.")

    if st.session_state.refs:
        st.divider()
        txt_out = ""
        for i, r in enumerate(st.session_state.refs, 1):
            v_i = f"{r['vol']}({r['issue']})" if r['vol'] and r['issue'] else r['vol']
            p_g = f":{r['page']}" if r['page'] else ""
            if "Vancouver" in style: cite = f"{i}. {r['author']}. {r['title']}. {r['journal']}. {r['year']};{v_i}{p_g}. doi:{r['doi']}"
            elif "APA" in style: cite = f"{r['author']} ({r['year']}). {r['title']}. {r['journal']}, {v_i}{p_g}. https://doi.org/{r['doi']}"
            else: cite = f"[{i}] {r['author']}, \"{r['title']},\" {r['journal']}, {r['year']}."
            st.code(cite, language="text")
            txt_out += cite + "\n"
        
        c_1, c_2 = st.columns(2)
        with c_1: st.download_button("📥 TXT Olarak İndir", txt_out, use_container_width=True)
        with c_2: 
            if st.button("🗑️ Temizle", use_container_width=True): st.session_state.refs = []; st.rerun()

    st.divider()
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.markdown(f"### ❓ Sıkça Sorulan Sorular")
        with st.expander("Scholar uyumlu mu?"): st.write("Evet, Google Scholar ve PubMed standartlarıyla tam uyumludur.")
        with st.expander("Dosyalar saklanıyor mu?"): st.write("Hayır, verileriniz işlendikten sonra anında silinir.")
    with col_f2:
        st.markdown(f"### 🚀 Neden Citemate?")
        st.write("✓ **Hız:** Ek yazılım kurmadan anında çözüm.")
        st.write("✓ **Bilimsel Derinlik:** Lifegenix'in biyoinformatik tecrübesiyle hatasız veri.")

elif page_selection == "💎 Profesyonel Hizmetler":
    st.markdown('<p class="main-title">Profesyonel Hizmetler</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94a3b8; margin-bottom:30px;">Lifegenix Danışmanlık: Biyoinformatik ve Büyük Veri</p>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""<div class="service-card"><h3>🧬 Genetik Veri Analizi</h3><p>NCBI, GEO ve TCGA veri setlerinin Python tabanlı işlenmesi.</p><span class="feature-tag">TCGA</span><span class="feature-tag">GEO</span></div>""", unsafe_allow_html=True)
        st.markdown("""<div class="service-card"><h3>🤖 Sağlıkta Makine Öğrenimi</h3><p>Klinik veri modelleme ve yapay zeka çözümleri.</p><span class="feature-tag">Python</span><span class="feature-tag">AI</span></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="service-card"><h3>📊 Büyük Veri Analitiği</h3><p>Karmaşık veri setlerinin istatistiksel raporlanması.</p><span class="feature-tag">Big Data</span><span class="feature-tag">Stats</span></div>""", unsafe_allow_html=True)
        st.markdown("""<div class="service-card"><h3>🖋️ Akademik Yazım & Editoryal</h3><p>Uluslararası referans yönetimi ve yayına hazırlık.</p><span class="feature-tag">Editorial</span><span class="feature-tag">Publication</span></div>""", unsafe_allow_html=True)

st.markdown('<div class="footer">© 2026 Lifegenix Danışmanlık | Akademik Dürüstlük</div>', unsafe_allow_html=True)
