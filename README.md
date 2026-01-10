<div align="center">
  <img src="frontend/src/assets/logo.png" alt="DenialShield Logo" width="140" style="border-radius: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
  <h1>DenialShield</h1>
  <p><strong>Autonomous Medical Appeal Agent</strong></p>
  <p><i>"Healthcare is a right, not a privilege. Let AI fight the bureaucracy."</i></p>

  <p>
    <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
    <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
    <img src="https://img.shields.io/badge/LangGraph-FF4B4B?style=for-the-badge&logo=langchain&logoColor=white" alt="LangGraph" />
    <img src="https://img.shields.io/badge/PaddleOCR-007AFF?style=for-the-badge" alt="PaddleOCR" />
    <img src="https://img.shields.io/badge/Groq-F55036?style=for-the-badge" alt="Groq" />
  </p>
</div>

---

## 🌟 Overview

**DenialShield** is a cutting-edge Health Insurance Appeal Assistant powered by **Agentic AI**. It doesn't just generate text; it orchestrates a team of specialized AI agents to analyze, strategize, and fight incorrect claim denials.

By combining **PaddleOCR** for document understanding and **LangGraph** for multi-agent collaboration, DenialShield turns a complex, stressful process into a single click.

---

## 🌟 Features

### 1. **Multi-Agent Appeal Generation**
Six specialized AI agents work together to create compelling appeal letters:
- **Policy Agent**: Analyzes insurance policy compliance
- **Medical Agent**: Validates clinical necessity and medical justification
- **Legal Agent**: Ensures regulatory compliance (ERISA, state laws)
- **Simulator Agent**: Predicts approval probability with counterfactual analysis
- **Negotiator Agent**: Drafts persuasive appeal language
- **Auditor Agent**: Quality-checks the final letter

### 2. **Knowledge Graph Memory System**
- Automatically tracks repetitive denial patterns
- Learns from past cases to suggest proven solutions
- Identifies common missing documentation by insurance provider
- Provides historical success strategies for similar denials

### 3. **Claim Outcome Simulator** 🔮
- Estimates current approval probability (0-100%)
- Identifies critical missing evidence
- Generates 3 "what-if" scenarios showing how adding specific documents improves chances
- Uses counterfactual reasoning with Llama-3.3-70B

### 4. **Intelligent Document Analysis**
- Automated OCR extraction from medical bills, denial letters, and doctor's notes
- Supports PDF and image formats
- Structured data extraction with AI validation
- Policy compliance checking against major insurers

### 5. **Professional PDF Generation**
- Legally formatted appeal letters with proper structure
- Patient information auto-population
- Downloadable PDFs ready for submission

---

## 🏗️ Architecture

### Multi-Agent Workflow

```
┌─────────────┐
│   Upload    │
│ Documents   │
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌──────────────┐
│   Policy    │──────►│   Medical    │
│   Agent     │      │   Agent      │
└─────────────┘      └──────┬───────┘
                            │
                  ┌─────────┴─────────┐
                  ▼                   ▼
           ┌──────────┐        ┌─────────────┐
           │  Legal   │        │  Simulator  │
           │  Agent   │        │   Agent     │
           └────┬─────┘        └──────┬──────┘
                │                     │
                └─────────┬───────────┘
                          ▼
                  ┌───────────────┐
                  │  Negotiator   │
                  │    Agent      │
                  └───────┬───────┘
                          ▼
                  ┌───────────────┐
                  │   Auditor     │
                  │    Agent      │
                  └───────┬───────┘
                          ▼
                  ┌───────────────┐
                  │ Appeal Letter │
                  │   + Results   │
                  └───────────────┘
```

### Tech Stack

**Backend:**
- FastAPI 0.111.0
- LangChain 0.3.1 + LangGraph 0.2.34
- Groq API (Llama-3.3-70B, Llama-3.1-8B)
- SQLAlchemy 2.0.25
- PaddleOCR 2.7.3+
- PyMuPDF, ReportLab

**Frontend:**
- React 18
- Vite
- Axios

**AI Models:**
- **Reasoning**: Llama-3.3-70B (appeal logic, simulation)
- **Extraction**: Llama-3.1-8B (OCR data structuring)

---

## 📦 Installation

### Prerequisites
- Python 3.12+
- Node.js 18+
- Groq API Key ([Get one free](https://console.groq.com))

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/YashGupta2106/denialshield-agentic-ai.git
cd denialshield-agentic-ai

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_groq_api_key_here" > .env

# Run the backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Backend will run on:** `http://localhost:8000`

### Frontend Setup

```bash
# In a new terminal
cd frontend
npm install
npm run dev
```

**Frontend will run on:** `http://localhost:5173`

---

## 🚀 Usage

### 1. Pre-Claim Analysis
- Upload medical bill + doctor's notes
- Select insurance plan
- Get compliance analysis before submitting claim
- Identify missing requirements early

### 2. Claim Outcome Simulator
- Upload medical documents
- AI predicts approval probability
- See exactly which documents would improve your odds
- Example output:
  ```
  Current Approval: 35%
  
  Scenarios:
  → Add MRI Report: 75% approval
  → Add 6 weeks PT notes: 60% approval  
  → Add both: 90% approval
  ```

### 3. Denial Explanation
- Upload denial letter + supporting docs
- Get detailed breakdown of denial reasons
- Understand policy gaps and medical necessity issues

### 4. Appeal Letter Generation
- Upload all documents (bill, notes, denial letter)
- AI agents collaborate to build case
- Download professional PDF ready for submission
- Knowledge graph suggests strategies from similar past cases

---

## 📁 Project Structure

```
denialshield-agentic-ai/
├── backend/
│   ├── agents/                    # Multi-agent system
│   │   ├── orchestrator.py       # Workflow coordinator
│   │   ├── state.py              # Shared state definition
│   │   ├── policy_agent.py       # Policy compliance checker
│   │   ├── medical_agent.py      # Medical necessity validator
│   │   ├── legal_agent.py        # Regulatory compliance
│   │   ├── simulator_agent.py    # Outcome predictor (NEW)
│   │   ├── negotiator_agent.py   # Appeal writer
│   │   └── auditor_agent.py      # Quality control
│   ├── routes/                   # API endpoints
│   │   ├── upload.py            # Document upload
│   │   ├── analyze.py           # Analysis endpoint
│   │   ├── appeal.py            # Appeal generation
│   │   └── simulation.py        # Simulator endpoint (NEW)
│   ├── utils/
│   │   ├── memory_graph.py      # Knowledge graph (NEW)
│   │   ├── pdf_generator.py    # PDF creation
│   │   └── pdf_tools.py         # PDF utilities
│   ├── llm/                     # LLM integrations
│   ├── ocr/                     # OCR processing
│   ├── database.py              # SQLAlchemy models
│   ├── main.py                  # FastAPI app
│   └── requirements.txt         # Dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── FileUpload.jsx
│   │   │   ├── AnalysisResult.jsx
│   │   │   ├── SimulationResult.jsx  # (NEW)
│   │   │   └── AppealDetailsForm.jsx
│   │   ├── services/
│   │   │   └── api.js              # API client
│   │   ├── App.jsx                 # Main app (with simulator)
│   │   └── App.css
│   └── package.json
└── README.md
```

---

## 🔑 Key Components

### Knowledge Graph System
**Location:** `backend/utils/memory_graph.py`

Tracks denial patterns across sessions:
```python
# Records pattern
record_denial_pattern(
    db=session,
    insurance="Aetna",
    denial_code="50",
    procedure="Physical Therapy",
    missing_docs=["PT notes"],
    resolved_by=["Clinical justification"]
)

# Retrieves suggestions
suggestions = get_pattern_suggestions(
    db=session,
    insurance="Aetna", 
    denial_code="50"
)
# Returns: Historical success rate and recommended actions
```

### Simulator Agent
**Location:** `backend/agents/simulator_agent.py`

Uses counterfactual reasoning to predict outcomes:
```python
simulation_result = {
    "current_approval_probability": 45,
    "missing_evidence": ["MRI report", "PT notes"],
    "scenarios": [
        {
            "description": "Add MRI confirming stenosis",
            "estimated_probability": 85,
            "reasoning": "Objective imaging proves medical necessity"
        },
        ...
    ]
}
```

---

## 🧪 Testing

### Test Knowledge Graph
```bash
cd backend
python test_memory_logic.py
```

### Test Full Workflow
1. Start backend & frontend
2. Upload sample documents from `backend/test_data/`
3. Try each workflow:
   - ✅ Pre-Claim Analysis
   - ✅ Claim Simulator
   - ✅ Denial Explanation  
   - ✅ Appeal Generation

---

## 🛠️ Configuration

### Environment Variables
Create `backend/.env`:
```env
# Required
GROQ_API_KEY=your_api_key_here

# Optional
DATABASE_URL=sqlite:///./backend/data/app.db
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
USE_MOCK_OCR=false
```

### Supported Insurance Plans
- Aetna PPO
- BlueCross PPO
- UnitedHealthcare
- Custom policy upload

---

## 📊 Database Schema

### DenialPattern (Knowledge Graph)
```sql
CREATE TABLE denial_patterns (
    id INTEGER PRIMARY KEY,
    insurance VARCHAR,
    procedure VARCHAR,
    cpt_code VARCHAR,
    denial_code VARCHAR,
    missing_docs JSON,
    resolved_by JSON,
    occurrence_count INTEGER,
    last_seen TIMESTAMP
);
```

### UploadedDocument
```sql
CREATE TABLE uploaded_documents (
    id INTEGER PRIMARY KEY,
    filename VARCHAR,
    category VARCHAR,  -- 'PreClaim' | 'Denial'
    file_path VARCHAR,
    upload_date TIMESTAMP,
    ocr_extracted_text TEXT
);
```

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- **Groq** for fast LLM inference
- **LangChain** for agent orchestration framework
- **PaddleOCR** for document processing
- Medical professionals who provided domain expertise

---

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Email: support@denialshield.ai

---

## 🚧 Roadmap

- [ ] Integration with EHR systems
- [ ] Mobile app (iOS/Android)
- [ ] Real-time appeal status tracking
- [ ] Multi-language support
- [ ] Expanded insurance provider coverage
- [ ] Patient outcome feedback loop for improved ML

---

**Built with ❤️ to help patients fight unfair insurance denials**
