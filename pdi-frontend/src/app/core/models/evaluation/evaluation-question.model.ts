import { EvaluationResponse } from './evaluation.model';
import { FormQuestionResponse } from './form-question.model';

export interface EvaluationQuestionCreate {
  evaluation_id: number;
  question_id: number;
}

export interface EvaluationQuestionResponse extends EvaluationQuestionCreate {}

export interface EvaluationQuestionDetailResponse {
  evaluation: EvaluationResponse;
  question: FormQuestionResponse;
}

export interface EvaluationQuestionCreateResponse {
  message: string;
  evaluation_question: EvaluationQuestionResponse;
}
