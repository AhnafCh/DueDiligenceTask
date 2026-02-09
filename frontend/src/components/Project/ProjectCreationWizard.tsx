import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '../../store';
import { createProject, uploadQuestionnaire, fetchProjects } from '../../store/slices/projectSlice';
import { Plus, Upload, X } from 'lucide-react';

interface WizardProps {
  onClose: () => void;
}

export const ProjectCreationWizard: React.FC<WizardProps> = ({ onClose }) => {
  const [step, setStep] = useState(1);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [scopeType, setScopeType] = useState<'ALL_DOCS' | 'SPECIFIC'>('ALL_DOCS');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const dispatch = useDispatch<AppDispatch>();

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const project = await dispatch(createProject({ name, description, scope_type: scopeType })).unwrap();
      if (file) {
        await dispatch(uploadQuestionnaire({ projectId: project.id, file })).unwrap();
      }
      dispatch(fetchProjects());
      onClose();
    } catch (err) {
      console.error('Failed to create project', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content card">
        <header style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
          <h2>New Due Diligence Project</h2>
          <button className="btn-icon" onClick={onClose}><X size={24} /></button>
        </header>

        {step === 1 ? (
          <div className="fade-in">
            <div className="form-group">
              <label>Project Name</label>
              <input 
                type="text" 
                value={name} 
                onChange={(e) => setName(e.target.value)} 
                placeholder="e.g. Q1 2024 Compliance Review"
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Description (Optional)</label>
              <textarea 
                value={description} 
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Briefly describe the purpose of this project"
                className="form-input"
                rows={3}
              />
            </div>
            <div className="form-group">
              <label>Knowledge Scope</label>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <label className={`radio-btn ${scopeType === 'ALL_DOCS' ? 'active' : ''}`}>
                  <input type="radio" value="ALL_DOCS" checked={scopeType === 'ALL_DOCS'} onChange={() => setScopeType('ALL_DOCS')} hidden />
                  All Indexed Documents
                </label>
                <label className={`radio-btn ${scopeType === 'SPECIFIC' ? 'active' : ''}`}>
                  <input type="radio" value="SPECIFIC" checked={scopeType === 'SPECIFIC'} onChange={() => setScopeType('SPECIFIC')} hidden />
                  Specific Documents
                </label>
              </div>
            </div>
            <button className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }} onClick={() => setStep(2)}>
              Next: Upload Questionnaire
            </button>
          </div>
        ) : (
          <div className="fade-in">
            <p style={{ marginBottom: '1rem', color: 'var(--text-muted)' }}>Upload the questionnaire file (PDF or DOCX) to be answered.</p>
            <div 
              className="upload-zone"
              style={{ padding: '2rem' }}
              onClick={() => document.getElementById('q-file-input')?.click()}
            >
              {file ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Upload size={24} color="var(--primary)" />
                  <span style={{ fontWeight: 500 }}>{file.name}</span>
                </div>
              ) : (
                <>
                  <Upload size={40} color="var(--text-muted)" />
                  <p>Questionnaire File</p>
                </>
              )}
              <input 
                id="q-file-input"
                type="file" 
                accept=".pdf,.docx" 
                hidden 
                onChange={(e) => e.target.files && setFile(e.target.files[0])} 
              />
            </div>
            <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
              <button className="btn btn-secondary" style={{ flex: 1 }} onClick={() => setStep(1)}>Back</button>
              <button className="btn btn-primary" style={{ flex: 2 }} onClick={handleSubmit} disabled={loading || !name || !file}>
                {loading ? 'Creating...' : 'Create Project'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
