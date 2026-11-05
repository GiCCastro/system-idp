import { Injectable, inject } from '@angular/core';
import {
  PositionCreate,
  PositionCreateResponse,
  PositionResponse
} from '../../models/competence/position.model';
import { PaginatedResponse } from '../../models/utils/pagination.model';
import { ApiClientService } from '../api-client.service';

@Injectable({
  providedIn: 'root'
})
export class PositionService {
  private readonly api = inject(ApiClientService);

  list(page = 1, limit = 10): Promise<PaginatedResponse<PositionResponse>> {
    return this.api.get<PaginatedResponse<PositionResponse>>('/position/list', {
      params: { page, limit }
    });
  }

  create(payload: PositionCreate): Promise<PositionCreateResponse> {
    return this.api.post<PositionCreateResponse>('/position/create', payload);
  }
}
