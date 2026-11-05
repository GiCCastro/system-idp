import { Injectable, inject } from '@angular/core';
import {
  DevelopmentPlanCreate,
  DevelopmentPlanCreateResponse,
  DevelopmentPlanDetailResponse,
  DevelopmentPlanStatusUpdateResponse,
  ParsedAction702010,
  PlanStatus
} from '../../models/development/development-plan.model';
import { ApiClientService } from '../api-client.service';
import { DevelopmentService } from './development.service';

@Injectable({
  providedIn: 'root'
})
export class DevelopmentPlanService {
  private readonly api = inject(ApiClientService);
  private readonly developmentService = inject(DevelopmentService);

  create(payload: DevelopmentPlanCreate): Promise<DevelopmentPlanCreateResponse> {
    return this.api.post<DevelopmentPlanCreateResponse>('/development_plan/create', payload);
  }

  async listByDevelopment(developmentId: number): Promise<DevelopmentPlanDetailResponse[]> {
    const plans = await this.api.get<DevelopmentPlanDetailResponse[]>(
      `/development_plan/${developmentId}`
    );
    if (plans.length > 0 && plans[0].development?.user_id) {
      this.developmentService.cachePlans(plans[0].development.user_id, developmentId, plans);
    }
    return plans;
  }

  async updateStatus(
    planId: number,
    status: PlanStatus
  ): Promise<DevelopmentPlanStatusUpdateResponse> {
    const res = await this.api.patch<DevelopmentPlanStatusUpdateResponse>(
      `/development_plan/${planId}/status`,
      { status }
    );
    this.developmentService.updateCachedPlanStatus(planId, status, res.development_status);
    return res;
  }

  parseAction702010(actionText: string): ParsedAction702010 {
    const raw = actionText || '';
    const p70 = raw.match(/\[Prática 70%\]:\s*([\s\S]*?)(?=\n\s*\[Mentoria\/Troca 20%\]|$)/i);
    const p20 = raw.match(/\[Mentoria\/Troca 20%\]:\s*([\s\S]*?)(?=\n\s*\[Educação Formal 10%\]|$)/i);
    const p10 = raw.match(/\[Educação Formal 10%\]:\s*([\s\S]*?)$/i);

    return {
      practice70: p70 ? p70[1].trim() : '',
      mentoring20: p20 ? p20[1].trim() : '',
      formal10: p10 ? p10[1].trim() : '',
      raw
    };
  }
}
