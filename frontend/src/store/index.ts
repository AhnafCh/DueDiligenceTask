import { configureStore } from '@reduxjs/toolkit';
import documentReducer from './slices/documentSlice';
import projectReducer from './slices/projectSlice';
import answerReducer from './slices/answerSlice';
import evaluationReducer from './slices/evaluationSlice';

export const store = configureStore({
  reducer: {
    documents: documentReducer,
    projects: projectReducer,
    answers: answerReducer,
    evaluation: evaluationReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
