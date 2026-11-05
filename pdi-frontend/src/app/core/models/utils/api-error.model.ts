export interface FastApiValidationErrorItem {
  loc: (string | number)[];
  msg: string;
  type: string;
}

export interface FastApiErrorBody {
  detail?: string | FastApiValidationErrorItem[];
  message?: string;
}

export interface StandardizedApiError {
  status: number;
  title: string;
  message: string;
  endpoint: string;
  timestamp: string;
}
