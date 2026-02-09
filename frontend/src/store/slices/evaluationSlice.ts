import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

export interface EvaluationResult {
  id: string;
  ai_answer_id: string;
  semantic_similarity: number;
  keyword_overlap: number;
  bleu_score: number;
  agentic_score: number;
  combined_score: number;
  explanation: string;
  created_at: string;
}

export interface EvaluationReport {
  project_id: string;
  average_score: number;
  total_evaluated: number;
  results: EvaluationResult[];
}

interface EvaluationState {
  report: EvaluationReport | null;
  loading: boolean;
  error: string | null;
}

const initialState: EvaluationState = {
  report: null,
  loading: false,
  error: null,
};

export const fetchProjectReport = createAsyncThunk(
  'evaluation/fetchReport',
  async (projectId: string) => {
    const response = await api.get('/get-project-evaluation', { params: { project_id: projectId } });
    return response.data;
  }
);

export const evaluateAnswer = createAsyncThunk(
  'evaluation/evaluate',
  async ({ aiAnswerId, humanAnswerText }: { aiAnswerId: string; humanAnswerText: string }) => {
    const response = await api.post('/compare', { ai_answer_id: aiAnswerId, human_answer_text: humanAnswerText });
    return response.data;
  }
);

const evaluationSlice = createSlice({
  name: 'evaluation',
  initialState,
  reducers: {
    clearReport: (state) => {
      state.report = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchProjectReport.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchProjectReport.fulfilled, (state, action) => {
        state.loading = false;
        state.report = action.payload;
      })
      .addCase(fetchProjectReport.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch evaluation report';
      });
  },
});

export const { clearReport } = evaluationSlice.actions;
export default evaluationSlice.reducer;
