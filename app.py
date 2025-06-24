from dotenv import load_dotenv
load_dotenv()

import os
import openai
import requests
from urllib.parse import urlparse
import PyPDF2
import io
import re
from bs4 import BeautifulSoup
import base64
import tempfile
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)

def get_openai_client(user_api_key=None):
    api_key = user_api_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        return None
    return openai.OpenAI(api_key=api_key)

def extract_text_from_pdf(pdf_file):
    """Extract text content from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_text_from_url(url):
    """Extract text content from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        return f"Error fetching URL: {str(e)}"

def generate_summary(content, summary_type, user_api_key=None):
    """Generate summary using GPT-4 API"""
    print(f"[INFO] Generating {summary_type} summary...")
    
    client = get_openai_client(user_api_key)
    if not client:
        print("[ERROR] OpenAI API key not configured")
        return "Error: OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable."
    
    # Define prompts for different summary types
    prompts = {
        "30_second_tldr": "Create a very brief 30-second TLDR summary of the following content. Focus on the most important points only:",
        "60_second_summary": "Create a 60-second summary of the following content. Include key points and main ideas:",
        "5_minute_explainer": "Create a comprehensive 5-minute explainer of the following content. Include detailed explanations, context, and examples:",
        "explain_like_5": "Explain the following content as if you're talking to a 5-year-old. Use simple language, analogies, and make it easy to understand:"
    }
    
    try:
        # Truncate content if it's too long (GPT-4 has token limits)
        max_tokens = 4000  # Conservative limit
        original_length = len(content)
        if len(content) > max_tokens:
            content = content[:max_tokens] + "... [Content truncated for processing]"
            print(f"[INFO] Content truncated from {original_length} to {max_tokens} tokens")
        
        print("[INFO] Sending request to OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that creates clear, engaging summaries and explanations. Always respond in a conversational tone suitable for audio narration."
                },
                {
                    "role": "user",
                    "content": f"{prompts[summary_type]}\n\nContent:\n{content}"
                }
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        print("[INFO] Summary generated successfully")
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Error generating summary: {error_msg}")
        if hasattr(e, 'response') and hasattr(e.response, 'json'):
            api_error = e.response.json()
            error_msg = f"{error_msg}\nAPI Error: {api_error}"
        return f"Error generating summary: {error_msg}"

def generate_audio(text, voice="alloy", user_api_key=None):
    """Generate audio from text using OpenAI TTS API"""
    client = get_openai_client(user_api_key)
    if not client:
        return None, "Error: OpenAI API key not configured."
    
    try:
        # Truncate text if it's too long for TTS (max 4096 characters)
        if len(text) > 4000:
            text = text[:4000] + "... [Audio truncated]"
        
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        # Convert the audio response to base64 for sending to frontend
        audio_data = response.content
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        return audio_base64, None
        
    except Exception as e:
        return None, f"Error generating audio: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/read_pdf', methods=['POST'])
def read_pdf():
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['pdf_file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Please upload a PDF file'}), 400
    
    try:
        content = extract_text_from_pdf(file)
        return jsonify({'content': content, 'filename': file.filename})
    except Exception as e:
        return jsonify({'error': f'Error processing PDF: {str(e)}'}), 500

@app.route('/read_url', methods=['POST'])
def read_url():
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Basic URL validation
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return jsonify({'error': 'Please enter a valid URL'}), 400
    except:
        return jsonify({'error': 'Please enter a valid URL'}), 400
    
    try:
        content = extract_text_from_url(url)
        return jsonify({'content': content, 'url': url})
    except Exception as e:
        return jsonify({'error': f'Error fetching URL: {str(e)}'}), 500

@app.route('/generate_summary', methods=['POST'])
def generate_summary_route():
    data = request.get_json()
    content = data.get('content', '').strip()
    summary_type = data.get('summary_type', '')
    user_api_key = request.headers.get('X-User-OpenAI-Key')
    if user_api_key and not user_api_key.startswith('sk-'):
        user_api_key = None
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    if not summary_type:
        return jsonify({'error': 'Summary type is required'}), 400
    
    valid_types = ['30_second_tldr', '60_second_summary', '5_minute_explainer', 'explain_like_5']
    if summary_type not in valid_types:
        return jsonify({'error': 'Invalid summary type'}), 400
    
    try:
        summary = generate_summary(content, summary_type, user_api_key)
        return jsonify({'summary': summary, 'type': summary_type})
    except Exception as e:
        return jsonify({'error': f'Error generating summary: {str(e)}'}), 500

@app.route('/generate_audio', methods=['POST'])
def generate_audio_route():
    data = request.get_json()
    text = data.get('text', '').strip()
    voice = data.get('voice', 'alloy')
    user_api_key = request.headers.get('X-User-OpenAI-Key')
    if user_api_key and not user_api_key.startswith('sk-'):
        user_api_key = None
    if not text:
        return jsonify({'error': 'Text is required'}), 400
    
    try:
        audio_base64, error = generate_audio(text, voice, user_api_key)
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify({'audio': audio_base64, 'voice': voice})
    except Exception as e:
        return jsonify({'error': f'Error generating audio: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True) 