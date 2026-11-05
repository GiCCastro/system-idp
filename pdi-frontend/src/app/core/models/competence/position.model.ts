export interface PositionCreate {
  name: string;
  description: string;
}

export interface PositionResponse extends PositionCreate {
  id: number;
}

export interface PositionCreateResponse {
  message: string;
  position: PositionResponse;
}
