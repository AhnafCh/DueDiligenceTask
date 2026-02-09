import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

export interface Citation {
  id: string;
  chunk_text: string;
  page_number: number;
  bounding_box?: any;
  document_id: string;
}

export interface Answer {
  id: string;
  question_id: string;
  text: string;
  confidence_score: number;
  is_answerable: boolean;
  status: 'PENDING' | 'CONFIRMED' | 'REJECTED' | 'MANUAL_UPDATED' | 'MISSING_DATA';
  review_comment?: string;
  created_by: 'AI' | 'HUMAN';
  citations: Citation[];
  processing_metadata?: any;
}

interface AnswerState {
  currentAnswer: Answer | null;
  loading: boolean;
  error: string | null;
}

const initialState: AnswerState = {
  currentAnswer: null,
  loading: false,
  error: null,
};

export const fetchAnswer = createAsyncThunk('answers/fetch', async (answerId: string) => {
  const response = await api.get('/get-answer', { params: { answer_id: answerId } });
  return response.data;
});

export const confirmAnswer = createAsyncThunk(
  'answers/confirm',
  async ({ answerId, comment }: { answerId: string; comment?: string }) => {
    const response = await api.post('/confirm-answer', { comment }, { params: { answer_id: answerId } });
    return response.data;
  }
);

export const rejectAnswer = createAsyncThunk(
  'answers/reject',
  async ({ answerId, reason }: { answerId: string; reason: string }) => {
    const response = await api.post('/reject-answer', { reason }, { params: { answer_id: answerId } });
    return response.data;
  }
);

export const updateAnswer = createAsyncThunk(
  'answers/update',
  async ({ answerId, text }: { answerId: string; text: string }) => {
    const response = await api.post('/update-answer', { text }, { params: { answer_id: answerId } });
    return response.data;
  }
);

export const refineAnswer = createAsyncThunk(
  'answers/refine',
  async ({ answerId, feedback }: { answerId: string; feedback: string }) => {
    const response = await api.post(`/${answerId}/refine`, null, { params: { feedback } });
    return response.data;
  }
);

const answerSlice = createSlice({
  name: 'answers',
  initialState,
  reducers: {
    clearCurrentAnswer: (state) => {
      state.currentAnswer = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAnswer.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchAnswer.fulfilled, (state, action) => {
        state.loading = false;
        state.currentAnswer = action.payload;
      })
      .addCase(fetchAnswer.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch answer';
      })
      .addCase(confirmAnswer.fulfilled, (state, action) => {
        state.currentAnswer = action.payload;
      })
      .addCase(rejectAnswer.fulfilled, (state, action) => {
        state.currentAnswer = action.payload;
      })
      .addCase(updateAnswer.fulfilled, (state, action) => {
        state.currentAnswer = action.payload;
      })
      .addCase(refineAnswer.fulfilled, (state, action) => {
        state.currentAnswer = action.payload;
      });
  },
});

export const { clearCurrentAnswer } = answerSlice.actions;
export default answerSlice.reducer;
