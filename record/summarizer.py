
import fitz  
import requests

import os
from dotenv import load_dotenv


load_dotenv()


HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def summarize_prescription(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    if not text.strip():
        return "No text found in PDF."

    text = text[:1000]

    API_URL = "https://api-inference.huggingface.co/models/sshleifer/distilbart-cnn-12-6"
    headers = {
        "Authorization": f"Bearer HUGGINGFACE_TOKEN",  
        "Content-Type": "application/json"
    }
    payload = {"inputs": text}

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()[0]['summary_text']
    else:
        return f"Failed to summarize. Status: {response.status_code}"
