import openai
from dotenv import find_dotenv, load_dotenv
import time
import logging
# import re
import requests
import base64
import json
import streamlit as st
from streamlit_lottie import st_lottie_spinner, st_lottie


load_dotenv()



#APP CONFIGURATION
APP_TITLE = 'Alt Text Generator'
APP_SUBTITLE = 'This app accepts images via upload or URL and returns alt text for accessibility.'
APP_HOW_IT_WORKS = """
                This app creates alt text for accessibility from images. 
                For most images, it provides brief alt text to describe the image, focusing on the most important information first. 

                For complex images, like charts and graphs, the app creates a short description of the image and a longer detail that describes what the complex image is conveying. 

                For more information, see <a href="https://www.w3.org/WAI/tutorials/images/" target="_blank">W3C Images Accessibility Guidelines</a>
             """

#AI CONFIGURATION
AI_CLIENT = openai.OpenAI()
AI_MODEL = "gpt-4-vision-preview"


def submit_command(prompt, http_img_urls, base64_images):

    client = AI_CLIENT

    # Construct the initial content with the prompt
    content = [{"type": "text", "text": prompt}]

    # Append an entry for each image
    for image_http in http_img_urls:
        image_content = {
            "type": "image_url",
            "image_url": {
                "url": image_http,
                "detail": "low"
            }
        }
        content.append(image_content)
    
    
    # Append an entry for each image
    for image_base64 in base64_images:
        image_content = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image_base64}",
                "detail": "low"
            }
        }
        content.append(image_content)
    
    # Build the messages payload
    messages = [{
        "role": "user",
        "content": content,
    }]


    response = client.chat.completions.create(
      model=AI_MODEL,
      messages=messages,
      max_tokens=500,
      stream=True
    )

    return response

    

def main():

    st.title(APP_TITLE)
    st.write(APP_SUBTITLE)

    if APP_HOW_IT_WORKS:
        with st.expander("Learn how this works", expanded=False):
            st.markdown(APP_HOW_IT_WORKS, unsafe_allow_html=True)

    

    http_img_urls = st.text_area("Enter image urls")
    http_img_urls = str(http_img_urls)
    http_img_urls = http_img_urls.split(',') if ',' in http_img_urls else http_img_urls.split('\n')
    http_img_urls = [url.strip() for url in http_img_urls if url.strip()]

    uploaded_files = st.file_uploader("Choose a file", ['png', 'jpeg', 'gif', 'webp'], accept_multiple_files=True)

    base64_imgs = []

    for uploaded_file in uploaded_files:
        file_content = uploaded_file.read()
        base64_encoded_content = base64.b64encode(file_content)
        base64_string = base64_encoded_content.decode('utf-8')
        base64_imgs.append(base64_string)

    important_text = st.checkbox("The text in my image(s) is important", help="If text is important, it should be included in the alt text. If it is irrelevant or covered in text elsewhere on the page, it should not be inlcluded", value=True)
    complex_image = st.checkbox("My image is a complex image (chart, infographic, etc...)", help="Complex images get both a short and a long description of the image", value=False)

    # Determine the total number of images provided
    total_images = len(http_img_urls) + len(base64_imgs)

    # Display a warning if complex_image is checked and more than one image is provided
    if complex_image and total_images > 1:
        st.warning('Please provide only one image for a complex image analysis.')
        submit_enabled = False
    else:
        submit_enabled = True

    if complex_image:
        prompt = """I am sending you a complex image. Please provide a short description to identify the image, and a long description to represent the essential information conveyed by the image. \n
        Please provide your output in this format \n
        <b>Short Description:</b>\n
        [Short Description]\n\n
        <b>Long Description:</b>:\n
        [Long Descrtiption]"""
    else:
        prompt = """I am sending you one or more images. Please provide separate appropriate alt text for each image I send. The alt text should:
        - Aim to put the most important information at the beginning.\n"""
        if important_text:
            prompt += """- Make sure to include any text in this image as part of the alt text"""

    with st.expander("View/edit full prompt"):
        final_instructions = st.text_area(
            label="Prompt",
            height=100,
            max_chars=60000,
            value=prompt,
            key="init_prompt",
        )

    if submit_enabled:
        submit_button = st.button(label="Submit", type="primary", key="submit")
        if submit_button:
            summary = submit_command(prompt, http_img_urls, base64_imgs)
            st.write(summary)
    else:
        # Optionally disable the submit button or leave it out entirely
        st.button(label="Submit", type="primary", key="submit", disabled=True)

if __name__ == "__main__":
    main()
