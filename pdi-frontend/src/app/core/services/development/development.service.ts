import { Injectable, inject } from '@angular/core';
import {
  DevelopmentCreate,
  DevelopmentCreateResponse,
  DevelopmentDetailResponse,
  GenerateDevelopmentResponse
} from '../../models/development/development.model';
import { DevelopmentPlanDetailResponse, PlanStatus } from '../../models/development/development-plan.model';
import { ApiClientService } from '../api-client.service';

const CACHE_PDI_PLANS_KEY = 'sgpdi_cached_plans_by_user';

export interface CachedUserPdiSnapshot {
  userId: number;
  userName: string;
  developments: DevelopmentDetailResponse[];
  plansByDevId: Record<number, DevelopmentPlanDetailResponse[]>;
  updatedAt: string;
}

@Injectable({
  providedIn: 'root'
})
export class DevelopmentService {
  private readonly api = inject(ApiClientService);

  create(payload: DevelopmentCreate): Promise<DevelopmentCreateResponse> {
    return this.api.post<DevelopmentCreateResponse>('/development/create', payload);
  }

  async listByUser(userId: number): Promise<DevelopmentDetailResponse[]> {
    const devs = await this.api.get<DevelopmentDetailResponse[]>(`/development/${userId}`);
    if (devs.length > 0) {
      this.cacheUserDevelopments(userId, devs[0].user?.name ?? `Colaborador #${userId}`, devs);
    }
    return devs;
  }

  generateFromEvaluation(evaluationId: number): Promise<GenerateDevelopmentResponse> {
    return this.api.post<GenerateDevelopmentResponse>(
      `/development/generate-from-evaluation/${evaluationId}`,
      {}
    );
  }

  cacheUserDevelopments(
    userId: number,
    userName: string,
    developments: DevelopmentDetailResponse[]
  ): void {
    try {
      const all = this.getAllSnapshots();
      const existing = all[userId] ?? {
        userId,
        userName,
        developments: [],
        plansByDevId: {},
        updatedAt: new Date().toISOString()
      };
      existing.userName = userName || existing.userName;
      existing.developments = developments;
      existing.updatedAt = new Date().toISOString();
      all[userId] = existing;
      localStorage.setItem(CACHE_PDI_PLANS_KEY, JSON.stringify(all));
    } catch {
      // ignore
    }
  }

  cachePlans(
    userId: number,
    developmentId: number,
    plans: DevelopmentPlanDetailResponse[]
  ): void {
    try {
      const all = this.getAllSnapshots();
      const existing = all[userId] ?? {
        userId,
        userName: `Colaborador #${userId}`,
        developments: [],
        plansByDevId: {},
        updatedAt: new Date().toISOString()
      };
      existing.plansByDevId[developmentId] = plans;
      existing.updatedAt = new Date().toISOString();
      all[userId] = existing;
      localStorage.setItem(CACHE_PDI_PLANS_KEY, JSON.stringify(all));
    } catch {
      // ignore
    }
  }

  updateCachedPlanStatus(planId: number, status: PlanStatus, devStatus?: any): void {
    try {
      const all = this.getAllSnapshots();
      for (const userIdStr of Object.keys(all)) {
        const snap = all[Number(userIdStr)];
        for (const devIdStr of Object.keys(snap.plansByDevId)) {
          const devId = Number(devIdStr);
          const list = snap.plansByDevId[devId] ?? [];
          const found = list.find((p) => p.id === planId);
          if (found) {
            found.status = status;
            const devHeader = snap.developments.find((d) => d.id === devId);
            if (devHeader && devStatus) {
              devHeader.status = devStatus;
            }
          }
        }
      }
      localStorage.setItem(CACHE_PDI_PLANS_KEY, JSON.stringify(all));
    } catch {
      // ignore
    }
  }

  getCachedSnapshot(userId: number): CachedUserPdiSnapshot | null {
    return this.getAllSnapshots()[userId] ?? null;
  }

  private getAllSnapshots(): Record<number, CachedUserPdiSnapshot> {
    try {
      const raw = localStorage.getItem(CACHE_PDI_PLANS_KEY);
      return raw ? (JSON.parse(raw) as Record<number, CachedUserPdiSnapshot>) : {};
    } catch {
      return {};
    }
  }
}
