# 🚀 Setup Instructions - Hackios

This guide will help you set up the Health Insurance Denial Prevention & Appeal Assistant.

## Prerequisites

- **Python 3.9 or higher**
- **Node.js 16 or higher** and npm
- **Git** (optional, for version control)

---

## Step 1: Install Backend Dependencies

### 1.1 Navigate to the project root directory:
```bash
cd "c:\My Projects\Medical Hackathons\Hackios\Hackios"
```

### 1.2 Create a virtual environment (recommended):
```bash
python -m venv venv
```

<!-- the name of my venv is "hackios_venv" -->

### 1.3 Activate the virtual environment:

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 1.4 Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

> **Note:** PaddleOCR installation may take a few minutes as it downloads the OCR models.

---

## Step 2: Configure Environment Variables

### 2.1 Copy the example environment file:
```bash
cd ..
copy .env.example .env
```

### 2.2 **IMPORTANT: Add Your Groq API Key**

Open the `.env` file in a text editor and replace the dummy API key with your real Groq API key:

```env
GROQ_API_KEY=your_actual_groq_api_key_here
```

#### 🔑 How to Get a Groq API Key:

1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Navigate to **API Keys** section
4. Click **Create API Key**
5. Copy the key and paste it into your `.env` file

> **Note:** The Groq API provides access to Llama-3-8B and Llama-3-70B models for free with rate limits.

---

## Step 3: Install Frontend Dependencies

### 3.1 Navigate to the frontend directory:
```bash
cd frontend
```

### 3.2 Install npm dependencies:
```bash
npm install
```

---

## Step 4: Run the Application

You'll need **two terminal windows** - one for the backend and one for the frontend.

### Terminal 1 - Backend Server:

```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at: `http://localhost:8000`

You can view the API documentation at: `http://localhost:8000/docs`

### Terminal 2 - Frontend Development Server:

```bash
cd frontend
npm run dev
```

The frontend will be available at: `http://localhost:5173`

---

## Step 5: Test the Application

1. Open your browser and go to `http://localhost:5173`
2. You should see the **Hackios** interface with a medical-themed design
3. Upload some test documents (PDFs or images)
4. Select an insurance plan (optional)
5. Choose a workflow:
   - **Pre-Claim Analysis**: Check denial risk before submitting
   - **Denial Explanation**: Understand why a claim was denied
   - **Appeal Letter**: Generate a professional appeal letter PDF

---

## Troubleshooting

### Issue: PaddlePaddle installation fails
**Solution:** Make sure you have the latest version of pip:
```bash
pip install --upgrade pip
```

### Issue: PyMuPDF build error (requires Visual Studio)
**Solution:** This is already fixed in `requirements.txt`. We use PyMuPDF>=1.23.0 which has prebuilt wheels for Windows.

### Issue: Groq API errors (`TypeError: Client.__init__() got an unexpected keyword argument 'proxies'`)
**Solution:** Upgrade Groq SDK to the latest version:
```bash
pip install --upgrade groq
```
The `requirements.txt` already specifies `groq>=0.9.0` to avoid this issue.

### Issue: PaddleOCR errors (`show_log` or `cls` parameter errors)
**Solution:** These parameters were removed in newer PaddleOCR versions. The code has been updated to remove these deprecated parameters.

### Issue: `ModuleNotFoundError: No module named 'backend'`
**Solution:** This is already fixed. The imports now use relative imports instead of absolute `backend.*` imports.

### Issue: Model decommissioned error (`llama-3.1-70b-versatile`)
**Solution:** Updated to use `llama-3.3-70b-versatile` in `config.py`. This is the current supported model.

### Issue: Frontend can't connect to backend (ECONNREFUSED ::1:8000)
**Solution:** `vite.config.js` has been updated to use `127.0.0.1` instead of `localhost` to force IPv4 connection.

### Issue: Groq API key errors or slow analysis
**Solutions:**
1. Verify your API key is correct in the `.env` file (not `.env.example`)
2. Check you haven't exceeded rate limits at https://console.groq.com
3. Verify your internet connection

### Issue: OCR extraction fails
**Solution:** Make sure you have Poppler installed for PDF processing:
- **Windows**: Download from https://github.com/oschwartz10612/poppler-windows/releases/ and add to PATH
- **Mac**: `brew install poppler`
- **Linux**: `sudo apt-get install poppler-utils`

### Issue: Port already in use
**Solution:** 
- For backend: Change `BACKEND_PORT` in `.env` file
- For frontend: Change port in `vite.config.js`

---

## Database Location

The SQLite database will be created automatically at:
```
backend/data/app.db
```

Uploaded files will be stored in:
```
backend/uploads/
```

---

## Next Steps

- Upload your medical documents and test the three workflows
- Check the analysis results and denial risk scores
- Generate an appeal letter and review the PDF output
- For production deployment, consider using PostgreSQL instead of SQLite

---

## Need Help?

- Check the [README.md](README.md) for project overview
- Review the FastAPI documentation at `http://localhost:8000/docs`
- Ensure all dependencies are installed correctly

**Happy Hacking! 🏥**
