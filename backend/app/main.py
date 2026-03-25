# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import quantum

app = FastAPI(
    title="Quantum DNA Search API - Grover's Algorithm",
    description="""
    API for quantum DNA sequence search using Grover's algorithm.
    
    ## Features
    - 🧬 Search for specific DNA sequences in large databases
    - 📤 Upload your own DNA files (.txt)
    - ⚛️ Quantum speedup: O(√N) vs classical O(N)
    - 📊 Compare classical vs quantum search performance
    - 🔬 Visualize quantum circuits
    - 📈 Analyze quantum measurement results
    
    ## How it works
    Grover's algorithm uses quantum superposition and amplitude amplification
    to find target DNA sequences exponentially faster than classical search.
    
    ## Usage
    1. Upload your DNA file: POST /quantum/upload
    2. Search for a gene: POST /quantum/simulate?session_id=xxx
    3. Or use default database: POST /quantum/simulate
    """,
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(quantum.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Quantum DNA Search API",
        "version": "2.0.0",
        "algorithm": "Grover's Quantum Search Algorithm",
        "complexity": "O(√N) quantum vs O(N) classical",
        "endpoints": {
            "upload": "POST /quantum/upload - Upload DNA file (.txt)",
            "search": "POST /quantum/simulate - Perform quantum search",
            "info": "GET /quantum/info - Get database information",
            "health": "GET /quantum/health - Health check",
            "docs": "/docs - Interactive API documentation"
        }
    }

@app.get("/about")
async def about():
    return {
        "name": "Quantum DNA Search",
        "algorithm": "Grover's Search Algorithm",
        "description": "Quantum algorithm for unstructured search with quadratic speedup",
        "quantum_advantage": "O(√N) vs classical O(N)",
        "applications": [
            "DNA sequence matching",
            "Database search",
            "Pattern recognition",
            "Bioinformatics"
        ]
    }