import { HttpClient, HttpContext, HttpParams } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Observable, finalize, firstValueFrom, tap } from 'rxjs';
import { API_BASE_URL, SILENT_ERROR_CONTEXT } from '../config/api.config';
import { FeedbackService } from './feedback.service';

export interface RequestOptions {
  params?: Record<string, string | number | boolean | undefined | null>;
  silentError?: boolean;
  notifySuccess?: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class ApiClientService {
  private readonly http = inject(HttpClient);
  private readonly feedback = inject(FeedbackService);

  private readonly _pendingRequests = signal(0);
  readonly isLoading = computed(() => this._pendingRequests() > 0);

  /**
   * Stream Observable para uso direto ou com rxResource()
   */
  get$<T>(endpoint: string, options?: RequestOptions): Observable<T> {
    this._pendingRequests.update((n) => n + 1);
    return this.http
      .get<T>(`${API_BASE_URL}${endpoint}`, {
        params: this.buildParams(options?.params),
        context: this.buildContext(options?.silentError)
      })
      .pipe(finalize(() => this._pendingRequests.update((n) => Math.max(0, n - 1))));
  }

  /**
   * Consumo assíncrono direto via Promise (async/await) sem boilerplate de subscribe
   */
  get<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return firstValueFrom(this.get$<T>(endpoint, options));
  }

  /**
   * Envio POST enxuto com extração automática da mensagem de sucesso da API FastAPI
   */
  post<T>(endpoint: string, body: unknown = {}, options?: RequestOptions): Promise<T> {
    this._pendingRequests.update((n) => n + 1);
    const shouldNotify = options?.notifySuccess ?? true;

    return firstValueFrom(
      this.http
        .post<T>(`${API_BASE_URL}${endpoint}`, body, {
          params: this.buildParams(options?.params),
          context: this.buildContext(options?.silentError)
        })
        .pipe(
          tap((res: any) => {
            if (shouldNotify && res && typeof res.message === 'string') {
              this.feedback.showSuccess(res.message);
            }
          }),
          finalize(() => this._pendingRequests.update((n) => Math.max(0, n - 1)))
        )
    );
  }

  /**
   * Atualização parcial PATCH enxuta com notificação automática de sucesso
   */
  patch<T>(endpoint: string, body: unknown = {}, options?: RequestOptions): Promise<T> {
    this._pendingRequests.update((n) => n + 1);
    const shouldNotify = options?.notifySuccess ?? true;

    return firstValueFrom(
      this.http
        .patch<T>(`${API_BASE_URL}${endpoint}`, body, {
          params: this.buildParams(options?.params),
          context: this.buildContext(options?.silentError)
        })
        .pipe(
          tap((res: any) => {
            if (shouldNotify && res && typeof res.message === 'string') {
              this.feedback.showSuccess(res.message);
            }
          }),
          finalize(() => this._pendingRequests.update((n) => Math.max(0, n - 1)))
        )
    );
  }

  private buildParams(raw?: Record<string, string | number | boolean | undefined | null>): HttpParams {
    let params = new HttpParams();
    if (!raw) return params;
    for (const [key, value] of Object.entries(raw)) {
      if (value !== undefined && value !== null && value !== '') {
        params = params.set(key, String(value));
      }
    }
    return params;
  }

  private buildContext(silentError?: boolean): HttpContext {
    return new HttpContext().set(SILENT_ERROR_CONTEXT, Boolean(silentError));
  }
}
