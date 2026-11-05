import { UserSimpleResponse } from '../auth/user.model';
import { PositionResponse } from '../competence/position.model';

export type DevelopmentStatus = 'PENDING' | 'IN_PROGRESS' | 'COMPLETE';

export interface DevelopmentCreate {
  user_id: number;
  position_id: number;
  title: string;
  status?: DevelopmentStatus;
}

export interface DevelopmentResponse extends DevelopmentCreate {
  id: number;
  created_at: string;
}

export interface DevelopmentDetailResponse {
  id: number;
  user: UserSimpleResponse;
  position: PositionResponse;
  title: string;
  status: DevelopmentStatus;
  created_at: string;
}

export interface DevelopmentCreateResponse {
  message: string;
  development: DevelopmentResponse;
}

export interface GenerateDevelopmentResponse {
  message: string;
  development_id?: number;
  total_competences_addressed?: number;
  plans_created?: number;
}
