import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { fetchProjectReport } from '../store/slices/evaluationSlice';
import { useParams } from 'react-router-dom';
import { BarChart3, Target, Zap, MessageSquare, Download, AlertCircle } from 'lucide-react';

const EvaluationPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const dispatch = useDispatch<AppDispatch>();
  const { report, loading, error } = useSelector((state: RootState) => state.evaluation);

  useEffect(() => {
    if (id) {
      dispatch(fetchProjectReport(id));
    }
  }, [dispatch, id]);

  const getScoreColor = (score: number) => {
    if (score > 0.8) return 'var(--success)';
    if (score > 0.6) return 'var(--warning)';
    return 'var(--error)';
  };

  if (loading) return <div className="fade-in" style={{ padding: '2rem' }}>Loading evaluation report...</div>;
  if (!report) return (
    <div className="card" style={{ padding: '4rem', textAlign: 'center', marginTop: '2rem' }}>
      <AlertCircle size={48} color="var(--border)" style={{ marginBottom: '1rem' }} />
      <p style={{ color: 'var(--text-muted)' }}>No evaluation data available for this project yet.</p>
    </div>
  );

  return (
    <div className="fade-in">
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1>Evaluation Dashboard</h1>
          <p style={{ color: 'var(--text-muted)' }}>Performance metrics comparing AI answers to Ground Truth.</p>
        </div>
        <button className="btn btn-secondary"><Download size={18} style={{ marginRight: '0.5rem' }} /> Export Report</button>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.5rem', marginBottom: '2.5rem' }}>
        <div className="card">
          <span className="stat-label">Overall Score</span>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
            <span className="stat-value" style={{ color: getScoreColor(report.average_score) }}>{(report.average_score * 100).toFixed(1)}%</span>
          </div>
        </div>
        <div className="card">
          <span className="stat-label">Total Evaluated</span>
          <span className="stat-value">{report.total_evaluated}</span>
        </div>
        <div className="card">
          <span className="stat-label">Semantic Match</span>
          <span className="stat-value">{(report.results.reduce((acc, r) => acc + r.semantic_similarity, 0) / report.results.length * 100).toFixed(1)}%</span>
        </div>
        <div className="card">
          <span className="stat-label">Agentic Quality</span>
          <span className="stat-value">{(report.results.reduce((acc, r) => acc + r.agentic_score, 0) / report.results.length).toFixed(1)}/10</span>
        </div>
      </div>

      <h2 style={{ marginBottom: '1.5rem' }}>Individual Assessments</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {report.results.map((result, i) => (
          <div key={result.id} className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.125rem' }}>Question {i + 1}</h3>
              <div 
                className="badge" 
                style={{ 
                  backgroundColor: getScoreColor(result.combined_score) + '20', 
                  color: getScoreColor(result.combined_score) 
                }}
              >
                Match: {(result.combined_score * 100).toFixed(0)}%
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '1.5rem' }}>
              <div className="diff-view">
                <span className="diff-label">AI Answer</span>
                <div className="diff-content ai">...</div>
              </div>
              <div className="diff-view">
                <span className="diff-label">Ground Truth</span>
                <div className="diff-content human">...</div>
              </div>
            </div>

            <div className="explanation-box">
              <h4 style={{ fontSize: '0.875rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Zap size={14} color="var(--primary)" /> LLM Judge Explanation
              </h4>
              <p style={{ fontSize: '0.875rem', lineHeight: '1.6' }}>{result.explanation}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default EvaluationPage;
