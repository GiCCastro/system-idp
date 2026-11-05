import { Routes } from '@angular/router';
import { authGuard, guestGuard, roleGuard } from './core/guards/auth.guard';
import { LoginComponent } from './features/auth/login/login.component';
import { ShellComponent } from './layout/shell/shell.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { UsersComponent } from './features/user/users.component';
import { CompetencesComponent } from './features/competence/competences.component';
import { EvaluationsComponent } from './features/evaluation/evaluations.component';
import { DevelopmentComponent } from './features/development/development.component';
import { ProfileComponent } from './features/profile/profile.component';

export const routes: Routes = [
  {
    path: 'login',
    component: LoginComponent,
    canActivate: [guestGuard]
  },
  {
    path: '',
    component: ShellComponent,
    canActivate: [authGuard],
    children: [
      {
        path: 'painel',
        component: DashboardComponent
      },
      {
        path: 'colaboradores',
        component: UsersComponent,
        canActivate: [roleGuard(['Gestor', 'Recursos Humanos'])]
      },
      {
        path: 'competencias',
        component: CompetencesComponent
      },
      {
        path: 'avaliacoes',
        component: EvaluationsComponent
      },
      {
        path: 'pdi',
        component: DevelopmentComponent
      },
      {
        path: 'perfil',
        component: ProfileComponent
      },
      {
        path: '',
        redirectTo: 'painel',
        pathMatch: 'full'
      }
    ]
  },
  {
    path: '**',
    redirectTo: 'login'
  }
];
