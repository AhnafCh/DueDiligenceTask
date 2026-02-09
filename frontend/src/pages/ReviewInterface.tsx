import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { fetchProjectById } from '../store/slices/projectSlice';
import { fetchAnswer, Citation } from '../store/slices/answerSlice';
import { TreeNavigator } from '../components/Project/TreeNavigator';
import { AnswerCard } from '../components/Review/AnswerCard';
import { CitationViewer } from '../components/Review/CitationViewer';
import { ArrowLeft, ChevronLeft, ChevronRight, Share2, MoreVertical } from 'lucide-react';

const ReviewInterface: React.FC = () => {
  const { id, qid } = useParams<{ id: string; qid: string }>();
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { currentProject } = useSelector((state: RootState) => state.projects);
  const { currentAnswer, loading } = useSelector((state: RootState) => state.answers);
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);

  useEffect(() => {
    if (id && !currentProject) {
      dispatch(fetchProjectById(id));
    }
  }, [dispatch, id, currentProject]);

  useEffect(() => {
    if (qid) {
      dispatch(fetchAnswer(qid));
      setSelectedCitation(null);
    }
  }, [dispatch, qid]);

  const handleQuestionSelect = (newQid: string) => {
    navigate(`/projects/${id}/review/${newQid}`);
  };

  return (
    <div className="review-layout fade-in">
      <header className="review-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <button className="btn-icon" onClick={() => navigate(`/projects/${id}`)}>
            <ArrowLeft size={20} />
          </button>
          <div className="header-divider" />
          <div>
            <h2 style={{ fontSize: '1.125rem', marginBottom: '0.125rem' }}>{currentProject?.name}</h2>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Reviewing Question {qid?.slice(0, 8)}</p>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button className="btn btn-secondary btn-sm"><Share2 size={16} /> Export</button>
          <button className="btn btn-secondary btn-sm"><MoreVertical size={16} /></button>
        </div>
      </header>

      <div className="review-main">
        <aside className="review-sidebar card">
          <h4 style={{ marginBottom: '1rem', padding: '0 0.5rem' }}>Questions</h4>
          {currentProject && (
            <TreeNavigator 
              sections={currentProject.sections} 
              questions={currentProject.questions} 
              onSelectQuestion={handleQuestionSelect}
              selectedQuestionId={qid}
            />
          )}
        </aside>

        <section className="review-content">
          {loading ? (
            <div className="card" style={{ padding: '4rem', textAlign: 'center' }}>Loading answer...</div>
          ) : currentAnswer ? (
            <div className="review-split">
              <AnswerCard 
                answer={currentAnswer} 
                onCitationClick={(citation) => setSelectedCitation(citation)} 
              />
              <CitationViewer citation={selectedCitation} />
            </div>
          ) : (
            <div className="card" style={{ padding: '4rem', textAlign: 'center' }}>
              <p style={{ color: 'var(--text-muted)' }}>Generate an answer for this question to begin review.</p>
              <button className="btn btn-primary" style={{ marginTop: '1rem' }}>Generate Now</button>
            </div>
          )}
        </section>
      </div>

      <footer className="review-footer">
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button className="btn btn-secondary btn-sm"><ChevronLeft size={16} /> Previous Question</button>
          <button className="btn btn-secondary btn-sm">Next Question <ChevronRight size={16} /></button>
        </div>
      </footer>
    </div>
  );
};

export default ReviewInterface;
