import { Component, OnInit, computed, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../core/services/auth/auth.service';

export interface NavItem {
  icon?: string;
  label: string;
  route: string;
  roles: string[];
}

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './shell.component.html',
  styleUrl: './shell.component.scss'
})
export class ShellComponent implements OnInit {
  readonly authService = inject(AuthService);

  private readonly navItems: NavItem[] = [
    {
      icon: 'fa-solid fa-chart-column',
      label: 'Dashboard',
      route: '/painel',
      roles: ['Colaborador', 'Gestor', 'Recursos Humanos']
    },
    {
      icon: 'fa-solid fa-users',
      label: 'Colaboradores e Equipe',
      route: '/colaboradores',
      roles: ['Gestor', 'Recursos Humanos']
    },
    {
      icon: 'fa-solid fa-briefcase',
      label: 'Cargos e Competências',
      route: '/competencias',
      roles: ['Colaborador', 'Gestor', 'Recursos Humanos']
    },
    {
      icon: 'fa-solid fa-calendar-check',
      label: 'Ciclos de Avaliação',
      route: '/avaliacoes',
      roles: ['Colaborador', 'Gestor', 'Recursos Humanos']
    },
    {
      icon: 'fa-solid fa-file-lines',
      label: 'Plano de Desenvolvimento Individual',
      route: '/pdi',
      roles: ['Colaborador', 'Gestor', 'Recursos Humanos']
    }
  ];

  readonly visibleNavItems = computed(() => {
    const role = this.authService.userRole();
    return this.navItems.filter((item) => item.roles.includes(role));
  });

  ngOnInit(): void {
    void this.authService.refreshCurrentUserDetail();
  }
}
