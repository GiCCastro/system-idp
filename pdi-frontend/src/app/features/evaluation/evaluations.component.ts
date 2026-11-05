import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { UserDetailResponse, UserSimpleResponse } from '../../core/models/auth/user.model';
import { CompetenceResponse } from '../../core/models/competence/competence.model';
import { PositionResponse } from '../../core/models/competence/position.model';
import {
  EvaluationAnswerDetailResponse,
  EvaluationAnswerItem
} from '../../core/models/evaluation/evaluation-answer.model';
import { EvaluationQuestionDetailResponse } from '../../core/models/evaluation/evaluation-question.model';
import {
  EvaluationCreate,
  EvaluationDetailResponse,
  EvaluationType
} from '../../core/models/evaluation/evaluation.model';
import { FormQuestionDetailResponse } from '../../core/models/evaluation/form-question.model';
import { ApiClientService } from '../../core/services/api-client.service';
import { AuthService } from '../../core/services/auth/auth.service';
import { CompetenceService } from '../../core/services/competence/competence.service';
import { PositionService } from '../../core/services/competence/position.service';
import { DevelopmentService } from '../../core/services/development/development.service';
import { EvaluationAnswerService } from '../../core/services/evaluation/evaluation-answer.service';
import { EvaluationQuestionService } from '../../core/services/evaluation/evaluation-question.service';
import { EvaluationService } from '../../core/services/evaluation/evaluation.service';
import { FormQuestionService } from '../../core/services/evaluation/form-question.service';
import { FeedbackService } from '../../core/services/feedback.service';
import { UserService } from '../../core/services/user/user.service';

@Component({
  selector: 'app-evaluations',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './evaluations.component.html',
  styleUrl: './evaluations.component.scss'
})
export class EvaluationsComponent implements OnInit {
  readonly authService = inject(AuthService);
  readonly apiClient = inject(ApiClientService);
  private readonly userService = inject(UserService);
  private readonly positionService = inject(PositionService);
  private readonly competenceService = inject(CompetenceService);
  private readonly formQuestionService = inject(FormQuestionService);
  private readonly evaluationService = inject(EvaluationService);
  private readonly evaluationQuestionService = inject(EvaluationQuestionService);
  private readonly evaluationAnswerService = inject(EvaluationAnswerService);
  private readonly developmentService = inject(DevelopmentService);
  private readonly feedback = inject(FeedbackService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  

  readonly evaluations = signal<EvaluationDetailResponse[]>([]);
  readonly knownUsers = signal<UserDetailResponse[]>([]);
  readonly positions = signal<PositionResponse[]>([]);
  readonly competences = signal<CompetenceResponse[]>([]);
  readonly allFormQuestions = signal<FormQuestionDetailResponse[]>([]);

  readonly page = signal(1);
  readonly totalPages = signal(1);
  readonly showingAllHr = signal(false);
  readonly sortOrder = signal<'asc' | 'desc'>('desc');

  readonly showCreatePanel = signal(false);
  creationMode: 'SELF' | 'MANAGER' = 'MANAGER';

  createForm: EvaluationCreate = {
    user_id: 0,
    evaluator_id: 0,
    target_position_id: null,
    type: 'SELF',
    cycle: '2026.2'
  };

  filterUserId: number | null = null;

  readonly selectedEvaluation = signal<EvaluationDetailResponse | null>(null);
  readonly detailMode = signal<'questionnaire' | 'answers'>('questionnaire');
  readonly evaluationQuestions = signal<EvaluationQuestionDetailResponse[]>([]);
  readonly evaluationAnswers = signal<EvaluationAnswerDetailResponse[]>([]);
  readonly isCycleLocked = signal(false);

  answerDrafts: Record<number, EvaluationAnswerItem> = {};
  manualQuestionIdToLink = 0;

  readonly availableQuestionsToLink = computed(() => {
    const linkedIds = new Set(this.evaluationQuestions().map((eq) => eq.question.id));
    return this.allFormQuestions().filter((fq) => !linkedIds.has(fq.id));
  });

  async ngOnInit(): Promise<void> {
    if (this.authService.isManager()) {
      this.createForm.evaluator_id = this.authService.currentUser()?.id ?? 0;
    }

    const [posRes, compRes, fqRes] = await Promise.all([
      this.positionService.list(1, 100),
      this.competenceService.list(1, 100),
      this.formQuestionService.list(1, 100)
    ]);

    this.positions.set(posRes.items);
    this.competences.set(compRes.items);
    this.allFormQuestions.set(fqRes.items);

    if (this.authService.isHr()) {
      const uRes = await this.userService.list(1, 100);
      this.knownUsers.set(uRes.items);
    } else if (this.authService.isManager()) {
      const myId = this.authService.currentUser()?.id;
      this.knownUsers.set(
        this.userService.getCachedDirectory().filter((u) => u.manager?.id === myId)
      );
    }

    this.route.queryParams.subscribe((params) => {
      const qUserId = params['userId'] ? Number(params['userId']) : null;
      const qEvalId = params['evaluationId'] ? Number(params['evaluationId']) : null;

      if (qUserId) {
        this.filterUserId = qUserId;
        this.createForm.user_id = qUserId;
        void this.loadEvaluationsForUser(qEvalId);
      } else if (this.authService.isCollaborator()) {
        const myId = this.authService.currentUser()?.id;
        if (myId) {
          this.filterUserId = myId;
          void this.loadEvaluationsForUser(qEvalId);
        }
      } else if (this.authService.isHr()) {
        void this.loadAllHrEvaluations(1, qEvalId);
      } else if (this.authService.isManager()) {
        const firstSub = this.knownUsers()[0];
        if (firstSub) {
          this.filterUserId = firstSub.id;
          void this.loadEvaluationsForUser(qEvalId);
        }
      }
    });
  }

  onUserSelected(userId: number): void {
    const found = this.knownUsers().find((u) => u.id === Number(userId));
    this.createForm.evaluator_id = found?.manager?.id ?? 0;
  }

  getEvaluatorOptions(): UserSimpleResponse[] {
    const selectedCollaborator = this.knownUsers().find(
      (user) => user.id === Number(this.createForm.user_id)
    );
    return selectedCollaborator?.manager ? [selectedCollaborator.manager] : [];
  }

  

  async loadAllHrEvaluations(targetPage = 1, autoSelectEvalId: number | null = null): Promise<void> {
    this.showingAllHr.set(true);
    const res = await this.evaluationService.listAll(targetPage, 10, this.sortOrder());
    this.evaluations.set(res.items);
    this.page.set(res.page);
    this.totalPages.set(res.total_pages || 1);
    if (autoSelectEvalId) {
      const match = res.items.find((e) => e.id === autoSelectEvalId);
      if (match) void this.selectEvaluation(match, 'questionnaire');
    }
  }

  async loadEvaluationsForUser(autoSelectEvalId: number | null = null): Promise<void> {
    if (!this.filterUserId) return;
    this.showingAllHr.set(false);
    try {
      const list = await this.evaluationService.listByUser(this.filterUserId, false, this.sortOrder());
      this.evaluations.set(list);
      if (autoSelectEvalId) {
        const match = list.find((e) => e.id === autoSelectEvalId);
        if (match) void this.selectEvaluation(match, 'questionnaire');
      }
    } catch {
      this.evaluations.set([]);
    }
  }

  async toggleSortOrder(): Promise<void> {
    this.sortOrder.set(this.sortOrder() === 'desc' ? 'asc' : 'desc');
    await this.refreshCurrentView();
  }

  async createEvaluation(): Promise<void> {
    if (!this.createForm.user_id || !this.createForm.cycle.trim()) {
      this.feedback.showWarning('Informe o colaborador e o código do ciclo.');
      return;
    }


    const type: EvaluationType = this.creationMode === 'SELF' ? 'SELF' : 'MANAGER';
    const evaluatorId =
      type === 'SELF' ? Number(this.createForm.user_id) : Number(this.createForm.evaluator_id);

    await this.evaluationService.create({
      user_id: Number(this.createForm.user_id),
      evaluator_id: evaluatorId,
      target_position_id: this.createForm.target_position_id,
      type,
      cycle: this.createForm.cycle.trim()
    });
    this.showCreatePanel.set(false);
    await this.refreshCurrentView();
  }

  async selectEvaluation(
    ev: EvaluationDetailResponse,
    mode: 'questionnaire' | 'answers'
  ): Promise<void> {
    this.selectedEvaluation.set(ev);
    this.detailMode.set(mode);
    if (mode === 'questionnaire') {
      await Promise.all([this.fetchQuestionnaire(ev.id), this.checkIfCycleLocked(ev)]);
    } else {
      await this.fetchAnswers(ev.id);
    }
  }

  private async checkIfCycleLocked(ev: EvaluationDetailResponse): Promise<void> {
    const cyclePair = this.evaluations().filter(
      (item) => item.user.id === ev.user.id && item.cycle === ev.cycle
    );
    const evalIdsToCheck = cyclePair.length > 0 ? cyclePair.map((i) => i.id) : [ev.id];

    for (const id of evalIdsToCheck) {
      try {
        const answers = await this.evaluationAnswerService.listByEvaluation(id, true);
        if (answers.length > 0) {
          this.isCycleLocked.set(true);
          return;
        }
      } catch {
        // Sem respostas registradas nesta ponta ainda
      }
    }

    if (this.authService.isHr()) {
      try {
        const devs = await this.developmentService.listByUser(ev.user.id);
        const posId = ev.target_position?.id;
        const hasDev = posId
          ? devs.some((d) => d.position?.id === posId)
          : devs.length > 0;
        this.isCycleLocked.set(hasDev);
        return;
      } catch {
        // Sem PDI gerado ainda
      }
    }

    this.isCycleLocked.set(false);
  }

  async switchDetailMode(mode: 'questionnaire' | 'answers'): Promise<void> {
    const ev = this.selectedEvaluation();
    if (!ev) return;
    await this.selectEvaluation(ev, mode);
  }

  async fetchQuestionnaire(evaluationId: number): Promise<void> {
    try {
      const questions = await this.evaluationQuestionService.listByEvaluation(evaluationId);
      this.evaluationQuestions.set(questions);
      this.answerDrafts = {};
      for (const q of questions) {
        this.answerDrafts[q.question.id] = {
          question_id: q.question.id,
          score: 3,
          answer_text: ''
        };
      }
    } catch {
      this.evaluationQuestions.set([]);
    }
  }

  async fetchAnswers(evaluationId: number): Promise<void> {
    this.evaluationAnswers.set([]);
    try {
      const list = await this.evaluationAnswerService.listByEvaluation(evaluationId);
      this.evaluationAnswers.set(list);
    } catch {
      this.evaluationAnswers.set([]);
    }
  }

  canAnswerEvaluation(ev: EvaluationDetailResponse): boolean {
    const myId = this.authService.currentUser()?.id;
    return Boolean(myId && ev.evaluator?.id === myId);
  }

  setDraftScore(questionId: number, score: number): void {
    if (!this.answerDrafts[questionId]) {
      this.answerDrafts[questionId] = { question_id: questionId, score, answer_text: '' };
    } else {
      this.answerDrafts[questionId].score = score;
    }
  }

  async submitEvaluationAnswers(): Promise<void> {
    const ev = this.selectedEvaluation();
    if (!ev) return;

    const answers = Object.values(this.answerDrafts);
    for (const item of answers) {
      if (!item.answer_text.trim()) {
        this.feedback.showWarning('Preencha a justificativa de todas as questões antes de enviar.');
        return;
      }
    }

    await this.evaluationAnswerService.create({
      evaluation_id: ev.id,
      answers
    });
    await this.switchDetailMode('answers');
  }

  async linkManualQuestion(): Promise<void> {
    const ev = this.selectedEvaluation();
    if (!ev || !this.manualQuestionIdToLink) return;

    await this.evaluationQuestionService.create({
      evaluation_id: ev.id,
      question_id: Number(this.manualQuestionIdToLink)
    });
    this.manualQuestionIdToLink = 0;
    await this.fetchQuestionnaire(ev.id);
  }

  async generateCycleQuestions(ev: EvaluationDetailResponse): Promise<void> {
    await this.evaluationService.generateQuestions(ev.id);
    await this.selectEvaluation(ev, 'questionnaire');
  }

  async generatePdiFromEvaluation(ev: EvaluationDetailResponse): Promise<void> {
    const res = await this.developmentService.generateFromEvaluation(ev.id);
    if (res.development_id) {
      await this.router.navigate(['/pdi'], {
        queryParams: { userId: ev.user.id, developmentId: res.development_id }
      });
    }
  }

  getCompetenceName(competenceId: number): string {
    const found = this.competences().find((c) => c.id === competenceId);
    return found ? found.name : `Competência #${competenceId}`;
  }

  getScoreLabel(score: number): string {
    const labels: Record<number, string> = {
      1: 'Insatisfatório',
      2: 'Em Desenvolvimento',
      3: 'Atende ao Esperado',
      4: 'Acima do Esperado',
      5: 'Referência / Excelência'
    };
    return labels[score] ?? '';
  }

  private async refreshCurrentView(): Promise<void> {
    if (this.authService.isHr() && this.showingAllHr()) {
      await this.loadAllHrEvaluations(this.page());
    } else if (this.filterUserId) {
      await this.loadEvaluationsForUser();
    }
  }
}
