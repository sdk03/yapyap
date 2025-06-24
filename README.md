# YAPYAP: PDF & URL Reader with AI Summaries & Audio

A modern Flask web application that extracts content from PDF files and web pages, generates AI-powered summaries, and creates audio versions of those summaries. Now with a secure, user-friendly settings page for managing your own OpenAI API key, which can be saved with encryption in your browser.

---

## 🚀 Features

- **PDF Reader**: Upload and extract text from PDF files
- **URL Reader**: Fetch and display text from web pages
- **AI Summaries**: Generate summaries using OpenAI GPT-4o
- **Audio Generation**: Convert summaries to high-quality audio (TTS)
- **Voice Selection**: Choose from 6 different AI voices
- **User API Key Management**: Enter and store your own OpenAI API key securely in your browser (encrypted with AES)
- **Modern UI**: Responsive, mobile-friendly, and beautiful
- **Secure**: User API keys are encrypted in-browser and never sent to the server except for the current request

---

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd YAPYAP
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure OpenAI API Key (choose one or both):**

   **3a. Server Default API Key (for all users, optional):**
   - Create a `.env` file in the project root:
     ```env
     OPENAI_API_KEY=sk-your_default_server_key_here
     ```
   - Or set the environment variable in your shell:
     ```bash
     # PowerShell
     $env:OPENAI_API_KEY = "sk-your_default_server_key_here"
     # Bash
     export OPENAI_API_KEY=sk-your_default_server_key_here
     ```
   - This key will be used for all requests unless a user provides their own key in the browser.

   **3b. User API Key (recommended for privacy):**
   - Start the app and open it in your browser.
   - Click the ⚙️ Settings button (top right).
   - Enter your own OpenAI API key (it will be encrypted and saved in your browser only).
   - This key will be used for your requests and never stored on the server.

---

## ⚙️ Usage

1. **Start the Flask application**
   ```bash
   python app.py
   ```

2. **Open your browser** and go to:
   ```
   http://localhost:5000
   ```

3. **Use the application**
   - **PDF Reader Tab**: Upload a PDF and click "Read PDF"
   - **URL Reader Tab**: Enter a URL and click "Read URL"
   - **Generate Summaries**: Select a summary type (30s TLDR, 60s, 5min, ELI5)
   - **Generate Audio**: Choose a voice and click "Generate Audio"
   - **Settings**: Click the ⚙️ button (top right) to enter your own OpenAI API key (encrypted in your browser)

---

## 🔐 User API Key Management

- **Settings Page**: Click the ⚙️ button to open the settings modal.
- **Encryption**: Your API key is encrypted in-browser using AES (CryptoJS) and stored in `localStorage`. **You can save your API key with encryption in your browser for convenience and security.**
- **Privacy**: The key is never sent to the server except as a custom header for summary/audio requests. The server never logs or stores your key.
- **Fallback**: If no user key is set, the server's default key (from `.env`) is used.
- **Industry Standard**: This approach ensures user privacy and security, following best practices for client-side secret management.

---

## 🧑‍💻 Developer Notes

- **Frontend**: Pure HTML, CSS, and JS (no frameworks). CryptoJS is used for encryption.
- **Backend**: Flask, OpenAI Python SDK v1.x, python-dotenv for environment management.
- **API Key Header**: User key is sent as `X-User-OpenAI-Key` in requests to `/generate_summary` and `/generate_audio`.
- **Server Logic**: If the header is present and valid, it is used for OpenAI calls; otherwise, the server's key is used.
- **No Persistent Storage**: User keys are never written to disk or logs.

---

## 📝 Example .env

```env
OPENAI_API_KEY=sk-your_default_server_key_here
```

---

## 🗝️ Security & Privacy

- **User API keys are encrypted in-browser** and never stored on the server.
- **You can save your API key with encryption in your browser** for seamless, secure use across sessions.
- **No persistent storage** of user keys on the backend.
- **All OpenAI requests** are made with the user's key if provided, otherwise the server's key.
- **Industry best practices** for handling secrets in browser-based apps.

---

## 🧩 File Structure

```
YAPYAP/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── templates/
    └── index.html      # Web interface template
```

---

## 🧪 Testing

- **Test your OpenAI key**: Use the settings modal to enter your key and try generating a summary or audio.
- **Fallback**: Remove your key from settings to use the server's key.
- **Error Handling**: All errors are shown in the UI and logged in the Flask console.

---

## 🖥️ Browser Compatibility

- Chrome (recommended)
- Firefox
- Safari
- Edge
- Mobile browsers

---

## 💡 Troubleshooting

- **500 errors**: Usually indicate an invalid or missing API key, or OpenAI API limits.
- **No audio/summary**: Check your API key and usage limits.
- **.env not loaded**: Make sure you have `python-dotenv` installed and `.env` in the project root.
- **CORS issues**: Not expected in local use; if deploying, configure CORS as needed.

---

## 📦 Dependencies

- Flask
- requests
- PyPDF2
- beautifulsoup4
- lxml
- openai>=1.0.0
- python-dotenv
- CryptoJS (frontend, via CDN)

---

## 📜 License

MIT License. See  for details.

---

## 🙏 Acknowledgements

- [OpenAI](https://openai.com/) for the API
- [CryptoJS](https://cryptojs.gitbook.io/docs/) for browser encryption
- [Flask](https://flask.palletsprojects.com/) for the backend

---

## 🤝 Contributing

Pull requests and issues are welcome! Please open an issue for bugs, feature requests, or questions.

---

## 📣 Contact

For support or questions, open an issue or contact the maintainer. # yapyap
