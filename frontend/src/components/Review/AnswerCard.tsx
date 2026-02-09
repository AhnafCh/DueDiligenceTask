import React, { useState } from 'react';
import { Answer, Citation } from '../../store/slices/answerSlice';
import { Check, X, Edit3, MessageSquare, AlertCircle, ExternalLink } from 'lucide-react';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '../../store';
import { confirmAnswer, rejectAnswer, updateAnswer, refineAnswer } from '../../store/slices/answerSlice';

interface Props {
  answer: Answer;
  onCitationClick: (citation: Citation) => void;
}

export const AnswerCard: React.FC<Props> = ({ answer, onCitationClick }) => {
  const dispatch = useDispatch<AppDispatch>();
  const [isEditing, setIsEditing] = useState(false);
  const [editedText, setEditedText] = useState(answer.text);
  const [feedback, setFeedback] = useState('');
  const [showRefine, setShowRefine] = useState(false);

  const handleSave = () => {
    dispatch(updateAnswer({ answerId: answer.id, text: editedText }));
    setIsEditing(false);
  };

  const handleRefine = () => {
    dispatch(refineAnswer({ answerId: answer.id, feedback }));
    setShowRefine(false);
    setFeedback('');
  };

  const getConfidenceColor = (score: number) => {
    if (score > 0.8) return 'var(--success)';
    if (score > 0.5) return 'var(--warning)';
    return 'var(--error)';
  };

  return (
    <div className="card answer-card fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div 
            className="confidence-orb" 
            style={{ backgroundColor: getConfidenceColor(answer.confidence_score) }}
          />
          <span style={{ fontWeight: 600 }}>{(answer.confidence_score * 100).toFixed(0)}% Confidence</span>
          <span className="badge" style={{ backgroundColor: '#f1f5f9', color: 'var(--text-muted)' }}>{answer.status}</span>
        </div>
        {!isEditing && (
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button className="btn btn-secondary btn-sm" onClick={() => setIsEditing(true)}>
              <Edit3 size={14} style={{ marginRight: '0.25rem' }} /> Edit
            </button>
            <button className="btn btn-secondary btn-sm" onClick={() => setShowRefine(true)}>
              <MessageSquare size={14} style={{ marginRight: '0.25rem' }} /> Refine
            </button>
          </div>
        )}
      </div>

      {isEditing ? (
        <div className="fade-in">
          <textarea 
            className="form-input" 
            rows={10} 
            value={editedText} 
            onChange={(e) => setEditedText(e.target.value)}
            style={{ marginBottom: '1rem' }}
          />
          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
            <button className="btn btn-secondary" onClick={() => setIsEditing(false)}>Cancel</button>
            <button className="btn btn-primary" onClick={handleSave}>Save Override</button>
          </div>
        </div>
      ) : (
        <div className="answer-content">
          <p style={{ whiteSpace: 'pre-wrap' }}>{answer.text}</p>
        </div>
      )}

      {showRefine && (
        <div className="refine-box fade-in">
          <h4 style={{ marginBottom: '0.5rem' }}>Provide feedback to AI</h4>
          <textarea 
            className="form-input" 
            placeholder="e.g. Include more details about the Q3 compliance audit..." 
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            rows={3}
          />
          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem', justifyContent: 'flex-end' }}>
            <button className="btn btn-secondary btn-sm" onClick={() => setShowRefine(false)}>Cancel</button>
            <button className="btn btn-primary btn-sm" onClick={handleRefine} disabled={!feedback}>Send Feedback</button>
          </div>
        </div>
      )}

      <div className="citations-section">
        <h4 style={{ marginBottom: '0.75rem', fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <AlertCircle size={14} /> Citations
        </h4>
        <div className="citation-list">
          {answer.citations.map((citation, i) => (
            <div 
              key={citation.id} 
              className="citation-tag"
              onClick={() => onCitationClick(citation)}
            >
              <span className="citation-num">{i + 1}</span>
              <span className="citation-text">Page {citation.page_number}</span>
              <ExternalLink size={12} />
            </div>
          ))}
        </div>
      </div>

      <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem', borderTop: '1px solid var(--border)', paddingTop: '1.5rem' }}>
        <button className="btn btn-secondary" style={{ flex: 1, color: 'var(--error)', borderColor: 'var(--error)' }} onClick={() => dispatch(rejectAnswer({ answerId: answer.id, reason: 'Manual Rejection' }))}>
          <X size={18} style={{ marginRight: '0.5rem' }} /> Reject
        </button>
        <button className="btn btn-primary" style={{ flex: 2, backgroundColor: 'var(--success)' }} onClick={() => dispatch(confirmAnswer({ answerId: answer.id }))}>
          <Check size={18} style={{ marginRight: '0.5rem' }} /> Approve Answer
        </button>
      </div>
    </div>
  );
};
