import { Injectable, inject } from '@angular/core';
import {
  PositionCompetenceCreate,
  PositionCompetenceCreateResponse,
  PositionCompetenceDetailResponse
} from '../../models/competence/position-competence.model';
import { PaginatedResponse } from '../../models/utils/pagination.model';
import { ApiClientService } from '../api-client.service';

@Injectable({
  providedIn: 'root'
})
export class PositionCompetenceService {
  private readonly api = inject(ApiClientService);

  list(page = 1, limit = 10): Promise<PaginatedResponse<PositionCompetenceDetailResponse>> {
    return this.api.get<PaginatedResponse<PositionCompetenceDetailResponse>>(
      '/position_competence/list',
      { params: { page, limit } }
    );
  }

  listByPosition(positionId: number): Promise<PositionCompetenceDetailResponse[]> {
    return this.api.get<PositionCompetenceDetailResponse[]>(
      `/position_competence/${positionId}`
    );
  }

  create(payload: PositionCompetenceCreate): Promise<PositionCompetenceCreateResponse> {
    return this.api.post<PositionCompetenceCreateResponse>('/position_competence/create', payload);
  }
}
