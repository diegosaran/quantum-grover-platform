# backend/app/routers/quantum.py
from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from typing import Optional
import os
import uuid
import re
import time
from datetime import datetime, timedelta
from app.models.schemas import SearchRequest, SearchResponse, FileUploadResponse, HealthResponse
from app.circuits.grover_dna import GroverDNASearch

router = APIRouter(prefix="/quantum", tags=["quantum"])
sessions = {}
SESSION_TIMEOUT = timedelta(minutes=30)

def extract_dna_sequence(content: str) -> str:
    """Extract only DNA bases (A, C, G, T)"""
    return re.sub(r'[^acgt]', '', content.lower())

@router.get("/health")
async def health_check():
    import qiskit
    return {
        "status": "operational",
        "version": "2.0.0",
        "qiskit_version": qiskit.__version__,
        "active_sessions": len(sessions)
    }

@router.post("/upload")
async def upload_dna_file(file: UploadFile = File(...)):
    """Upload DNA file"""
    content = await file.read()
    text_content = content.decode('utf-8')
    dna_sequence = extract_dna_sequence(text_content)
    
    if len(dna_sequence) == 0:
        raise HTTPException(400, "No DNA bases found")
    
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "dna_sequence": dna_sequence,
        "filename": file.filename,
        "created_at": datetime.now(),
        "sequence_length": len(dna_sequence)
    }
    
    return {
        "success": True,
        "session_id": session_id,
        "message": f"Uploaded {len(dna_sequence):,} bases",
        "dna_sequence_length": len(dna_sequence),
        "first_100_bases": dna_sequence[:100]
    }

@router.post("/simulate")
async def simulate_grover_search(
    request: SearchRequest,
    session_id: Optional[str] = Query(None)
):
    """Complete quantum search with classical comparison"""
    
    # 1. Get DNA sequence
    if session_id and session_id in sessions:
        dna_sequence = sessions[session_id]["dna_sequence"]
        source = "uploaded"
    else:
        default_file = "gen_bases.txt"
        if not os.path.exists(default_file):
            raise HTTPException(404, "No DNA database found")
        with open(default_file, "r") as f:
            dna_sequence = extract_dna_sequence(f.read())
        source = "default"
    
    # Limit size
    dna_size = min(request.dna_size, len(dna_sequence))
    dna_sequence = dna_sequence[:dna_size]
    
    # 2. CLASSICAL SEARCH (exactly like your original script)
    classical_start = time.time()
    target_positions = []
    gene_len = len(request.gene_sequence)
    
    for pos in range(len(dna_sequence) - gene_len + 1):
        if dna_sequence[pos:pos + gene_len] == request.gene_sequence:
            target_positions.append(pos)
    
    classical_time = (time.time() - classical_start) * 1000
    
    # 3. QUANTUM SEARCH
    grover = GroverDNASearch(dna_sequence, request.gene_sequence, dna_size)
    counts, quantum_time = grover.run_simulation(shots=request.shots)
    analysis = grover.analyze_results(counts, request.shots)
    info = grover.get_info()
    
    # 4. Return complete data for frontend
    return {
        # Success info
        "success": True,
        "source": source,
        
        # Classical results (what your script shows)
        "classical": {
            "occurrences": len(target_positions),
            "positions": target_positions[:50],  # First 50 positions
            "positions_sample": target_positions[:10],
            "time_ms": round(classical_time, 2)
        },
        
        # Quantum results
        "quantum": {
            "success_rate": analysis["success_rate"],
            "time_ms": round(quantum_time, 2),
            "top_measurements": analysis["top_measurements"],
            "shots_used": request.shots
        },
        
        # Circuit configuration
        "circuit": {
            "n_qubits": info["n_qubits"],
            "total_states": info["total_states"],
            "grover_iterations": info["grover_iterations"],
            "targets_marked": info["num_targets"]
        },
        
        # DNA info
        "dna": {
            "size_analyzed": dna_size,
            "gene_sequence": request.gene_sequence,
            "gene_length": len(request.gene_sequence)
        },
        
        # Visualization (optional)
        "circuit_image": grover.get_circuit_diagram() if request.visualize else None
    }

@router.get("/info")
async def get_info(session_id: Optional[str] = Query(None)):
    """Get database info"""
    if session_id and session_id in sessions:
        session = sessions[session_id]
        return {
            "source": "uploaded",
            "filename": session["filename"],
            "size": session["sequence_length"],
            "created": session["created_at"].isoformat()
        }
    else:
        return {"source": "default", "file": "gen_bases.txt"}