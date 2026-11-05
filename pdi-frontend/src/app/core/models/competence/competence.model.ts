export interface CompetenceCreate {
  name: string;
  description: string;
}

export interface CompetenceResponse extends CompetenceCreate {
  id: number;
}

export interface CompetenceCreateResponse {
  message: string;
  competence: CompetenceResponse;
}
