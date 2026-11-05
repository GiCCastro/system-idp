import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CompetenceResponse } from '../../core/models/competence/competence.model';
import { PositionCompetenceDetailResponse } from '../../core/models/competence/position-competence.model';
import { PositionResponse } from '../../core/models/competence/position.model';
import { FormQuestionDetailResponse } from '../../core/models/evaluation/form-question.model';
import { ApiClientService } from '../../core/services/api-client.service';
import { AuthService } from '../../core/services/auth/auth.service';
import { CompetenceService } from '../../core/services/competence/competence.service';
import { PositionCompetenceService } from '../../core/services/competence/position-competence.service';
import { PositionService } from '../../core/services/competence/position.service';
import { FormQuestionService } from '../../core/services/evaluation/form-question.service';

@Component({
  selector: 'app-competences',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './competences.component.html',
  styleUrl: './competences.component.scss'
})
export class CompetencesComponent implements OnInit {
  readonly authService = inject(AuthService);
  readonly apiClient = inject(ApiClientService);
  private readonly positionService = inject(PositionService);
  private readonly competenceService = inject(CompetenceService);
  private readonly positionCompetenceService = inject(PositionCompetenceService);
  private readonly formQuestionService = inject(FormQuestionService);

  readonly activeTab = signal<'matrix' | 'positions' | 'competences' | 'questions'>('matrix');

  readonly pageSize = 10;

  // Catálogos completos para os <select> de vínculo
  readonly allPositions = signal<PositionResponse[]>([]);
  readonly allCompetences = signal<CompetenceResponse[]>([]);

  // Listas paginadas (limit = 10) das 4 abas
  readonly matrixItems = signal<PositionCompetenceDetailResponse[]>([]);
  readonly matrixPage = signal(1);
  readonly matrixTotalPages = signal(1);
  readonly matrixTotal = signal(0);

  readonly positions = signal<PositionResponse[]>([]);
  readonly positionsPage = signal(1);
  readonly positionsTotalPages = signal(1);
  readonly positionsTotal = signal(0);

  readonly competences = signal<CompetenceResponse[]>([]);
  readonly competencesPage = signal(1);
  readonly competencesTotalPages = signal(1);
  readonly competencesTotal = signal(0);

  readonly formQuestions = signal<FormQuestionDetailResponse[]>([]);
  readonly questionsPage = signal(1);
  readonly questionsTotalPages = signal(1);
  readonly questionsTotal = signal(0);

  selectedPositionFilter = 0;

  positionForm = { name: '', description: '' };
  competenceForm = { name: '', description: '' };
  relationForm = { position_id: 0, competence_id: 0, expected_level: 3 };
  questionForm = { competence_id: 0, question_text: '' };

  readonly groupedMatrix = computed(() => {
    const groups = new Map<
      number,
      { position: PositionResponse; items: PositionCompetenceDetailResponse[] }
    >();
    for (const item of this.matrixItems()) {
      const existing = groups.get(item.position.id);
      if (existing) {
        existing.items.push(item);
      } else {
        groups.set(item.position.id, {
          position: item.position,
          items: [item]
        });
      }
    }
    return Array.from(groups.values());
  });

  ngOnInit(): void {
    void this.reloadAll();
  }

  onPositionFilterChange(): void {
    void this.loadMatrixPage(1);
  }

  async reloadAll(): Promise<void> {
    await Promise.all([
      this.loadSelectCatalogs(),
      this.loadMatrixPage(this.matrixPage()),
      this.loadPositionsPage(this.positionsPage()),
      this.loadCompetencesPage(this.competencesPage()),
      this.loadQuestionsPage(this.questionsPage())
    ]);
  }

  private async loadSelectCatalogs(): Promise<void> {
    const [posAll, compAll] = await Promise.all([
      this.positionService.list(1, 100),
      this.competenceService.list(1, 100)
    ]);
    this.allPositions.set(posAll.items);
    this.allCompetences.set(compAll.items);

    if (posAll.items.length > 0 && !this.relationForm.position_id) {
      this.relationForm.position_id = posAll.items[0].id;
    }
    if (compAll.items.length > 0) {
      if (!this.relationForm.competence_id) this.relationForm.competence_id = compAll.items[0].id;
      if (!this.questionForm.competence_id) this.questionForm.competence_id = compAll.items[0].id;
    }
  }

  async loadMatrixPage(page: number): Promise<void> {
    if (page < 1) return;
    const posId = Number(this.selectedPositionFilter);
    if (posId > 0) {
      const items = await this.positionCompetenceService.listByPosition(posId);
      this.matrixItems.set(items);
      this.matrixPage.set(1);
      this.matrixTotalPages.set(1);
      this.matrixTotal.set(items.length);
      return;
    }

    const res = await this.positionCompetenceService.list(page, this.pageSize);
    this.matrixItems.set(res.items);
    this.matrixPage.set(res.page);
    this.matrixTotalPages.set(res.total_pages || 1);
    this.matrixTotal.set(res.total);
  }

  async loadPositionsPage(page: number): Promise<void> {
    if (page < 1) return;
    const res = await this.positionService.list(page, this.pageSize);
    this.positions.set(res.items);
    this.positionsPage.set(res.page);
    this.positionsTotalPages.set(res.total_pages || 1);
    this.positionsTotal.set(res.total);
  }

  async loadCompetencesPage(page: number): Promise<void> {
    if (page < 1) return;
    const res = await this.competenceService.list(page, this.pageSize);
    this.competences.set(res.items);
    this.competencesPage.set(res.page);
    this.competencesTotalPages.set(res.total_pages || 1);
    this.competencesTotal.set(res.total);
  }

  async loadQuestionsPage(page: number): Promise<void> {
    if (page < 1) return;
    const res = await this.formQuestionService.list(page, this.pageSize);
    this.formQuestions.set(res.items);
    this.questionsPage.set(res.page);
    this.questionsTotalPages.set(res.total_pages || 1);
    this.questionsTotal.set(res.total);
  }

  async createPosition(): Promise<void> {
    if (!this.positionForm.name.trim() || !this.positionForm.description.trim()) return;
    await this.positionService.create(this.positionForm);
    this.positionForm = { name: '', description: '' };
    await this.reloadAll();
  }

  async createCompetence(): Promise<void> {
    if (!this.competenceForm.name.trim() || !this.competenceForm.description.trim()) return;
    await this.competenceService.create(this.competenceForm);
    this.competenceForm = { name: '', description: '' };
    await this.reloadAll();
  }

  async createRelation(): Promise<void> {
    if (!this.relationForm.position_id || !this.relationForm.competence_id) return;
    await this.positionCompetenceService.create(this.relationForm);
    await this.reloadAll();
  }

  async createQuestion(): Promise<void> {
    if (!this.questionForm.competence_id || !this.questionForm.question_text.trim()) return;
    await this.formQuestionService.create(this.questionForm);
    this.questionForm.question_text = '';
    await this.reloadAll();
  }
}
