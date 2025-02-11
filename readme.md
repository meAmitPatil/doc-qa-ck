# 📚 Doc-QA-CK: AI-Powered Document Q&A System

**Doc-QA-CK** is an AI-driven document intelligence platform that allows users to upload multiple PDF documents and engage in AI-powered Q&A conversations. It leverages **OpenAI , Qdrant for vector search, and Phoenix for observability & tracing.**

## 🚀 Features

✅ **AI-Powered Q&A:** Ask questions about uploaded documents and receive intelligent answers.  
✅ **Multi-Document Support:** Query across multiple PDFs for cross-document analysis.  
✅ **RAG Pipeline:** Uses **retrieval-augmented generation (RAG)** for better response accuracy.  
✅ **Phoenix Integration:** Provides observability, tracing, and performance monitoring.  
✅ **FastAPI Backend & Next.js Frontend:** Fully containerized for easy deployment.  

---

## 🛠️ Tech Stack

| Component       | Technology |
|----------------|------------|
| **Frontend**   | Next.js, Tailwind CSS |
| **Backend**    | FastAPI (Python) |
| **Vector DB**  | Qdrant |
| **LLM**        | OpenAI |
| **Parsing**        |  LlamaIndex(SemanticSplitterNodeParser) |
| **Observability** | Phoenix (Arize AI) |
| **Containerization** | Docker, Docker Compose |

---

## 🔧 Installation & Setup

### **1 Clone the Repository**
```sh
git clone https://github.com/meAmitPatil/doc-qa-ck.git
cd doc-qa-ck
```

### **2 Configure Environment Variables**
rename .env.example to .env and fill in the env values.

### **3 Start the Application using Docker**
docker-compose up --build

## 🖥️ Running Locally (Without Docker)

### **1 Backend (FastAPI)**
```sh
cd backend
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### **2 Frontend (Next.js)**
```sh
cd frontend
npm install
npm run dev
```

The frontend should be accessible at http://localhost:3000, and the backend at http://localhost:8000.

## 🤝 Contributing
👨‍💻 Contributions are welcome!
To contribute, fork the repo, create a feature branch, and submit a pull request.