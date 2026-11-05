import { Injectable, inject } from '@angular/core';
import {
  EvaluationCreate,
  EvaluationCreateResponse,
  EvaluationDetailResponse,
  GenerateQuestionsResponse
} from '../../models/evaluation/evaluation.model';
import { PaginatedResponse } from '../../models/utils/pagination.model';
import { ApiClientService } from '../api-client.service';

@Injectable({
  providedIn: 'root'
})
export class EvaluationService {
  private readonly api = inject(ApiClientService);

  create(payload: EvaluationCreate): Promise<EvaluationCreateResponse> {
    return this.api.post<EvaluationCreateResponse>('/evaluation/create', payload);
  }

  listAll(
    page = 1,
    limit = 10,
    order: 'asc' | 'desc' = 'desc'
  ): Promise<PaginatedResponse<EvaluationDetailResponse>> {
    return this.api.get<PaginatedResponse<EvaluationDetailResponse>>('/evaluation/list', {
      params: { page, limit, order }
    });
  }

  listByUser(
    userId: number,
    silentError = false,
    order: 'asc' | 'desc' = 'desc'
  ): Promise<EvaluationDetailResponse[]> {
    return this.api.get<EvaluationDetailResponse[]>(`/evaluation/${userId}`, {
      params: { order },
      silentError
    });
  }

  generateQuestions(evaluationId: number): Promise<GenerateQuestionsResponse> {
    return this.api.post<GenerateQuestionsResponse>(
      `/evaluation/${evaluationId}/generate-questions`,
      {}
    );
  }
}
