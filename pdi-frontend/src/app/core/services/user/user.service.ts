import { Injectable, inject } from '@angular/core';
import { UserDetailResponse } from '../../models/auth/user.model';
import { PaginatedResponse } from '../../models/utils/pagination.model';
import { ApiClientService } from '../api-client.service';

const CACHE_USERS_KEY = 'sgpdi_cached_users_directory';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private readonly api = inject(ApiClientService);

  async list(page = 1, limit = 10): Promise<PaginatedResponse<UserDetailResponse>> {
    const res = await this.api.get<PaginatedResponse<UserDetailResponse>>('/users/list', {
      params: { page, limit }
    });
    this.cacheUsers(res.items);
    return res;
  }

  async getById(userId: number, silentError = false): Promise<UserDetailResponse> {
    const user = await this.api.get<UserDetailResponse>(`/users/${userId}`, { silentError });
    this.cacheUsers([user]);
    return user;
  }

  getCachedDirectory(): UserDetailResponse[] {
    try {
      const raw = localStorage.getItem(CACHE_USERS_KEY);
      return raw ? (JSON.parse(raw) as UserDetailResponse[]) : [];
    } catch {
      return [];
    }
  }

  private cacheUsers(users: UserDetailResponse[]): void {
    try {
      const map = new Map<number, UserDetailResponse>();
      this.getCachedDirectory().forEach((u) => map.set(u.id, u));
      users.forEach((u) => {
        if (u?.id) map.set(u.id, u);
      });
      localStorage.setItem(CACHE_USERS_KEY, JSON.stringify(Array.from(map.values())));
    } catch {
      // ignore
    }
  }
}
