import { CompetenceResponse } from '../competence/competence.model';

export interface FormQuestionCreate {
  question_text: string;
  competence_id: number;
}

export interface FormQuestionResponse extends FormQuestionCreate {
  id: number;
}

export interface FormQuestionDetailResponse {
  id: number;
  question_text: string;
  competence: CompetenceResponse;
}

export interface FormQuestionCreateResponse {
  message: string;
  form_question: FormQuestionResponse;
}
