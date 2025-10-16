import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Upload, Search, Download, Activity, Image as ImageIcon } from 'lucide-react';
import './index.css';

const API_BASE = 'http://localhost:8000';

function App() {
  const [activeTab, setActiveTab] = useState('upload');
  const [chips, setChips] = useState([]);
  const [className, setClassName] = useState('');
  const [indexPath, setIndexPath] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState({ embedder_loaded: false, index_loaded: false });

  useEffect(() => {
    checkStatus();
  }, []);

  const checkStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE}/status`);
      setStatus(response.data);
    } catch (error) {
      console.error('Failed to check status:', error);
    }
  };

  const handleFileUpload = async (event) => {
    const files = event.target.files;
    
    for (let file of files) {
      const formData = new FormData();
      formData.append('file', file);
      
      try {
        const response = await axios.post(`${API_BASE}/upload_chip`, formData);
        setChips([...chips, response.data]);
      } catch (error) {
        console.error('Upload failed:', error);
        alert('Failed to upload chip');
      }
    }
  };

  const handleLoadIndex = async () => {
    if (!indexPath) {
      alert('Please enter index path');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('index_dir', indexPath);
      
      const response = await axios.post(`${API_BASE}/load_index`, formData);
      alert(`Index loaded: ${response.data.total_vectors} vectors`);
      checkStatus();
    } catch (error) {
      console.error('Failed to load index:', error);
      alert('Failed to load index');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (chips.length === 0) {
      alert('Please upload at least one chip');
      return;
    }

    if (!className) {
      alert('Please enter class name');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/search`, {
        chip_ids: chips.map(c => c.chip_id),
        class_name: className,
        top_k: 100,
        similarity_threshold: 0.7,
        nms_threshold: 0.5
      });
      
      setResults(response.data);
      setActiveTab('results');
    } catch (error) {
      console.error('Search failed:', error);
      alert('Search failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    if (!results) return;

    try {
      const response = await axios.post(
        `${API_BASE}/export_submission`,
        results.detections,
        {
          responseType: 'blob',
          params: { team_name: 'TeamName' }
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `submission_${Date.now()}.txt`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Export failed:', error);
      alert('Failed to export results');
    }
  };

  const removeChip = (chipId) => {
    setChips(chips.filter(c => c.chip_id !== chipId));
  };

  const getScoreClass = (score) => {
    if (score >= 0.8) return 'score-high';
    if (score >= 0.6) return 'score-medium';
    return 'score-low';
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <Activity size={32} color="#60a5fa" />
            <h1>PS-03 Visual Search</h1>
          </div>
          <div className="status">
            <div className="status-badge">
              Embedder: {status.embedder_loaded ? '✓' : '✗'}
            </div>
            <div className="status-badge">
              Index: {status.index_loaded ? '✓' : '✗'}
            </div>
          </div>
        </div>
      </header>

      <div className="container">
        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'upload' ? 'active' : ''}`}
            onClick={() => setActiveTab('upload')}
          >
            <Upload size={18} />
            Upload Chips
          </button>
          <button 
            className={`tab ${activeTab === 'search' ? 'active' : ''}`}
            onClick={() => setActiveTab('search')}
          >
            <Search size={18} />
            Search
          </button>
          <button 
            className={`tab ${activeTab === 'results' ? 'active' : ''}`}
            onClick={() => setActiveTab('results')}
            disabled={!results}
          >
            <ImageIcon size={18} />
            Results ({results?.total_count || 0})
          </button>
        </div>

        {activeTab === 'upload' && (
          <div className="panel">
            <h2 style={{ marginBottom: '1.5rem' }}>Upload Query Chips</h2>
            
            <div 
              className="upload-zone"
              onClick={() => document.getElementById('fileInput').click()}
            >
              <Upload size={48} color="#60a5fa" style={{ margin: '0 auto' }} />
              <p style={{ marginTop: '1rem', fontSize: '1.125rem', fontWeight: 500 }}>
                Click to upload TIFF chips
              </p>
              <p style={{ marginTop: '0.5rem', color: '#94a3b8', fontSize: '0.875rem' }}>
                Support for 4-band multispectral imagery
              </p>
              <input
                id="fileInput"
                type="file"
                multiple
                accept=".tif,.tiff"
                onChange={handleFileUpload}
                style={{ display: 'none' }}
              />
            </div>

            {chips.length > 0 && (
              <div style={{ marginTop: '2rem' }}>
                <h3 style={{ marginBottom: '1rem' }}>Uploaded Chips ({chips.length})</h3>
                <div className="chip-list">
                  {chips.map((chip) => (
                    <div key={chip.chip_id} className="chip-item">
                      <img 
                        src={`${API_BASE}/preview/${chip.chip_id}`} 
                        alt={chip.filename}
                      />
                      <button 
                        className="chip-remove"
                        onClick={() => removeChip(chip.chip_id)}
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div style={{ marginTop: '2rem' }}>
              <h3 style={{ marginBottom: '1rem' }}>Load FAISS Index</h3>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <input
                  className="input"
                  type="text"
                  placeholder="Path to index directory (e.g., cache/indexes)"
                  value={indexPath}
                  onChange={(e) => setIndexPath(e.target.value)}
                />
                <button 
                  className="button button-primary"
                  onClick={handleLoadIndex}
                  disabled={loading}
                >
                  Load Index
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'search' && (
          <div className="panel">
            <h2 style={{ marginBottom: '1.5rem' }}>Configure Search</h2>
            
            <div className="grid">
              <div className="card">
                <h3 style={{ marginBottom: '1rem' }}>Query Chips</h3>
                <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>
                  {chips.length} chip(s) loaded
                </p>
              </div>

              <div className="card">
                <h3 style={{ marginBottom: '1rem' }}>Class Name</h3>
                <input
                  className="input"
                  type="text"
                  placeholder="e.g., Solar_Panel"
                  value={className}
                  onChange={(e) => setClassName(e.target.value)}
                />
              </div>
            </div>

            <div style={{ marginTop: '2rem', textAlign: 'center' }}>
              <button
                className="button button-primary"
                onClick={handleSearch}
                disabled={loading || chips.length === 0 || !className}
                style={{ fontSize: '1rem', padding: '1rem 2rem' }}
              >
                {loading ? (
                  <>
                    <div className="spinner" style={{ width: 20, height: 20 }} />
                    Searching...
                  </>
                ) : (
                  <>
                    <Search size={20} />
                    Run Search
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {activeTab === 'results' && results && (
          <div className="panel">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <div>
                <h2>Search Results</h2>
                <p style={{ color: '#94a3b8', marginTop: '0.5rem' }}>
                  {results.total_count} detections in {results.images_count} images
                </p>
              </div>
              <button 
                className="button button-primary"
                onClick={handleExport}
              >
                <Download size={18} />
                Export Submission
              </button>
            </div>

            <div className="results-grid">
              {results.detections.slice(0, 100).map((det, idx) => (
                <div key={idx} className="detection-card">
                  <div className="detection-info">
                    <strong>{det.target_filename}</strong>
                    <div>Class: {det.class_name}</div>
                    <div>
                      Box: [{det.x_min}, {det.y_min}, {det.x_max}, {det.y_max}]
                    </div>
                    <span className={`score-badge ${getScoreClass(det.score)}`}>
                      Score: {det.score.toFixed(3)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {loading && (
          <div className="loading">
            <div className="spinner" />
            <p>Processing...</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
