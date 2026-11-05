import { Injectable, inject } from '@angular/core';
import {
  EvaluationQuestionCreate,
  EvaluationQuestionCreateResponse,
  EvaluationQuestionDetailResponse
} from '../../models/evaluation/evaluation-question.model';
import { ApiClientService } from '../api-client.service';

@Injectable({
  providedIn: 'root'
})
export class EvaluationQuestionService {
  private readonly api = inject(ApiClientService);

  create(payload: EvaluationQuestionCreate): Promise<EvaluationQuestionCreateResponse> {
    return this.api.post<EvaluationQuestionCreateResponse>('/evaluation_question/create', payload);
  }

  listByEvaluation(evaluationId: number): Promise<EvaluationQuestionDetailResponse[]> {
    return this.api.get<EvaluationQuestionDetailResponse[]>(`/evaluation_question/${evaluationId}`);
  }
}
