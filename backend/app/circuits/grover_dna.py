# backend/app/circuits/grover_dna.py
"""
QUANTUM DNA SEARCH - GROVER'S ALGORITHM IMPLEMENTATION
========================================================
This code implements Grover's quantum search algorithm to find specific DNA sequences
in a large DNA database. It demonstrates quantum advantage over classical search.
"""

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import math
import time
import base64
import io
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict, Any

class GroverDNASearch:
    """Grover's algorithm implementation for DNA sequence search"""
    
    def __init__(self, dna_sequence: str, target_gene: str, dna_size: int):
        """
        Initialize Grover's algorithm for DNA search
        
        Args:
            dna_sequence: Full DNA sequence from file
            target_gene: DNA sequence to search for
            dna_size: Number of bases to analyze
        """
        # Clean and prepare DNA sequence
        self.full_dna = dna_sequence.replace("\n", "").replace(" ", "").replace("\r", "").lower()
        self.target_gene = target_gene.lower()
        self.dna_size = min(dna_size, len(self.full_dna))
        self.dna_sequence = self.full_dna[:self.dna_size]
        
        # Validate DNA sequence (only A, C, G, T)
        valid_bases = set('acgt')
        invalid_bases = set(self.dna_sequence) - valid_bases
        if invalid_bases:
            raise ValueError(f"Invalid characters in DNA sequence: {invalid_bases}")
        
        # Find target positions classically
        self.target_positions = self._classical_search()
        
        # Quantum configuration
        self.n_qubits = max(1, math.ceil(math.log2(len(self.dna_sequence))))
        self.total_states = 2 ** self.n_qubits
        self.num_targets = max(1, len(self.target_positions))
        
        # Calculate optimal Grover iterations
        if self.num_targets > 0:
            self.iterations = int(math.pi / 4 * math.sqrt(self.total_states / self.num_targets))
            self.iterations = max(1, self.iterations)
        else:
            self.iterations = 1
        
        # Initialize simulator
        self.simulator = AerSimulator()
    
    def _classical_search(self) -> List[int]:
        """Perform classical linear search to find all target positions"""
        positions = []
        gene_len = len(self.target_gene)
        
        if gene_len > len(self.dna_sequence):
            return positions
        
        # EXATAMENTE como no seu código original
        for position in range(len(self.dna_sequence) - gene_len + 1):
            if self.dna_sequence[position:position + gene_len] == self.target_gene:
                positions.append(position)
        
        return positions
    
    def _create_oracle(self, qc: QuantumCircuit):
        """
        Creates the quantum oracle that marks target positions.
        
        How it works:
        1. For each target position, convert it to binary representation
        2. Apply X gates to flip bits that are 0 (transforming |target⟩ to |111...⟩)
        3. Apply multi-controlled Z gate to flip the phase
        4. Unapply the X gates to restore original state
        """
        if not self.target_positions:
            return
        
        for position in self.target_positions:
            if position >= self.total_states:
                continue
                
            # Convert position to binary with leading zeros
            binary_position = format(position, f"0{self.n_qubits}b")
            
            # Apply X gates where binary has '0'
            for i, bit in enumerate(binary_position):
                if bit == '0':
                    qc.x(i)
            
            # Apply multi-controlled Z gate (phase flip)
            if self.n_qubits > 1:
                qc.h(self.n_qubits - 1)
                qc.mcx(list(range(self.n_qubits - 1)), self.n_qubits - 1)
                qc.h(self.n_qubits - 1)
            else:
                qc.z(0)
            
            # Unapply the X gates
            for i, bit in enumerate(binary_position):
                if bit == '0':
                    qc.x(i)
    
    def _create_diffuser(self, qc: QuantumCircuit):
        """
        Creates the Grover diffusion operator.
        
        How it works:
        1. Apply H gates to all qubits
        2. Apply X gates to all qubits
        3. Apply multi-controlled Z gate
        4. Unapply X and H gates
        """
        if self.n_qubits == 1:
            qc.h(0)
            qc.z(0)
            qc.h(0)
            return
        
        # Apply Hadamard to all qubits
        qc.h(range(self.n_qubits))
        
        # Apply X to all qubits
        qc.x(range(self.n_qubits))
        
        # Multi-controlled Z gate
        qc.h(self.n_qubits - 1)
        qc.mcx(list(range(self.n_qubits - 1)), self.n_qubits - 1)
        qc.h(self.n_qubits - 1)
        
        # Unapply X and H gates
        qc.x(range(self.n_qubits))
        qc.h(range(self.n_qubits))
    
    def build_circuit(self) -> QuantumCircuit:
        """Build the complete Grover search circuit"""
        # Create quantum circuit
        circuit = QuantumCircuit(self.n_qubits, self.n_qubits)
        
        # STEP 1: Create uniform superposition over all positions
        circuit.h(range(self.n_qubits))
        
        # STEP 2: Apply Grover iterations
        for _ in range(self.iterations):
            self._create_oracle(circuit)
            self._create_diffuser(circuit)
        
        # STEP 3: Measure all qubits
        circuit.measure(range(self.n_qubits), range(self.n_qubits))
        
        return circuit
    
    def run_simulation(self, shots: int = 4096) -> Tuple[Dict[str, int], float]:
        """
        Run Grover's algorithm on quantum simulator
        
        Returns:
            Tuple of (measurement counts, execution time in ms)
        """
        # Build circuit
        circuit = self.build_circuit()
        
        # Start timing
        start_time = time.time()
        
        # Transpile and execute
        transpiled_circuit = transpile(circuit, self.simulator)
        result = self.simulator.run(transpiled_circuit, shots=shots).result()
        
        # End timing
        execution_time = (time.time() - start_time) * 1000
        
        # Get results
        counts = result.get_counts()
        
        return counts, execution_time
    
    def get_circuit_diagram(self) -> str:
        """Generate circuit visualization as base64 encoded image"""
        try:
            circuit = self.build_circuit()
            
            # Adjust fold for large circuits
            fold = 100 if circuit.size() > 100 else -1
            
            fig = circuit.draw('mpl', style='iqp', fold=fold, scale=0.8)
            
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            
            img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close(fig)
            
            return img_base64
        except Exception:
            return None
    
    def analyze_results(self, counts: Dict[str, int], shots: int) -> Dict[str, Any]:
        """Analyze quantum measurement results"""
        # Sort results by frequency
        sorted_results = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        
        # Calculate success rate
        success_count = 0
        top_measurements = []
        
        for state, count in sorted_results[:50]:  # Top 50 results
            try:
                # Convert from little-endian to big-endian
                position = int(state[::-1], 2)
            except ValueError:
                continue
                
            percentage = count / shots * 100
            is_target = position in self.target_positions
            
            if is_target:
                success_count += count
            
            top_measurements.append({
                "state": state,
                "position": position,
                "count": count,
                "percentage": round(percentage, 2),
                "is_target": is_target
            })
        
        success_rate = (success_count / shots) * 100 if shots > 0 else 0
        
        return {
            "top_measurements": top_measurements,
            "success_rate": round(success_rate, 2),
            "total_targets_found": len([m for m in top_measurements if m["is_target"]])
        }
    
    def get_info(self) -> Dict[str, Any]:
        """Get algorithm configuration information"""
        return {
            "n_qubits": self.n_qubits,
            "total_states": self.total_states,
            "num_targets": self.num_targets,
            "grover_iterations": self.iterations,
            "target_positions": self.target_positions[:20],
            "dna_size_analyzed": self.dna_size,
            "gene_length": len(self.target_gene),
            "target_found": len(self.target_positions) > 0,
            "classical_time_ms": self.dna_size / 1000000  # Approximate classical time
        }