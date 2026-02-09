import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

export interface Project {
  id: string;
  name: string;
  description?: string;
  scope_type: 'ALL_DOCS' | 'SPECIFIC';
  status: 'DRAFT' | 'PROCESSING' | 'READY' | 'REVIEW' | 'COMPLETED' | 'OUTDATED';
  created_at: string;
  updated_at: string;
  document_count?: number;
}

export interface ProjectDetail extends Project {
  sections: any[];
  questions: any[];
}

interface ProjectState {
  projects: Project[];
  currentProject: ProjectDetail | null;
  loading: boolean;
  error: string | null;
}

const initialState: ProjectState = {
  projects: [],
  currentProject: null,
  loading: false,
  error: null,
};

export const fetchProjects = createAsyncThunk('projects/fetchAll', async () => {
  const response = await api.get('/list-projects');
  return response.data;
});

export const fetchProjectById = createAsyncThunk('projects/fetchById', async (id: string) => {
  const response = await api.get('/get-project-info', { params: { project_id: id } });
  return response.data;
});

export const createProject = createAsyncThunk('projects/create', async (project: Partial<Project>) => {
  const response = await api.post('/create-project', project);
  return response.data;
});

export const uploadQuestionnaire = createAsyncThunk(
  'projects/uploadQuestionnaire',
  async ({ projectId, file }: { projectId: string; file: File }) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post(`/${projectId}/questionnaire`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }
);

const projectSlice = createSlice({
  name: 'projects',
  initialState,
  reducers: {
    clearCurrentProject: (state) => {
      state.currentProject = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchProjects.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchProjects.fulfilled, (state, action) => {
        state.loading = false;
        state.projects = action.payload;
      })
      .addCase(fetchProjects.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch projects';
      })
      .addCase(fetchProjectById.fulfilled, (state, action) => {
        state.currentProject = action.payload;
      })
      .addCase(createProject.fulfilled, (state, action) => {
        state.projects.unshift(action.payload);
      });
  },
});

export const { clearCurrentProject } = projectSlice.actions;
export default projectSlice.reducer;
