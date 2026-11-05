export interface PaginatedResponse<T> {
  total: number;
  page: number;
  limit: number;
  total_pages: number;
  items: T[];
}

export interface PaginationParams {
  page?: number;
  limit?: number;
}
