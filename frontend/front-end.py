import streamlit as st
import requests
import json
import base64
import os
import dotenv

dotenv.load_dotenv()

function_url = os.getenv("AZURE_FUNCTION_ENDPOINT")
st.set_page_config(page_title="Document Translation Demo", layout="wide")

st.title("Document Translation Demo")

# Prompt user to upload a PDF
uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()  # Read the binary content of the file

    # Save the PDF locally (optional)
    pdf_path = "uploaded_document.pdf"
    with open(pdf_path, "wb") as f:
        f.write(file_bytes)

    # Display PDF in the page
    # Convert PDF to base64
    base64_pdf = base64.b64encode(file_bytes).decode('utf-8')



    with st.spinner("Processing..."):
        # Make a POST request with the raw binary data
        headers = {"Content-Type": "application/pdf"}
        try:
            response = requests.post(function_url, headers=headers, data=file_bytes)
            response.raise_for_status()
            data = response.json()  # the returned JSON from the function
        except requests.RequestException as e:
            st.error(f"Error calling the translation function: {e}")
            st.stop()
        
        # Assume data format as previously discussed:
        # [
        #   {
        #       "original_text": "...",
        #       "detected_language": "...",
        #       "detected_language_score": ...,
        #       "translated_text": "...",
        #       "summary": "...",
        #       "description": "..."
        #   }
        # ]

        if isinstance(data, list) and len(data) > 0:
            doc_info = data[0]  # Take the first item if only one document
            original_text = doc_info.get("original_text", "")
            translated_text = doc_info.get("translated_text", "")
            summary = doc_info.get("summary", "")
            description = doc_info.get("description", "")

            col3, col4 = st.columns(2)
            with col3:
                st.subheader("Summary")
                st.write(summary)
  
                st.subheader("Description")
                st.write(description)

                st.subheader("Detected Language")
                st.write(doc_info.get("detected_language", ""))

                st.subheader("Detected Language Score")
                st.write(doc_info.get("detected_language_score", ""))                

            with col4:

                # Create an embedded PDF viewer
                st.subheader("Original Document")
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)                

            st.subheader("Original and Translated Text")
            col1, col2 = st.columns(2)
            with col1:
                st.write("### Original Text")
                st.write(original_text)
            with col2:
                st.write("### Translated Text")
                st.write(translated_text)
        else:
            st.warning("No valid data received from the function. Check the function response format.")
