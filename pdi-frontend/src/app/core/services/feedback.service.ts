import { Injectable, signal } from '@angular/core';
import { StandardizedApiError } from '../models/utils/api-error.model';

export interface FeedbackBanner {
  id: number;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  status?: number;
  endpoint?: string;
}

@Injectable({
  providedIn: 'root'
})
export class FeedbackService {
  private readonly _banner = signal<FeedbackBanner | null>(null);
  readonly banner = this._banner.asReadonly();
  private dismissTimer: ReturnType<typeof setTimeout> | null = null;
  private nextId = 1;

  showSuccess(message: string, title = 'Operação Concluída'): void {
    this.present(
      {
        id: this.nextId++,
        type: 'success',
        title,
        message
      },
      5500
    );
  }

  showWarning(message: string, title = 'Atenção Operacional'): void {
    this.present(
      {
        id: this.nextId++,
        type: 'warning',
        title,
        message
      },
      7000
    );
  }

  showApiError(apiError: StandardizedApiError): void {
    this.present(
      {
        id: this.nextId++,
        type: 'error',
        title: apiError.title,
        message: apiError.message,
        status: apiError.status,
        endpoint: apiError.endpoint
      },
      9000
    );
  }

  showError(message: string, title = 'Falha na Operação'): void {
    this.present(
      {
        id: this.nextId++,
        type: 'error',
        title,
        message
      },
      9000
    );
  }

  clear(): void {
    if (this.dismissTimer) {
      clearTimeout(this.dismissTimer);
      this.dismissTimer = null;
    }
    this._banner.set(null);
  }

  private present(banner: FeedbackBanner, autoHideMs: number): void {
    if (this.dismissTimer) {
      clearTimeout(this.dismissTimer);
    }
    this._banner.set(banner);
    this.dismissTimer = setTimeout(() => {
      this._banner.set(null);
      this.dismissTimer = null;
    }, autoHideMs);
  }
}
