import { Injectable, inject } from '@angular/core';
import {
  EvaluationAnswerCreate,
  EvaluationAnswerCreateResponse,
  EvaluationAnswerDetailResponse
} from '../../models/evaluation/evaluation-answer.model';
import { PaginatedResponse } from '../../models/utils/pagination.model';
import { ApiClientService } from '../api-client.service';

@Injectable({
  providedIn: 'root'
})
export class EvaluationAnswerService {
  private readonly api = inject(ApiClientService);

  create(payload: EvaluationAnswerCreate): Promise<EvaluationAnswerCreateResponse> {
    return this.api.post<EvaluationAnswerCreateResponse>('/evaluation_answer/create', payload);
  }

  async listByEvaluation(
    evaluationId: number,
    silentError = false
  ): Promise<EvaluationAnswerDetailResponse[]> {
    const res = await this.api.get<
      PaginatedResponse<EvaluationAnswerDetailResponse> | EvaluationAnswerDetailResponse[]
    >(`/evaluation_answer/${evaluationId}`, { silentError });
    return Array.isArray(res) ? res : (res.items ?? []);
  }
}
