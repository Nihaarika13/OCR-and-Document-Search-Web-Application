import streamlit as st
import pytesseract
from PIL import Image
import re
import pandas as pd
import json
from io import BytesIO

# Function for OCR using pytesseract with exception handling
def perform_ocr(image):
    try:
        # Perform OCR
        text = pytesseract.image_to_string(image, lang='eng+hin')
        
        # Check if any text was detected
        if not text.strip():
            raise ValueError("No text detected in the image.")
        
        # Check for languages other than Hindi and English
        if not re.search(r'[a-zA-Z\u0900-\u097F]', text):
            raise ValueError("Text in other languages detected. This application only supports Hindi and English.")
        
        return text
    
    except Exception as e:
        st.error(f"Error: {e}")
        return ""

# Function to count words in the extracted text
def count_words(text):
    words = text.split()
    return len(words)

# Save history of extracted text and images
def save_history(image, extracted_text):
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    # Save the image as bytes and keep the extracted text
    img_bytes = BytesIO()
    image.save(img_bytes, format='PNG')
    st.session_state.history.append({
        'image': img_bytes.getvalue(), 
        'text': extracted_text
    })

# Function to download extracted text as JSON
def download_json(extracted_text):
    json_data = json.dumps({"extracted_text": extracted_text}, indent=4)
    st.download_button(
        label="Download Extracted Text as JSON",
        file_name="extracted_text.json",
        mime="application/json",
        data=json_data
    )

# Function to export history as CSV
def download_history_csv():
    if 'history' in st.session_state:
        history_data = [{
            'text': entry['text']
        } for entry in st.session_state.history]
        df = pd.DataFrame(history_data)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download History as CSV",
            data=csv,
            file_name="history.csv",
            mime="text/csv"
        )

# Main Streamlit app
def main():
    # Set page title, logo, and sidebar navigation
    st.set_page_config(page_title="Hindi-English OCR", page_icon="🖼️")
    # Set background color
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #87CEEB;  /* Sky blue color */
        }
        .stButton button {
            background-color: #87CEEB;  /* Sky blue color for buttons */
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.sidebar.image("lgog.jpg", width=200)  # Placeholder for your logo image
    st.sidebar.title("Online-OCR")
    nav = st.sidebar.radio("Go to", ["Home", "About Us", "History"])
    
    # About Us Section
    if nav == "About Us":
        st.title("About Us")
        st.write("""
        **OCR Web Application** allows you to upload images containing text in Hindi and English, extract text, search for keywords, and download results in various formats. 
        This project uses **Pytesseract**, an optical character recognition (OCR) tool for Python.
        """)
        st.write("""**THE STEPS TO FOLLOW:** """)
        st.write("""->Select the image according to the constraints shown.""")
        st.write("""->Click on "Perform OCR".""")
        st.write("""->If needed, you can also search for a keyword from the extracted text.""")
        return
    
    # History Section
    if nav == "History":
        st.title("OCR History")
        if 'history' in st.session_state and st.session_state.history:
            for i, record in enumerate(st.session_state.history):
                st.subheader(f"Entry {i+1}")
                st.image(record['image'], caption="Uploaded Image")
                st.write(record['text'])
            download_history_csv()
        else:
            st.write("No history available yet.")
        return
    
    # Home (OCR functionality)
    st.title("Hindi-English OCR Application")
    st.subheader("Upload an image containing text in both Hindi and English")
    
    # Initialize session state for extracted text
    if 'extracted_text' not in st.session_state:
        st.session_state.extracted_text = ""

    # File uploader for image
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Display uploaded image
        image = Image.open(uploaded_file).convert('RGB')  # Ensure image is in RGB format
        st.image(image, caption='Uploaded Image', use_column_width=True)

        # Perform OCR on image
        if st.button("Perform OCR"):
            extracted_text = perform_ocr(image)
            
            if extracted_text:  # Only display text if OCR was successful
                word_count = count_words(extracted_text)
                
                st.subheader("Extracted Text")
                st.write(extracted_text)
                st.write(f"Number of words: {word_count}")
                
                # Store the extracted text in session state
                st.session_state.extracted_text = extracted_text

                # Save extraction to session state (for history)
                save_history(image, extracted_text)
                
                # Provide download options
                download_json(extracted_text)

    # Keyword search functionality
    if st.session_state.extracted_text:
        keyword = st.text_input("Enter keyword to search:")
        if keyword:
            if re.search(keyword, st.session_state.extracted_text, re.IGNORECASE):
                st.success(f'Keyword "{keyword}" found in the extracted text!')
                highlighted_text = re.sub(f'({keyword})', r'**\1**', st.session_state.extracted_text, flags=re.IGNORECASE)
                st.write(highlighted_text)
            else:
                st.warning(f'Keyword "{keyword}" not found in the extracted text.')

if __name__ == "__main__":
    main()
