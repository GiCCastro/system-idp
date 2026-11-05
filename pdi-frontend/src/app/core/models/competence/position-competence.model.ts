import { CompetenceResponse } from './competence.model';
import { PositionResponse } from './position.model';

export interface PositionCompetenceCreate {
  position_id: number;
  competence_id: number;
  expected_level: number;
}

export interface PositionCompetenceResponse extends PositionCompetenceCreate {}

export interface PositionCompetenceDetailResponse {
  position: PositionResponse;
  competence: CompetenceResponse;
  expected_level: number;
}

export interface PositionCompetenceCreateResponse {
  message: string;
  position_competence: PositionCompetenceResponse;
}
