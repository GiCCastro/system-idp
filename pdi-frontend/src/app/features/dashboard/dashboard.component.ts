import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { EvaluationDetailResponse } from '../../core/models/evaluation/evaluation.model';
import { AuthService } from '../../core/services/auth/auth.service';
import { CompetenceService } from '../../core/services/competence/competence.service';
import { PositionCompetenceService } from '../../core/services/competence/position-competence.service';
import { PositionService } from '../../core/services/competence/position.service';
import { EvaluationService } from '../../core/services/evaluation/evaluation.service';
import { FormQuestionService } from '../../core/services/evaluation/form-question.service';
import { UserService } from '../../core/services/user/user.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit {
  readonly authService = inject(AuthService);
  private readonly userService = inject(UserService);
  private readonly positionService = inject(PositionService);
  private readonly competenceService = inject(CompetenceService);
  private readonly positionCompetenceService = inject(PositionCompetenceService);
  private readonly formQuestionService = inject(FormQuestionService);
  private readonly evaluationService = inject(EvaluationService);

  readonly recentEvaluations = signal<EvaluationDetailResponse[]>([]);
  readonly sortOrder = signal<'asc' | 'desc'>('desc');

  readonly hrTotalUsers = signal(0);
  readonly totalPositions = signal(0);
  readonly totalCompetences = signal(0);
  readonly totalMatrixLinks = signal(0);
  readonly totalQuestions = signal(0);
  readonly hrTotalEvaluations = signal(0);

  async ngOnInit(): Promise<void> {
    const currentUser = this.authService.currentUser();
    if (!currentUser) return;

    await Promise.allSettled([
      this.positionService.list(1, 10).then((r) => this.totalPositions.set(r.total)),
      this.competenceService.list(1, 10).then((r) => this.totalCompetences.set(r.total)),
      this.positionCompetenceService.list(1, 10).then((r) => this.totalMatrixLinks.set(r.total)),
      this.formQuestionService.list(1, 10).then((r) => this.totalQuestions.set(r.total))
    ]);

    if (this.authService.isHr()) {
      await Promise.allSettled([
        this.userService.list(1, 10).then((r) => this.hrTotalUsers.set(r.total)),
        this.loadDashboardEvaluations()
      ]);
    } else if (this.authService.isCollaborator()) {
      await this.loadDashboardEvaluations();
    }
  }

  async toggleSortOrder(): Promise<void> {
    this.sortOrder.set(this.sortOrder() === 'desc' ? 'asc' : 'desc');
    await this.loadDashboardEvaluations();
  }

  private async loadDashboardEvaluations(): Promise<void> {
    const currentUser = this.authService.currentUser();
    if (!currentUser) return;

    if (this.authService.isHr()) {
      const r = await this.evaluationService.listAll(1, 8, this.sortOrder());
      this.hrTotalEvaluations.set(r.total);
      this.recentEvaluations.set(r.items);
    } else if (this.authService.isCollaborator()) {
      const evals = await this.evaluationService.listByUser(
        currentUser.id,
        true,
        this.sortOrder()
      );
      this.recentEvaluations.set(evals);
    }
  }
}
