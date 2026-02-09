import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { fetchProjectById, clearCurrentProject } from '../store/slices/projectSlice';
import { TreeNavigator } from '../components/Project/TreeNavigator';
import { ArrowLeft, Play, Settings, MoreVertical, CheckCircle2, Clock, AlertTriangle } from 'lucide-react';

const ProjectDetailView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { currentProject, loading } = useSelector((state: RootState) => state.projects);

  useEffect(() => {
    if (id) {
      dispatch(fetchProjectById(id));
    }
    return () => {
      dispatch(clearCurrentProject());
    };
  }, [dispatch, id]);

  if (loading && !currentProject) return <div className="fade-in" style={{ padding: '2rem' }}>Loading project details...</div>;
  if (!currentProject) return <div style={{ padding: '2rem' }}>Project not found.</div>;

  return (
    <div className="fade-in">
      <header style={{ marginBottom: '2rem' }}>
        <button className="btn-icon" onClick={() => navigate('/projects')} style={{ marginBottom: '1rem', marginLeft: '-0.5rem' }}>
          <ArrowLeft size={20} /> Back to Projects
        </button>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
              <h1>{currentProject.name}</h1>
              <span className="badge" style={{ backgroundColor: '#ebf5ff', color: 'var(--primary)' }}>
                {currentProject.status}
              </span>
            </div>
            <p style={{ color: 'var(--text-muted)' }}>{currentProject.description}</p>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button className="btn btn-secondary"><Settings size={18} /></button>
            <button className="btn btn-primary">
              <Play size={18} style={{ marginRight: '0.5rem' }} /> Generate All Answers
            </button>
          </div>
        </div>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '2rem' }}>
        <aside className="card" style={{ padding: '1rem', height: 'fit-content', position: 'sticky', top: '2rem' }}>
          <h3 style={{ marginBottom: '1rem', fontSize: '1rem', padding: '0 0.5rem' }}>Questionnaire Structure</h3>
          <TreeNavigator 
            sections={currentProject.sections} 
            questions={currentProject.questions} 
            onSelectQuestion={(qid) => navigate(`/projects/${id}/review/${qid}`)} 
          />
        </aside>

        <section>
          <div className="card">
            <h3 style={{ marginBottom: '1.5rem' }}>Overview</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem' }}>
              <div className="stat-card">
                <span className="stat-label">Total Questions</span>
                <span className="stat-value">{currentProject.questions.length}</span>
              </div>
              <div className="stat-card">
                <span className="stat-label">Completed</span>
                <span className="stat-value" style={{ color: 'var(--success)' }}>0</span>
              </div>
              <div className="stat-card">
                <span className="stat-label">Documents</span>
                <span className="stat-value">{currentProject.document_count || 0}</span>
              </div>
            </div>

            <div style={{ marginTop: '2.5rem' }}>
              <h4 style={{ marginBottom: '1rem' }}>Project Roadmap</h4>
              <div className="roadmap">
                <div className="roadmap-step completed">
                  <CheckCircle2 size={24} />
                  <div>
                    <div className="step-title">Questionnaire Uploaded</div>
                    <div className="step-desc">Parsed into {currentProject.sections.length} sections</div>
                  </div>
                </div>
                <div className="roadmap-step active">
                  <Clock size={24} />
                  <div>
                    <div className="step-title">Answer Generation</div>
                    <div className="step-desc">Ready to trigger AI generation</div>
                  </div>
                </div>
                <div className="roadmap-step">
                  <AlertTriangle size={24} />
                  <div>
                    <div className="step-title">Human Review</div>
                    <div className="step-desc">Pending completion of generation</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default ProjectDetailView;
