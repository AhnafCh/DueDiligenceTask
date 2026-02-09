import React from 'react';
import { Citation } from '../../store/slices/answerSlice';
import { FileText } from 'lucide-react';

interface Props {
  citation: Citation | null;
}

export const CitationViewer: React.FC<Props> = ({ citation }) => {
  return (
    <div className="card citation-viewer" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <header style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <FileText size={20} color="var(--primary)" />
        <h3 style={{ fontSize: '1rem' }}>Source Document</h3>
      </header>
      
      {citation ? (
        <div className="fade-in" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <div className="citation-meta">
            <span>Page {citation.page_number}</span>
            <span className="dot" />
            <span>ID: {citation.document_id.slice(0, 8)}</span>
          </div>
          
          <div className="citation-highlight-box">
            <p className="citation-chunk-text">"{citation.chunk_text}"</p>
          </div>
          
          <div className="pdf-placeholder">
            <p>PDF Visual Highlight Placeholder</p>
            <div className="mock-bbox" />
          </div>
        </div>
      ) : (
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
          <p>Select a citation to view the source material</p>
        </div>
      )}
    </div>
  );
};
