import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO

# पेज का सेटअप
st.set_page_config(page_title="PDF Result Searcher", layout="wide")

st.title("📄 PDF Result & Name Matcher")
st.markdown("### अपने 33 PDF यहाँ अपलोड करें और Roll Number/Name से सर्च करें")

# 1. साइडबार में फाइल अपलोडर
with st.sidebar:
    st.header("Upload Section")
    uploaded_files = st.file_uploader("PDF फाइल्स चुनें (Multiple)", type=['pdf'], accept_multiple_files=True)
    st.write(f"कुल फाइलें अपलोड की गईं: {len(uploaded_files)}")

# 2. यूजर इनपुट सेक्शन
col1, col2, col3 = st.columns(3)
with col1:
    search_roll = st.text_input("Roll Number (अनिवार्य)", placeholder="Example: 123456")
with col2:
    search_name = st.text_input("Name (नाम)", placeholder="Example: Rahul Kumar")
with col3:
    search_dob = st.text_input("DOB (जन्म तिथि)", placeholder="Example: 15-08-2000")

search_btn = st.button("🔍 सर्च करें")

# फंक्शन: डेटा को एक्सेल में बदलने के लिए
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

# 3. सर्च लॉजिक (Search Logic)
if search_btn and uploaded_files and search_roll:
    found_data = []
    progress_bar = st.progress(0)
    total_files = len(uploaded_files)
    
    st.info("सर्चिंग शुरू हो रही है, कृपया प्रतीक्षा करें...")

    for i, pdf_file in enumerate(uploaded_files):
        try:
            # PDF को खोलना और पढ़ना
            with pdfplumber.open(pdf_file) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        lines = text.split('\n')
                        for line in lines:
                            # 1. रोल नंबर चेक करें
                            if search_roll in line:
                                is_match = True
                                match_details = []

                                # 2. नाम चेक करें
                                if search_name:
                                    if search_name.lower() in line.lower():
                                        match_details.append("✅ Name Matched")
                                    else:
                                        is_match = False
                                        match_details.append("❌ Name Not Matched")

                                # 3. DOB चेक करें
                                if search_dob:
                                    if search_dob in line:
                                        match_details.append("✅ DOB Matched")
                                    else:
                                        match_details.append("⚠️ Check DOB Manually")

                                if is_match:
                                    found_data.append({
                                        "File Name": pdf_file.name,
                                        "Page No": page_num + 1,
                                        "Roll Number": search_roll,
                                        "Match Status": ", ".join(match_details) if match_details else "✅ Found",
                                        "Full Line Text": line.strip()
                                    })
        
        # प्रोग्रेस बार अपडेट
        progress_bar.progress((i + 1) / total_files)

    # 4. रिजल्ट और डाउनलोड बटन
    st.divider()
    if found_data:
        st.success(f"बधाई हो! कुल {len(found_data)} जगह आपका डेटा मिला है।")
        
        # डेटाफ्रेम (Table) बनाना
        df = pd.DataFrame(found_data)
        
        # टेबल दिखाएं
        st.table(df)
        
        # एक्सेल डाउनलोड बटन
        excel_data = to_excel(df)
        st.download_button(
            label="📥 Download Excel Result",
            data=excel_data,
            file_name=f"Result_{search_roll}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    else:
        st.error(f"दुःखद! रोल नंबर '{search_roll}' किसी भी PDF में नहीं मिला।")

elif search_btn and not uploaded_files:
    st.warning("कृपया पहले PDF फाइलें अपलोड करें।")
elif search_btn and not search_roll:
    st.warning("कृपया सर्च करने के लिए Roll Number डालें।")
  
