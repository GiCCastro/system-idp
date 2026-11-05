import { EnterpriseResponse } from '../auth/enterprise.model';
import { UserSimpleResponse } from '../auth/user.model';
import { PositionResponse } from '../competence/position.model';

export type EvaluationType = 'SELF' | 'MANAGER';

export interface EvaluationCreate {
  user_id: number;
  evaluator_id: number;
  target_position_id?: number | null;
  enterprise_id?: number;
  type: EvaluationType;
  cycle: string;
}

export interface EvaluationResponse extends EvaluationCreate {
  id: number;
  created_at: string;
}

export interface EvaluationDetailResponse {
  id: number;
  created_at: string;
  user: UserSimpleResponse;
  evaluator: UserSimpleResponse;
  enterprise?: EnterpriseResponse | null;
  target_position?: PositionResponse | null;
  type: EvaluationType;
  cycle: string;
}

export interface EvaluationCreateResponse {
  message: string;
  evaluation: EvaluationResponse;
}

export interface GenerateQuestionsResponse {
  message: string;
  total: number;
  linked_evaluations: {
    self_evaluation_id: number;
    manager_evaluation_id: number;
  };
}
