import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { UserDetailResponse } from '../../core/models/auth/user.model';
import {
  DevelopmentPlanDetailResponse,
  ParsedAction702010,
  PlanStatus
} from '../../core/models/development/development-plan.model';
import { DevelopmentDetailResponse } from '../../core/models/development/development.model';
import { EvaluationDetailResponse } from '../../core/models/evaluation/evaluation.model';
import { ApiClientService } from '../../core/services/api-client.service';
import { AuthService } from '../../core/services/auth/auth.service';
import { DevelopmentPlanService } from '../../core/services/development/development-plan.service';
import { DevelopmentService } from '../../core/services/development/development.service';
import { EvaluationService } from '../../core/services/evaluation/evaluation.service';
import { FeedbackService } from '../../core/services/feedback.service';
import { UserService } from '../../core/services/user/user.service';

@Component({
  selector: 'app-development',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './development.component.html',
  styleUrl: './development.component.scss'
})
export class DevelopmentComponent implements OnInit {
  readonly authService = inject(AuthService);
  readonly apiClient = inject(ApiClientService);
  private readonly userService = inject(UserService);
  private readonly evaluationService = inject(EvaluationService);
  private readonly developmentService = inject(DevelopmentService);
  private readonly developmentPlanService = inject(DevelopmentPlanService);
  private readonly feedback = inject(FeedbackService);
  private readonly route = inject(ActivatedRoute);

  readonly users = signal<UserDetailResponse[]>([]);
  readonly evaluations = signal<EvaluationDetailResponse[]>([]);

  targetUserId = 0;
  selectedEvaluationIdForAi = 0;
  readonly generatingAiPdi = signal(false);

  readonly developments = signal<DevelopmentDetailResponse[]>([]);
  readonly selectedDevelopment = signal<DevelopmentDetailResponse | null>(null);
  readonly plans = signal<DevelopmentPlanDetailResponse[]>([]);

  readonly showAiGeneratorModal = signal(false);

  readonly filteredEvaluationsForTargetUser = computed(() => {
    const uid = Number(this.targetUserId);
    const all = this.evaluations();
    if (!uid) return all;
    return all.filter((ev) => ev.user.id === uid);
  });

  async ngOnInit(): Promise<void> {
    if (this.authService.isHr()) {
      const [uRes, evalRes] = await Promise.all([
        this.userService.list(1, 100),
        this.evaluationService.listAll(1, 100)
      ]);
      this.users.set(uRes.items);
      this.evaluations.set(evalRes.items);

      if (evalRes.items.length > 0 && !this.selectedEvaluationIdForAi) {
        this.selectedEvaluationIdForAi = evalRes.items[0].id;
      }
    }

    this.route.queryParams.subscribe((params) => {
      const qUserId = params['userId'] ? Number(params['userId']) : null;
      const qDevId = params['developmentId'] ? Number(params['developmentId']) : null;

      if (this.authService.isHr()) {
        if (qUserId) {
          this.targetUserId = qUserId;
          void this.onCollaboratorChange(qUserId, qDevId);
        }
      } else {
        const userIdToLookup = qUserId ?? this.authService.currentUser()?.id ?? 0;
        this.targetUserId = userIdToLookup;
        const cached = this.developmentService.getCachedSnapshot(userIdToLookup);
        if (cached) {
          this.developments.set(cached.developments);
          if (qDevId) {
            const matchedDev = cached.developments.find((d) => d.id === qDevId) ?? null;
            if (matchedDev) {
              this.selectedDevelopment.set(matchedDev);
              this.plans.set(cached.plansByDevId[matchedDev.id] ?? []);
            }
          }
        }
      }
    });
  }

  async onCollaboratorChange(userId: number, autoSelectDevId: number | null = null): Promise<void> {
    this.targetUserId = Number(userId);
    const matchingEvals = this.filteredEvaluationsForTargetUser();
    if (matchingEvals.length > 0) {
      this.selectedEvaluationIdForAi = matchingEvals[0].id;
    } else {
      this.selectedEvaluationIdForAi = 0;
    }
    await this.loadUserDevelopments(autoSelectDevId);
  }

  async generatePdiWithAi(): Promise<void> {
    if (!this.selectedEvaluationIdForAi) {
      this.feedback.showWarning(
        'Selecione uma avaliação válida do ciclo concluído (SELF + MANAGER respondidas) para gerar o PDI.'
      );
      return;
    }

    const chosenEval = this.evaluations().find(
      (e) => e.id === Number(this.selectedEvaluationIdForAi)
    );

    this.generatingAiPdi.set(true);
    try {
      const res = await this.developmentService.generateFromEvaluation(
        Number(this.selectedEvaluationIdForAi)
      );
      this.showAiGeneratorModal.set(false);
      if (chosenEval?.user?.id) {
        this.targetUserId = chosenEval.user.id;
      }
      if (this.targetUserId) {
        await this.loadUserDevelopments(res.development_id ?? null);
      }
    } finally {
      this.generatingAiPdi.set(false);
    }
  }

  async loadUserDevelopments(autoSelectDevId: number | null = null): Promise<void> {
    if (!this.targetUserId) return;

    if (!this.authService.isHr()) {
      const snap = this.developmentService.getCachedSnapshot(this.targetUserId);
      if (snap) this.developments.set(snap.developments);
      return;
    }

    try {
      const devs = await this.developmentService.listByUser(Number(this.targetUserId));
      this.developments.set(devs);
      if (autoSelectDevId && devs.length > 0) {
        const target = devs.find((d) => d.id === autoSelectDevId);
        if (target) {
          await this.selectDevelopment(target);
        }
      }
    } catch {
      this.developments.set([]);
      this.selectedDevelopment.set(null);
      this.plans.set([]);
    }
  }

  async selectDevelopment(dev: DevelopmentDetailResponse): Promise<void> {
    this.selectedDevelopment.set(dev);
    if (this.authService.isHr()) {
      try {
        const items = await this.developmentPlanService.listByDevelopment(dev.id);
        this.plans.set(items);
      } catch {
        this.plans.set([]);
      }
    } else {
      const snap = this.developmentService.getCachedSnapshot(dev.user.id);
      this.plans.set(snap?.plansByDevId[dev.id] ?? []);
    }
  }

  async togglePlanStatus(plan: DevelopmentPlanDetailResponse): Promise<void> {
    const nextStatus: PlanStatus = plan.status === 'COMPLETE' ? 'PENDING' : 'COMPLETE';
    const res = await this.developmentPlanService.updateStatus(plan.id, nextStatus);

    this.plans.update((list) =>
      list.map((p) => (p.id === plan.id ? { ...p, status: nextStatus } : p))
    );

    const dev = this.selectedDevelopment();
    if (dev && res.development_status) {
      const updatedDev: DevelopmentDetailResponse = {
        ...dev,
        status: res.development_status
      };
      this.selectedDevelopment.set(updatedDev);
      this.developments.update((list) =>
        list.map((d) => (d.id === updatedDev.id ? updatedDev : d))
      );
    }
  }

  formatDate(date: string): string {
    const match = /^(\d{4})-(\d{2})-(\d{2})(?:$|T)/.exec(date);
    if (!match) return date;
    return `${match[3]}-${match[2]}-${match[1]}`;
  }

  parseAction(actionText: string): ParsedAction702010 {
    return this.developmentPlanService.parseAction702010(actionText);
  }

  formatDevStatus(status: string): string {
    if (status === 'COMPLETE') return 'Concluído';
    if (status === 'IN_PROGRESS') return 'Em Andamento';
    return 'Pendente (PENDING)';
  }
}
