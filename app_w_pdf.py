import streamlit as st
import numpy as np
from PIL import Image
import time
import utlis
import easyocr
import cv2
import fitz  # PyMuPDF
import io

# Cache the EasyOCR reader with both Arabic and English languages
@st.cache_resource
def get_reader_lang():
    return easyocr.Reader(['ar', 'en'])

# Cache the result of OCR processing
@st.cache_data
def get_result(image):
    reader = get_reader_lang()
    result = reader.readtext(image)
    return result 

def extract_images_from_pdf(pdf_file):
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    pages = []
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        image_list = page.get_images(full=True)
        page_images = []
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            page_images.append(np.asarray(image))
        pages.append(page_images)
    return pages

def main():
    st.markdown("<h1 style='text-align: center; position:static; top:-50; color: rgb(65, 59, 59); font-size:300%;'>Arabic and English OCR</h1>", unsafe_allow_html=True)
    side_bar = st.sidebar
    file = side_bar.file_uploader('Upload an image or PDF', type=['png', 'jpg', 'jpeg', 'pdf'])
    col1, col2 = st.columns(2)
    
    if file is not None:
        images = []
        if file.type == 'application/pdf':
            pages = extract_images_from_pdf(file)
            total_pages = len(pages)
            start_btn = side_bar.button('Start OCR')
            ocr_pages = 3
            
            if start_btn:
                for page_num, page_images in enumerate(pages):
                    st.write(f"Processing page {page_num + 1} of {ocr_pages}")
                    for image_index, image in enumerate(page_images):
                        animation_placeholder = st.empty()
                        animation_placeholder.markdown(utlis.read_custum_html('animation_style.html'), unsafe_allow_html=True)
                        t1 = time.time()
                        
                        result = get_result(image)
                        
                        animation_placeholder.empty()
                        if result:  # Check if result is not empty
                            annoted_image = utlis.annotate_image(image.copy(), result)
                            annoted_image = Image.fromarray(annoted_image)
                            col1.text('Image')
                            col1.image(annoted_image, use_column_width=True)
                            extracted_text = utlis.get_raw_text(result)
                            col2.text('Extracted text')
                            col2.write(extracted_text)
                        else:
                            col1.text('No text detected in this image.')
                        
                        t2 = time.time()
                        st.write(f'Image {image_index + 1} on page {page_num + 1} processed in {t2 - t1:.2f} seconds')
        else:
            images = [get_image(file)]
            start_btn = side_bar.button('Start OCR')
            
            if start_btn:
                for image_index, image in enumerate(images):
                    animation_placeholder = st.empty()
                    animation_placeholder.markdown(utlis.read_custum_html('animation_style.html'), unsafe_allow_html=True)
                    t1 = time.time()
                    
                    result = get_result(image)
                    
                    animation_placeholder.empty()
                    if result:  # Check if result is not empty
                        annoted_image = utlis.annotate_image(image.copy(), result)
                        annoted_image = Image.fromarray(annoted_image)
                        col1.text('Image')
                        col1.image(annoted_image, use_column_width=True)
                        extracted_text = utlis.get_raw_text(result)
                        col2.text('Extracted text')
                        col2.write(extracted_text)
                    else:
                        col1.text('No text detected in this image.')
                    
                    t2 = time.time()
                    st.write(f'Image {image_index + 1} processed in {t2 - t1:.2f} seconds')

if __name__ == "__main__":
    main()