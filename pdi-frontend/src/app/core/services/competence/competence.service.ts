import { Injectable, inject } from '@angular/core';
import {
  CompetenceCreate,
  CompetenceCreateResponse,
  CompetenceResponse
} from '../../models/competence/competence.model';
import { PaginatedResponse } from '../../models/utils/pagination.model';
import { ApiClientService } from '../api-client.service';

@Injectable({
  providedIn: 'root'
})
export class CompetenceService {
  private readonly api = inject(ApiClientService);

  list(page = 1, limit = 10): Promise<PaginatedResponse<CompetenceResponse>> {
    return this.api.get<PaginatedResponse<CompetenceResponse>>('/competences/list', {
      params: { page, limit }
    });
  }

  create(payload: CompetenceCreate): Promise<CompetenceCreateResponse> {
    return this.api.post<CompetenceCreateResponse>('/competences/create', payload);
  }
}
