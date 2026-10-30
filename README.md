# hinglish-ai-study-buddy
summarizer

# 📚 Hinglish AI Study Buddy (Week 1)

An AI-powered study companion built for Indian college students. Upload your lecture notes or textbook chapter PDFs, and get exam-ready summaries written in conversational Hinglish with standard English technical terms.

---

## 🚀 Features (Week 1 Scope)

- **PDF Text Extraction**: Extracts text from typed digital PDFs using `PyMuPDF` (`fitz`).
- **Hinglish AI Summaries**: Uses Gemini API (`gemini-1.5-flash`) to generate intuitive summaries (e.g., *"Deadlock tab hota hai jab do process ek-dusre ke resource ka wait karte hain"*).
- **Two Revision Modes**:
  - `Short (10 bullet points)`: High-yield points for quick revision right before exams.
  - `Detailed (topic-wise)`: In-depth breakdown with exam tips and core concepts.
- **Smart Chunking**: Automatically handles long documents using a Map-Reduce chunking strategy (~3000 words per chunk).
- **Graceful Error Handling**: Detects empty PDFs, scanned/image-only PDFs, and API connection issues.

---

## 🛠️ Tech Stack

- **Python**: 3.11+
- **Streamlit**: Web UI
- **PyMuPDF (`fitz`)**: Fast PDF text extraction
- **Google Generative AI SDK**: LLM integration (`gemini-1.5-flash`)
- **python-dotenv**: Secure environment variable handling

---

## 📂 Project Structure

```text
study-buddy/
├── app.py                     # Streamlit UI
├── pdf_utils.py               # PDF text extraction and validation
├── summarizer.py              # Prompt templates, chunking, and Gemini API calls
├── generate_test_samples.py   # One-click generator for test PDFs
├── requirements.txt           # Project dependencies
├── .env.example               # Environment variable template
├── .gitignore                 # Ignores .env and virtual environments
└── README.md                  # Setup and instructions
```

---

## ⚙️ Setup and Installation

### 1. Open Terminal and Navigate to Project
```bash
cd study-buddy
```

### 2. Create and Activate Virtual Environment
- **On Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
  *(If you face execution policy error, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` first)*

- **On macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Your Gemini API Key
1. Get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Copy `.env.example` to `.env`:
   - Windows: `copy .env.example .env`
   - Linux/Mac: `cp .env.example .env`
3. Open `.env` and paste your key:
   ```env
   GEMINI_API_KEY=AIzaSyYourActualKeyHere...
   ```

### 5. (Optional) Generate Sample Test PDFs
Inside your activated virtual environment, run:
```bash
python generate_test_samples.py
```
This automatically creates a `test_samples/` folder with 3 ready-to-test PDFs:
- `short_notes.pdf`: Typed OS Deadlock & Mutex notes.
- `empty.pdf`: 0-byte file to test empty PDF validation.
- `scanned_dummy.pdf`: Visual shapes without text to test scanned PDF detection.

### 6. Run the App
```bash
streamlit run app.py
```
The app will automatically open in your default browser at `http://localhost:8501`.

---

## 🧪 Suggested Test Cases

1. **Short Typed PDF (1–3 pages)**: Upload a brief chapter or tutorial notes (e.g., OS process scheduling). Test both *Short* and *Detailed* modes.
2. **Long Document (20–50 pages)**: Upload an entire textbook chapter (>3000 words) to verify that word chunking and the Map-Reduce consolidation work smoothly without crashing.
3. **Scanned / Image-Only PDF**: Upload an image-only PDF (like a smartphone photo converted to PDF). Verify that the app catches it cleanly and shows the friendly Hinglish warning message instead of crashing.

