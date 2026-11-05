import { Injectable, inject } from '@angular/core';
import {
  FormQuestionCreate,
  FormQuestionCreateResponse,
  FormQuestionDetailResponse
} from '../../models/evaluation/form-question.model';
import { PaginatedResponse } from '../../models/utils/pagination.model';
import { ApiClientService } from '../api-client.service';

@Injectable({
  providedIn: 'root'
})
export class FormQuestionService {
  private readonly api = inject(ApiClientService);

  list(page = 1, limit = 10): Promise<PaginatedResponse<FormQuestionDetailResponse>> {
    return this.api.get<PaginatedResponse<FormQuestionDetailResponse>>('/form_question/list', {
      params: { page, limit }
    });
  }

  create(payload: FormQuestionCreate): Promise<FormQuestionCreateResponse> {
    return this.api.post<FormQuestionCreateResponse>('/form_question/create', payload);
  }
}
