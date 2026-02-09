import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import './styles/globals.css';
import DocumentManager from './pages/DocumentManager';
import ProjectDashboard from './pages/ProjectDashboard';
import ProjectDetailView from './pages/ProjectDetail';
import ReviewInterface from './pages/ReviewInterface';
import EvaluationPage from './pages/Evaluation';

// Lazy load pages later, for now placeholders
const Dashboard = () => <div>Dashboard</div>;
const Analytics = () => <div>Analytics</div>;

function App() {
  return (
    <Router>
      <div className="layout">
        <aside className="sidebar">
          <h1 style={{ marginBottom: '2rem', fontSize: '1.25rem' }}>QDiligence AI</h1>
          <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>Dashboard</NavLink>
            <NavLink to="/documents" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>Documents</NavLink>
            <NavLink to="/projects" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>Projects</NavLink>
            <NavLink to="/analytics" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>Analytics</NavLink>
          </nav>
        </aside>
        <main className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/documents" element={<DocumentManager />} />
            <Route path="/projects" element={<ProjectDashboard />} />
            <Route path="/projects/:id" element={<ProjectDetailView />} />
            <Route path="/projects/:id/review/:qid" element={<ReviewInterface />} />
            <Route path="/analytics" element={<EvaluationPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
