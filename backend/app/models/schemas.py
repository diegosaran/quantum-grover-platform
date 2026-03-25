# backend/app/models/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class SearchRequest(BaseModel):
    """Request model for DNA search"""
    gene_sequence: str = Field(..., description="DNA sequence to search for", min_length=1, max_length=50)
    dna_size: int = Field(200000, description="Size of DNA database to analyze", ge=100, le=1000000)
    shots: int = Field(4096, description="Number of quantum measurements", ge=100, le=100000)
    visualize: bool = Field(False, description="Generate circuit visualization")

class FileUploadResponse(BaseModel):
    """Response model for file upload"""
    success: bool
    message: str
    filename: str
    file_size: int
    dna_sequence_length: int
    first_100_bases: str
    session_id: str  # To identify the uploaded file in subsequent requests

class SearchResponse(BaseModel):
    """Response model for DNA search"""
    success: bool
    message: str
    
    # Search results
    target_positions: List[int]
    classical_time_ms: float
    quantum_time_ms: float
    quantum_success_rate: float
    
    # Quantum circuit info
    n_qubits: int
    total_states: int
    grover_iterations: int
    shots_used: int
    
    # Measurement results
    top_measurements: List[Dict[str, Any]]
    
    # Optional visualization
    circuit_image: Optional[str] = None

    # Adicione estes:
    classical_occurrences: int  # Número de ocorrências encontradas classicamente
    classical_positions_sample: List[int]  # Primeiras posições

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    qiskit_version: str
    active_sessions: int