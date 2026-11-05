import { Injectable, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import {
  JwtPayload,
  Token,
  UserCreate,
  UserCreateResponse,
  UserDetailResponse,
  UserLogin,
  UserResponse
} from '../../models/auth/user.model';
import { UserRoleName } from '../../models/auth/role.model';
import { ApiClientService } from '../api-client.service';

const STORAGE_TOKEN_KEY = 'sgpdi_access_token';
const STORAGE_USER_KEY = 'sgpdi_user';
const STORAGE_DETAIL_KEY = 'sgpdi_user_detail';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly api = inject(ApiClientService);
  private readonly router = inject(Router);

  private readonly _token = signal<string | null>(localStorage.getItem(STORAGE_TOKEN_KEY));
  private readonly _user = signal<UserResponse | null>(this.readJson<UserResponse>(STORAGE_USER_KEY));
  private readonly _userDetail = signal<UserDetailResponse | null>(
    this.readJson<UserDetailResponse>(STORAGE_DETAIL_KEY)
  );

  readonly token = this._token.asReadonly();
  readonly currentUser = this._user.asReadonly();
  readonly currentUserDetail = this._userDetail.asReadonly();

  readonly isAuthenticated = computed(() => {
    const token = this._token();
    const user = this._user();
    if (!token || !user) return false;
    const payload = this.decodeJwt(token);
    return !(payload?.exp && payload.exp * 1000 < Date.now());
  });

  readonly userRole = computed<UserRoleName | string>(() => this._user()?.role ?? '');
  readonly isHr = computed(() => this.userRole() === 'Recursos Humanos');
  readonly isManager = computed(() => this.userRole() === 'Gestor');
  readonly isCollaborator = computed(() => this.userRole() === 'Colaborador');

  readonly enterpriseId = computed<number | null>(() => {
    const detail = this._userDetail();
    if (detail?.enterprise?.id) return detail.enterprise.id;
    const token = this._token();
    if (!token) return null;
    const payload = this.decodeJwt(token);
    return payload?.enterprise_id ? Number(payload.enterprise_id) : null;
  });

  async login(credentials: UserLogin): Promise<Token> {
    const res = await this.api.post<Token>('/auth/login', credentials, { notifySuccess: false });
    localStorage.setItem(STORAGE_TOKEN_KEY, res.access_token);
    localStorage.setItem(STORAGE_USER_KEY, JSON.stringify(res.user));
    this._token.set(res.access_token);
    this._user.set(res.user);
    void this.refreshCurrentUserDetail(res.user.id);
    return res;
  }

  register(payload: UserCreate): Promise<UserCreateResponse> {
    return this.api.post<UserCreateResponse>('/auth/register', payload);
  }

  async refreshCurrentUserDetail(userId?: number): Promise<void> {
    const id = userId ?? this._user()?.id;
    if (!id) return;
    try {
      const detail = await this.api.get<UserDetailResponse>(`/users/${id}`, { silentError: true });
      localStorage.setItem(STORAGE_DETAIL_KEY, JSON.stringify(detail));
      this._userDetail.set(detail);
    } catch {
      // Silencioso em background
    }
  }

  logout(): void {
    localStorage.removeItem(STORAGE_TOKEN_KEY);
    localStorage.removeItem(STORAGE_USER_KEY);
    localStorage.removeItem(STORAGE_DETAIL_KEY);
    this._token.set(null);
    this._user.set(null);
    this._userDetail.set(null);
    void this.router.navigate(['/login']);
  }

  decodeJwt(token: string): JwtPayload | null {
    try {
      const parts = token.split('.');
      if (parts.length !== 3) return null;
      const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      return JSON.parse(jsonPayload) as JwtPayload;
    } catch {
      return null;
    }
  }

  private readJson<T>(key: string): T | null {
    try {
      const raw = localStorage.getItem(key);
      return raw ? (JSON.parse(raw) as T) : null;
    } catch {
      return null;
    }
  }
}
