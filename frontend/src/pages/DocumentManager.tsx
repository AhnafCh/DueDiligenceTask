import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { fetchDocuments } from '../store/slices/documentSlice';
import { FileUploader } from '../components/Document/FileUploader';
import { RefreshCw, FileText, CheckCircle, Clock, AlertCircle } from 'lucide-react';

const DocumentManager: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { documents, loading, error } = useSelector((state: RootState) => state.documents);

  useEffect(() => {
    dispatch(fetchDocuments());
    // Poll for status updates every 5 seconds if there are documents processing
    const interval = setInterval(() => {
      dispatch(fetchDocuments());
    }, 5000);
    return () => clearInterval(interval);
  }, [dispatch]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'READY': return <CheckCircle size={18} color="var(--success)" />;
      case 'INDEXING': return <RefreshCw size={18} className="spin" color="var(--primary)" />;
      case 'UPLOADED': return <Clock size={18} color="var(--warning)" />;
      case 'ERROR': return <AlertCircle size={18} color="var(--error)" />;
      default: return null;
    }
  };

  return (
    <div className="fade-in">
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>Document Manager</h1>
        <button className="btn btn-secondary" onClick={() => dispatch(fetchDocuments())}>
          <RefreshCw size={16} style={{ marginRight: '0.5rem' }} /> Refresh
        </button>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem' }}>
        <div>
          <FileUploader />
        </div>

        <div className="card">
          <h2 style={{ marginBottom: '1.5rem' }}>Indexed Documents</h2>
          {loading && documents.length === 0 ? (
            <p>Loading documents...</p>
          ) : (
            <div className="document-list">
              {documents.length === 0 ? (
                <p style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>No documents uploaded yet.</p>
              ) : (
                documents.map((doc) => (
                  <div key={doc.id} className="document-item">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <div className="file-icon">
                        <FileText size={24} color="white" />
                      </div>
                      <div>
                        <div style={{ fontWeight: 600 }}>{doc.filename}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          {doc.file_type.toUpperCase()} • {new Date(doc.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      {getStatusIcon(doc.status)}
                      <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>
                        {doc.status}
                        {doc.chunk_count ? ` • ${doc.chunk_count} chunks` : ''}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentManager;
