import { HttpContextToken } from '@angular/common/http';

export const API_BASE_URL = 'http://127.0.0.1:8000';

/**
 * Quando verdadeiro no HttpContext da requisição, suprime o disparo automático
 * do banner global de erro no errorInterceptor (útil para consultas silenciosas em background).
 */
export const SILENT_ERROR_CONTEXT = new HttpContextToken<boolean>(() => false);
