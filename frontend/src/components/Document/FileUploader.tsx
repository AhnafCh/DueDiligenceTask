import React, { useRef, useState } from 'react';
import { Upload, X, FileText } from 'lucide-react';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '../../store';
import { uploadDocument, indexDocument } from '../../store/slices/documentSlice';

export const FileUploader: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const dispatch = useDispatch<AppDispatch>();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    setUploading(true);
    try {
      for (const file of files) {
        const result = await dispatch(uploadDocument(file)).unwrap();
        // Automatically trigger indexing after upload
        await dispatch(indexDocument(result.id));
      }
      setFiles([]);
    } catch (err) {
      console.error('Upload failed', err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="card" style={{ marginBottom: '2rem' }}>
      <h2 style={{ marginBottom: '1rem' }}>Upload Documents</h2>
      <div 
        className="upload-zone"
        onClick={() => fileInputRef.current?.click()}
      >
        <Upload size={48} color="var(--text-muted)" />
        <p>Click or drag documents here to upload</p>
        <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>PDF, DOCX, XLSX, PPTX</span>
        <input 
          type="file" 
          multiple 
          hidden 
          ref={fileInputRef} 
          onChange={handleFileChange}
          accept=".pdf,.docx,.xlsx,.pptx"
        />
      </div>

      {files.length > 0 && (
        <div style={{ marginTop: '1.5rem' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {files.map((file, i) => (
              <div key={i} className="file-item">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <FileText size={20} color="var(--primary)" />
                  <span>{file.name}</span>
                </div>
                <button onClick={() => removeFile(i)} className="btn-icon">
                  <X size={18} />
                </button>
              </div>
            ))}
          </div>
          <button 
            onClick={handleUpload} 
            disabled={uploading} 
            className="btn btn-primary" 
            style={{ marginTop: '1rem', width: '100%' }}
          >
            {uploading ? 'Uploading & Indexing...' : `Upload ${files.length} Files`}
          </button>
        </div>
      )}
    </div>
  );
};
