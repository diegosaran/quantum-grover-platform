import { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://quantum-grover-platform.onrender.com';

export default function Home() {
  const [searchItem, setSearchItem] = useState('agct');
  const [databaseSize, setDatabaseSize] = useState(100000);
  const [shots, setShots] = useState(4096);
  const [visualize, setVisualize] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [image, setImage] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [fileInfo, setFileInfo] = useState(null);

  const uploadFile = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/quantum/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setSessionId(response.data.session_id);
      setFileInfo({
        name: response.data.filename,
        bases: response.data.dna_sequence_length,
        first: response.data.first_100_bases
      });
      alert(`✅ File uploaded! ${response.data.dna_sequence_length.toLocaleString()} DNA bases loaded.`);
    } catch (error) {
      alert('❌ Upload error: ' + (error.response?.data?.detail || error.message));
    }
    setLoading(false);
  };

  const executeSearch = async () => {
    if (!searchItem) {
      alert('❌ Please enter a DNA sequence to search');
      return;
    }
    
    setLoading(true);
    setResult(null);
    try {
      const url = sessionId 
        ? `${API_BASE_URL}/quantum/simulate?session_id=${sessionId}`
        : `${API_BASE_URL}/quantum/simulate`;
      
      const response = await axios.post(url, {
        gene_sequence: searchItem.toLowerCase(),
        dna_size: databaseSize,
        shots: shots,
        visualize: visualize
      });
      setResult(response.data);
      
      if (response.data.circuit_image) {
        setImage(response.data.circuit_image);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('❌ Error: Backend is not running!');
    }
    setLoading(false);
  };

  const getSuccessRateClass = (rate) => {
    if (rate > 50) return { color: '#059669' };
    if (rate > 20) return { color: '#d97706' };
    return { color: '#dc2626' };
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>🧬 Quantum DNA Search</h1>
      <p style={styles.subtitle}>Grover's Algorithm - Quantum DNA Sequence Search</p>
      <p style={styles.complexity}>⚛️ Complexity: O(√N) Quantum vs O(N) Classical</p>

      {/* File Upload */}
      <div style={styles.card}>
        <h2 style={styles.cardTitle}>📤 1. Upload DNA File</h2>
        <label style={styles.fileLabel}>
          <input 
            type="file" 
            accept=".txt" 
            onChange={uploadFile}
            style={{ display: 'none' }}
          />
          <div style={styles.fileButton}>
            📁 Select .txt file
          </div>
        </label>
        {fileInfo && (
          <div style={styles.fileInfo}>
            <div>✅ File: <strong>{fileInfo.name}</strong></div>
            <div>📊 Bases: <strong>{fileInfo.bases.toLocaleString()}</strong></div>
            <div>🔬 First bases: <code>{fileInfo.first?.slice(0, 50)}...</code></div>
            <div>🆔 Session ID: <code>{sessionId?.slice(0, 8)}...</code></div>
          </div>
        )}
        {!fileInfo && (
          <div style={styles.aviso}>
            ⚠️ Please upload a DNA file first
          </div>
        )}
      </div>

      {/* Search Configuration */}
      <div style={styles.card}>
        <h2 style={styles.cardTitle}>🔍 2. Quantum Search Configuration</h2>
        
        <div style={styles.field}>
          <label style={styles.label}>DNA Sequence to Search:</label>
          <input 
            type="text" 
            value={searchItem} 
            onChange={(e) => setSearchItem(e.target.value.toLowerCase())}
            style={styles.input}
            placeholder="e.g., agct, ccc, atgc"
          />
          <div style={styles.hint}>Only letters A, C, G, T</div>
        </div>

        <div style={styles.field}>
          <label style={styles.label}>Database Size: {databaseSize.toLocaleString()} bases</label>
          <input 
            type="range" 
            min="1000" 
            max="200000" 
            step="1000"
            value={databaseSize} 
            onChange={(e) => setDatabaseSize(Number(e.target.value))}
            style={styles.range}
          />
        </div>

        <div style={styles.field}>
          <label style={styles.label}>Shots (Measurements): {shots}</label>
          <input 
            type="range" 
            min="1024" 
            max="8192" 
            step="1024"
            value={shots} 
            onChange={(e) => setShots(Number(e.target.value))}
            style={styles.range}
          />
        </div>

        <div style={styles.field}>
          <label style={styles.checkboxLabel}>
            <input 
              type="checkbox" 
              checked={visualize} 
              onChange={(e) => setVisualize(e.target.checked)}
              style={styles.checkbox}
            />
            🔬 Visualize Quantum Circuit
          </label>
        </div>

        <button 
          onClick={executeSearch} 
          disabled={loading || !sessionId}
          style={loading || !sessionId ? styles.buttonDisabled : styles.buttonPrimary}
        >
          {loading ? '⚛️ Running Grover...' : '🚀 Search with Grover'}
        </button>
      </div>

      {/* Results */}
      {result && (
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>📊 Search Results</h2>
          
          <div style={styles.resultsGrid}>
            <div style={styles.resultItem}>
              <div style={styles.resultValue}>{result.classical?.occurrences || 0}</div>
              <div style={styles.resultLabel}>Classical Occurrences</div>
            </div>
            <div style={styles.resultItem}>
              <div style={{...styles.resultValue, ...getSuccessRateClass(result.quantum?.success_rate || 0)}}>
                {result.quantum?.success_rate || 0}%
              </div>
              <div style={styles.resultLabel}>Quantum Success Rate</div>
            </div>
            <div style={styles.resultItem}>
              <div style={styles.resultValue}>{result.classical?.time_ms || 0} ms</div>
              <div style={styles.resultLabel}>Classical Time</div>
            </div>
            <div style={styles.resultItem}>
              <div style={styles.resultValue}>{result.quantum?.time_ms || 0} ms</div>
              <div style={styles.resultLabel}>Quantum Time</div>
            </div>
            <div style={styles.resultItem}>
              <div style={styles.resultValue}>{result.circuit?.grover_iterations || 0}</div>
              <div style={styles.resultLabel}>Grover Iterations</div>
            </div>
            <div style={styles.resultItem}>
              <div style={styles.resultValue}>{result.circuit?.n_qubits || 0}</div>
              <div style={styles.resultLabel}>Qubits Used</div>
            </div>
          </div>

          {/* Iterations Comparison */}
          <div style={styles.comparisonBox}>
            <h3>⚡ Iterations Comparison</h3>
            <div style={styles.comparisonRow}>
              <div style={styles.comparisonCol}>
                <div style={styles.comparisonNumber}>{result.circuit?.grover_iterations || 0}</div>
                <div>Quantum Iterations (Grover)</div>
                <div style={styles.comparisonFormula}>O(√N) = √{result.dna?.size_analyzed?.toLocaleString() || databaseSize}</div>
              </div>
              <div style={styles.comparisonCol}>
                <div style={styles.comparisonNumber}>{result.dna?.size_analyzed?.toLocaleString() || databaseSize}</div>
                <div>Classical Iterations (Linear)</div>
                <div style={styles.comparisonFormula}>O(N) = N bases</div>
              </div>
            </div>
          </div>

          <div style={styles.resultSection}>
            <h3>🎯 Target Positions Found (Classical Search)</h3>
            <div style={styles.positionsBox}>
              {result.classical?.positions && result.classical.positions.length > 0 ? (
                <>
                  <div><strong>Total:</strong> {result.classical.occurrences} occurrences</div>
                  <div><strong>First 20 positions:</strong></div>
                  <code style={styles.resultCode}>
                    {result.classical.positions.slice(0, 20).join(', ')}
                    {result.classical.occurrences > 20 && '...'}
                  </code>
                </>
              ) : (
                <div>No occurrences found</div>
              )}
            </div>
          </div>

          <div style={styles.resultSection}>
            <h3>⚛️ Top Quantum Measurements</h3>
            <table style={styles.table}>
              <thead>
                <tr style={styles.tableHeader}>
                  <th>State</th>
                  <th>Position</th>
                  <th>Count</th>
                  <th>%</th>
                  <th>Target</th>
                </tr>
              </thead>
              <tbody>
                {result.quantum?.top_measurements?.map((m, i) => (
                  <tr key={i} style={m.is_target ? styles.targetRow : {}}>
                    <td><code>{m.state}</code></td>
                    <td>{m.position}</td>
                    <td>{m.count}</td>
                    <td>{m.percentage}%</td>
                    <td>{m.is_target ? '⭐ Yes' : '❌ No'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {image && (
            <div style={styles.resultSection}>
              <h3>🔬 Grover's Quantum Circuit</h3>
              <img 
                src={`data:image/png;base64,${image}`} 
                style={styles.image}
                alt="Grover Circuit"
              />
            </div>
          )}
        </div>
      )}

      <div style={styles.status}>
        🟢 Backend: {API_BASE_URL} | Grover's Algorithm | Quantum Speedup O(√N)
      </div>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: 1000,
    margin: '0 auto',
    padding: '20px',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    backgroundColor: '#f5f5f5',
    minHeight: '100vh'
  },
  title: {
    color: '#4f46e5',
    marginBottom: '5px',
    fontSize: '28px',
    textAlign: 'center'
  },
  subtitle: {
    color: '#666',
    marginBottom: '5px',
    fontSize: '16px',
    textAlign: 'center'
  },
  complexity: {
    color: '#059669',
    marginBottom: '30px',
    fontSize: '14px',
    textAlign: 'center',
    fontWeight: 'bold'
  },
  cardTitle: {
    marginTop: '0',
    marginBottom: '20px',
    color: '#333',
    fontSize: '20px'
  },
  card: {
    backgroundColor: '#fff',
    padding: '25px',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
    marginBottom: '20px'
  },
  field: {
    marginBottom: '20px'
  },
  label: {
    display: 'block',
    marginBottom: '8px',
    fontWeight: '600',
    color: '#333'
  },
  input: {
    width: '100%',
    padding: '10px',
    borderRadius: '6px',
    border: '1px solid #ddd',
    fontSize: '14px',
    fontFamily: 'monospace'
  },
  hint: {
    fontSize: '12px',
    color: '#666',
    marginTop: '5px'
  },
  range: {
    width: '100%'
  },
  checkboxLabel: {
    display: 'flex',
    alignItems: 'center',
    cursor: 'pointer'
  },
  checkbox: {
    marginRight: '10px',
    width: '18px',
    height: '18px'
  },
  fileLabel: {
    cursor: 'pointer',
    display: 'inline-block'
  },
  fileButton: {
    padding: '12px 24px',
    backgroundColor: '#10b981',
    color: '#fff',
    borderRadius: '6px',
    textAlign: 'center',
    cursor: 'pointer',
    fontWeight: '600',
    display: 'inline-block'
  },
  fileInfo: {
    marginTop: '15px',
    padding: '15px',
    backgroundColor: '#ecfdf5',
    borderRadius: '8px',
    fontSize: '14px'
  },
  aviso: {
    marginTop: '15px',
    padding: '10px',
    backgroundColor: '#fef3c7',
    borderRadius: '6px',
    fontSize: '13px',
    color: '#92400e'
  },
  buttonPrimary: {
    width: '100%',
    padding: '12px',
    backgroundColor: '#4f46e5',
    color: '#fff',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: '600'
  },
  buttonDisabled: {
    width: '100%',
    padding: '12px',
    backgroundColor: '#a5b4fc',
    color: '#fff',
    border: 'none',
    borderRadius: '6px',
    cursor: 'not-allowed',
    fontSize: '16px',
    fontWeight: '600'
  },
  resultsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '15px',
    marginBottom: '30px'
  },
  resultItem: {
    textAlign: 'center',
    padding: '15px',
    backgroundColor: '#f9fafb',
    borderRadius: '8px'
  },
  resultValue: {
    fontSize: '28px',
    fontWeight: 'bold',
    color: '#4f46e5'
  },
  resultLabel: {
    fontSize: '12px',
    color: '#666',
    marginTop: '5px'
  },
  comparisonBox: {
    marginTop: '25px',
    padding: '20px',
    backgroundColor: '#f9fafb',
    borderRadius: '8px',
    textAlign: 'center'
  },
  comparisonRow: {
    display: 'flex',
    justifyContent: 'center',
    gap: '40px',
    marginTop: '15px',
    flexWrap: 'wrap'
  },
  comparisonCol: {
    textAlign: 'center',
    minWidth: '200px'
  },
  comparisonNumber: {
    fontSize: '36px',
    fontWeight: 'bold',
    color: '#4f46e5',
    marginBottom: '5px'
  },
  comparisonFormula: {
    fontSize: '12px',
    color: '#666',
    fontFamily: 'monospace',
    marginTop: '5px'
  },
  resultSection: {
    marginTop: '25px'
  },
  positionsBox: {
    backgroundColor: '#f9fafb',
    padding: '15px',
    borderRadius: '8px',
    fontFamily: 'monospace',
    fontSize: '13px'
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    fontSize: '13px'
  },
  tableHeader: {
    backgroundColor: '#f3f4f6',
    borderBottom: '2px solid #e5e7eb'
  },
  targetRow: {
    backgroundColor: '#f0fdf4'
  },
  resultCode: {
    fontFamily: 'monospace',
    fontSize: '12px',
    display: 'block',
    marginTop: '8px',
    wordBreak: 'break-all'
  },
  image: {
    maxWidth: '100%',
    height: 'auto',
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    marginTop: '15px'
  },
  status: {
    marginTop: '20px',
    padding: '15px',
    backgroundColor: '#ecfdf5',
    borderRadius: '8px',
    color: '#059669',
    fontWeight: '500',
    textAlign: 'center'
  }
};