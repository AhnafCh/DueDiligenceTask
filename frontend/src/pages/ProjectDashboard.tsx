import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { fetchProjects } from '../store/slices/projectSlice';
import { ProjectCreationWizard } from '../components/Project/ProjectCreationWizard';
import { Plus, Search, Filter, ArrowRight, Clock, FileCheck, Layers } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const ProjectDashboard: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { projects, loading } = useSelector((state: RootState) => state.projects);
  const [showWizard, setShowWizard] = useState(false);

  useEffect(() => {
    dispatch(fetchProjects());
  }, [dispatch]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'READY': return 'var(--success)';
      case 'PROCESSING': return 'var(--primary)';
      case 'REVIEW': return 'var(--warning)';
      case 'COMPLETED': return '#6366f1';
      case 'OUTDATED': return 'var(--error)';
      default: return 'var(--text-muted)';
    }
  };

  return (
    <div className="fade-in">
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1>Due Diligence Projects</h1>
          <p style={{ color: 'var(--text-muted)' }}>Manage and monitor your AI-assisted questionnaire completions.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowWizard(true)}>
          <Plus size={18} style={{ marginRight: '0.5rem' }} /> Create New Project
        </button>
      </header>

      <div className="card" style={{ marginBottom: '2rem', display: 'flex', gap: '1rem', padding: '1rem' }}>
        <div style={{ flex: 1, position: 'relative' }}>
          <Search size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input type="text" placeholder="Search projects..." className="form-input" style={{ paddingLeft: '2.5rem' }} />
        </div>
        <button className="btn btn-secondary"><Filter size={18} /> Filter</button>
      </div>

      {loading && projects.length === 0 ? (
        <p>Loading projects...</p>
      ) : (
        <div className="project-grid">
          {projects.length === 0 ? (
            <div className="card" style={{ textAlign: 'center', padding: '4rem', gridColumn: '1 / -1' }}>
              <Layers size={48} color="var(--border)" style={{ marginBottom: '1rem' }} />
              <p style={{ color: 'var(--text-muted)' }}>No projects yet. Create your first project to get started.</p>
            </div>
          ) : (
            projects.map((project) => (
              <div key={project.id} className="card project-card" onClick={() => navigate(`/projects/${project.id}`)}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                  <span className="badge" style={{ backgroundColor: getStatusColor(project.status) + '20', color: getStatusColor(project.status) }}>
                    {project.status}
                  </span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <Clock size={12} /> {new Date(project.created_at).toLocaleDateString()}
                  </span>
                </div>
                <h3 style={{ marginBottom: '0.5rem' }}>{project.name}</h3>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '1.5rem', minHeight: '3rem' }}>
                  {project.description || 'No description provided.'}
                </p>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--border)', paddingTop: '1rem' }}>
                  <div style={{ fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <FileCheck size={16} color="var(--text-muted)" />
                    <span>Scope: {project.scope_type}</span>
                  </div>
                  <ArrowRight size={18} color="var(--primary)" />
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {showWizard && <ProjectCreationWizard onClose={() => setShowWizard(false)} />}
    </div>
  );
};

export default ProjectDashboard;
