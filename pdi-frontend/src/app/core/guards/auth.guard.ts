import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { UserRoleName } from '../models/auth/role.model';
import { AuthService } from '../services/auth/auth.service';

export const authGuard: CanActivateFn = (_route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  return authService.isAuthenticated()
    ? true
    : router.createUrlTree(['/login'], { queryParams: { returnUrl: state.url } });
};

export const guestGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);
  return !authService.isAuthenticated() ? true : router.createUrlTree(['/painel']);
};

export const roleGuard = (allowedRoles: UserRoleName[]): CanActivateFn => {
  return (_route, state) => {
    const authService = inject(AuthService);
    const router = inject(Router);

    if (!authService.isAuthenticated()) {
      return router.createUrlTree(['/login'], { queryParams: { returnUrl: state.url } });
    }

    const currentRole = authService.userRole() as UserRoleName;
    return allowedRoles.includes(currentRole) ? true : router.createUrlTree(['/painel']);
  };
};
