import React, { useState } from 'react';
import { ChevronRight, ChevronDown, FileQuestion, Hash } from 'lucide-react';

interface Question {
  id: string;
  text: string;
  section_id?: string;
}

interface Section {
  id: string;
  title: string;
}

interface TreeProps {
  sections: Section[];
  questions: Question[];
  onSelectQuestion: (questionId: string) => void;
  selectedQuestionId?: string;
}

export const TreeNavigator: React.FC<TreeProps> = ({ sections, questions, onSelectQuestion, selectedQuestionId }) => {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({});

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => ({ ...prev, [sectionId]: !prev[sectionId] }));
  };

  // Group questions by section
  const questionsBySection = questions.reduce((acc, q) => {
    const sid = q.section_id || 'root';
    if (!acc[sid]) acc[sid] = [];
    acc[sid].push(q);
    return acc;
  }, {} as Record<string, any[]>);

  return (
    <div className="tree-nav">
      {sections.map(section => (
        <div key={section.id} className="tree-section">
          <div 
            className="tree-section-header" 
            onClick={() => toggleSection(section.id)}
          >
            {expandedSections[section.id] ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            <span style={{ fontWeight: 600 }}>{section.title}</span>
          </div>
          
          {expandedSections[section.id] && (
            <div className="tree-question-list">
              {questionsBySection[section.id]?.map((question: Question) => (
                <div 
                  key={question.id} 
                  className={`tree-question-item ${selectedQuestionId === question.id ? 'active' : ''}`}
                  onClick={() => onSelectQuestion(question.id)}
                >
                  <FileQuestion size={14} />
                  <span>{question.text}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
      
      {/* Handle questions without a section if any */}
      {questionsBySection['root']?.length > 0 && (
        <div className="tree-question-list">
          {questionsBySection['root'].map((question: Question) => (
            <div 
              key={question.id} 
              className={`tree-question-item ${selectedQuestionId === question.id ? 'active' : ''}`}
              onClick={() => onSelectQuestion(question.id)}
            >
              <FileQuestion size={14} />
              <span>{question.text}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
