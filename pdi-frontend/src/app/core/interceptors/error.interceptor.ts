import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { SILENT_ERROR_CONTEXT } from '../config/api.config';
import { FastApiErrorBody, StandardizedApiError } from '../models/utils/api-error.model';
import { FeedbackService } from '../services/feedback.service';
import { AuthService } from '../services/auth/auth.service';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const feedback = inject(FeedbackService);
  const authService = inject(AuthService);

  return next(req).pipe(
    catchError((err: HttpErrorResponse) => {
      if (err.status === 401 && !req.url.includes('/auth/login')) {
        authService.logout();
      }

      const standardized = normalizeFastApiError(err, req.url);

      if (!req.context.get(SILENT_ERROR_CONTEXT)) {
        feedback.showApiError(standardized);
      }

      return throwError(() => standardized);
    })
  );
};

function normalizeFastApiError(err: HttpErrorResponse, url: string): StandardizedApiError {
  const endpoint = url.replace(/^https?:\/\/[^/]+/, '');
  const body = (err.error ?? {}) as FastApiErrorBody;

  let detailMessage = '';

  if (err.status === 0) {
    detailMessage =
      'Não foi possível estabelecer conexão com a API (http://127.0.0.1:8000). Verifique se o backend está em execução e se o navegador está acessando via http://127.0.0.1:4200.';
  } else if (typeof body.detail === 'string') {
    detailMessage = body.detail;
  } else if (Array.isArray(body.detail)) {
    detailMessage = body.detail
      .map((item) => {
        const field = item.loc?.[item.loc.length - 1] ?? 'campo';
        return `${field}: ${item.msg}`;
      })
      .join(' | ');
  } else if (typeof body.message === 'string') {
    detailMessage = body.message;
  } else {
    detailMessage = 'Ocorreu um erro inesperado ao processar a requisição.';
  }

  const titleByStatus: Record<number, string> = {
    0: 'Falha de Comunicação com o Servidor',
    400: 'Regra de Negócio / Dados Inválidos',
    401: 'Não Autorizado',
    403: 'Permissão Restrita ao Perfil',
    404: 'Registro Não Encontrado',
    422: 'Erro de Validação de Campos',
    500: 'Erro Interno no Servidor',
    503: 'Serviço Externo Temporariamente Indisponível'
  };

  return {
    status: err.status,
    title: titleByStatus[err.status] ?? `Erro HTTP ${err.status}`,
    message: detailMessage,
    endpoint,
    timestamp: new Date().toISOString()
  };
}
