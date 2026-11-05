import { CompetenceResponse } from '../competence/competence.model';
import { DevelopmentResponse, DevelopmentStatus } from './development.model';

export type PlanStatus = 'PENDING' | 'COMPLETE';

export interface DevelopmentPlanCreate {
  development_id: number;
  competence_id: number;
  gap: number;
  action: string;
  status?: PlanStatus;
}

export interface DevelopmentPlanResponse extends DevelopmentPlanCreate {
  id: number;
  created_at: string;
}

export interface DevelopmentPlanDetailResponse {
  id: number;
  development: DevelopmentResponse;
  competence: CompetenceResponse;
  gap: number;
  action: string;
  status: PlanStatus;
  created_at: string;
}

export interface DevelopmentPlanCreateResponse {
  message: string;
  development_plan: DevelopmentPlanResponse;
}

export interface DevelopmentPlanStatusUpdate {
  status: PlanStatus;
}

export interface DevelopmentPlanStatusUpdateResponse {
  message: string;
  development_plan: DevelopmentPlanResponse;
  development_status: DevelopmentStatus;
}

export interface ParsedAction702010 {
  practice70: string;
  mentoring20: string;
  formal10: string;
  raw: string;
}
