# backend/create_dna_file.py
"""Create a valid DNA file for testing"""
import random

def create_valid_dna_file(filename="gen_bases.txt", size=400000):
    """Create a valid DNA sequence file"""
    bases = ['a', 'c', 'g', 't']
    dna_sequence = ''.join(random.choice(bases) for _ in range(size))
    
    with open(filename, 'w') as f:
        f.write(dna_sequence)
    
    print(f"✅ Created {filename} with {len(dna_sequence):,} bases")
    print(f"   First 100 bases: {dna_sequence[:100]}")
    return dna_sequence

if __name__ == "__main__":
    create_valid_dna_file()