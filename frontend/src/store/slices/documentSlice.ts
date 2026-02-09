import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

export interface Document {
  id: string;
  filename: string;
  file_type: string;
  status: 'UPLOADED' | 'INDEXING' | 'READY' | 'ERROR';
  chunk_count?: number;
  indexed_at?: string;
  error_message?: string;
  created_at: string;
}

interface DocumentState {
  documents: Document[];
  loading: boolean;
  error: string | null;
}

const initialState: DocumentState = {
  documents: [],
  loading: false,
  error: null,
};

export const fetchDocuments = createAsyncThunk('documents/fetchAll', async () => {
  const response = await api.get('/documents');
  return response.data;
});

export const uploadDocument = createAsyncThunk(
  'documents/upload',
  async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/upload-document', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }
);

export const indexDocument = createAsyncThunk(
  'documents/index',
  async (documentId: string) => {
    const response = await api.post('/index-document-async', null, {
      params: { document_id: documentId },
    });
    return response.data;
  }
);

const documentSlice = createSlice({
  name: 'documents',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchDocuments.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchDocuments.fulfilled, (state, action) => {
        state.loading = false;
        state.documents = action.payload;
      })
      .addCase(fetchDocuments.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch documents';
      })
      .addCase(uploadDocument.fulfilled, (state, action) => {
        state.documents.unshift(action.payload);
      });
  },
});

export default documentSlice.reducer;
