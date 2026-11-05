import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { RoleResponse } from '../../core/models/auth/role.model';
import { UserCreate, UserDetailResponse } from '../../core/models/auth/user.model';
import { PositionResponse } from '../../core/models/competence/position.model';
import { ApiClientService } from '../../core/services/api-client.service';
import { AuthService } from '../../core/services/auth/auth.service';
import { PositionService } from '../../core/services/competence/position.service';
import { FeedbackService } from '../../core/services/feedback.service';
import { UserService } from '../../core/services/user/user.service';

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './users.component.html',
  styleUrl: './users.component.scss'
})
export class UsersComponent implements OnInit {
  readonly authService = inject(AuthService);
  readonly apiClient = inject(ApiClientService);
  private readonly userService = inject(UserService);
  private readonly positionService = inject(PositionService);
  private readonly feedback = inject(FeedbackService);

  readonly users = signal<UserDetailResponse[]>([]);
  readonly lookupUsers = signal<UserDetailResponse[]>([]);
  readonly positions = signal<PositionResponse[]>([]);
  readonly page = signal(1);
  readonly totalPages = signal(1);
  readonly totalItems = signal(0);

  readonly showRegisterModal = signal(false);

  lookupId: number | null = null;
  readonly lookedUpUser = signal<UserDetailResponse | null>(null);

  newUser: UserCreate = {
    cpf: '',
    name: '',
    email: '',
    password: '',
    np: '',
    role_id: 3,
    manager_id: null,
    position_id: 0,
    enterprise_id: 1
  };

  readonly availableRoles = computed<RoleResponse[]>(() => {
    const map = new Map<number, string>([
      [1, 'Recursos Humanos'],
      [2, 'Gestor'],
      [3, 'Colaborador']
    ]);
    for (const u of this.users()) {
      if (u.role?.id && u.role?.name) {
        map.set(u.role.id, u.role.name);
      }
    }
    return Array.from(map.entries()).map(([id, name]) => ({ id, name }));
  });

  readonly managersList = computed(() =>
    this.users().filter((u) => u.role?.name === 'Gestor')
  );

  readonly displayedUsers = computed(() => {
    if (this.authService.isHr()) return this.users();
    const myId = this.authService.currentUser()?.id;
    return this.users().filter((u) => u.manager?.id === myId);
  });

  readonly enterpriseName = computed(
    () =>
      this.authService.currentUserDetail()?.enterprise?.name ??
      this.users().find((user) => user.enterprise?.id === this.newUser.enterprise_id)?.enterprise
        ?.name ??
      ''
  );

  async ngOnInit(): Promise<void> {
    const entId = this.authService.enterpriseId();
    if (entId) this.newUser.enterprise_id = entId;

    const posRes = await this.positionService.list(1, 100);
    this.positions.set(posRes.items);
    if (posRes.items.length > 0 && !this.newUser.position_id) {
      this.newUser.position_id = posRes.items[0].id;
    }

    if (this.authService.isHr()) {
      const lookupRes = await this.userService.list(1, 100);
      this.lookupUsers.set(lookupRes.items);
      await this.loadUsersPage(1);
    } else {
      const cachedUsers = this.userService.getCachedDirectory();
      this.users.set(cachedUsers);
      this.lookupUsers.set(cachedUsers);
    }
  }

  async loadUsersPage(targetPage: number): Promise<void> {
    const res = await this.userService.list(targetPage, 10);
    this.users.set(res.items);
    this.page.set(res.page);
    this.totalPages.set(res.total_pages || 1);
    this.totalItems.set(res.total);
    if (res.items.length > 0 && res.items[0].enterprise?.id) {
      this.newUser.enterprise_id = res.items[0].enterprise.id;
    }
  }

  changePage(newPage: number): void {
    if (newPage < 1 || newPage > this.totalPages()) return;
    void this.loadUsersPage(newPage);
  }

  async lookupUserById(): Promise<void> {
    if (!this.lookupId || this.lookupId < 1) return;
    this.lookedUpUser.set(null);

    const user = await this.userService.getById(this.lookupId);
    this.lookedUpUser.set(user);
    if (!this.users().some((u) => u.id === user.id)) {
      this.users.set([user, ...this.users()]);
    }
  }

  clearLookedUpUser(): void {
    this.lookedUpUser.set(null);
  }

  async registerUser(): Promise<void> {
    if (!this.newUser.name || !this.newUser.cpf || !this.newUser.np || !this.newUser.email || !this.newUser.password) {
      this.feedback.showWarning('Preencha todos os campos obrigatórios do colaborador.');
      return;
    }

    const cleanCpf = this.newUser.cpf.replace(/\D/g, '');
    if (cleanCpf.length !== 11) {
      this.feedback.showWarning('O CPF deve conter 11 dígitos numéricos.');
      return;
    }

    if (!this.newUser.position_id) {
      this.feedback.showWarning('Selecione um cargo válido para o colaborador.');
      return;
    }

    const entId = this.authService.enterpriseId();
    if (entId) this.newUser.enterprise_id = entId;

    await this.authService.register({
      ...this.newUser,
      cpf: cleanCpf
    });
    this.showRegisterModal.set(false);
    this.newUser = {
      cpf: '',
      name: '',
      email: '',
      password: '',
      np: '',
      role_id: this.newUser.role_id,
      manager_id: null,
      position_id: this.positions()[0]?.id ?? 0,
      enterprise_id: this.newUser.enterprise_id
    };
    await this.loadUsersPage(this.page());
  }
}
