import { EvaluationResponse } from './evaluation.model';
import { FormQuestionResponse } from './form-question.model';

export interface EvaluationAnswerItem {
  question_id: number;
  answer_text: string;
  score: number;
}

export interface EvaluationAnswerCreate {
  evaluation_id: number;
  answers: EvaluationAnswerItem[];
}

export interface EvaluationAnswerResponse extends EvaluationAnswerCreate {}

export interface EvaluationAnswerDetailResponse {
  evaluation: EvaluationResponse;
  question: FormQuestionResponse;
  answer_text: string;
  score: number;
}

export interface EvaluationAnswerCreateResponse {
  message: string;
  evaluation_question: EvaluationAnswerResponse;
}
