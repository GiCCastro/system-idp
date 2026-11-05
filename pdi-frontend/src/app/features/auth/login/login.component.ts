import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { UserLogin } from '../../../core/models/auth/user.model';
import { ApiClientService } from '../../../core/services/api-client.service';
import { AuthService } from '../../../core/services/auth/auth.service';
import { FeedbackService } from '../../../core/services/feedback.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent implements OnInit {
  private readonly authService = inject(AuthService);
  private readonly feedback = inject(FeedbackService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  readonly apiClient = inject(ApiClientService);

  readonly loginMode = signal<'email' | 'np'>('email');
  readonly showPassword = signal(false);
  readonly originWarning = signal(false);

  email = '';
  np = '';
  password = '';

  ngOnInit(): void {
    this.feedback.clear();
    if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
      this.originWarning.set(true);
    }
  }

  setLoginMode(mode: 'email' | 'np'): void {
    this.loginMode.set(mode);
    this.feedback.clear();
  }

  async onSubmit(): Promise<void> {
    this.feedback.clear();
    const isEmail = this.loginMode() === 'email';
    const identifier = isEmail ? this.email.trim() : this.np.trim();

    if (!identifier) {
      this.feedback.showWarning(
        isEmail ? 'Informe seu e-mail corporativo.' : 'Informe seu Número Pessoal (NP).'
      );
      return;
    }

    if (!this.password) {
      this.feedback.showWarning('Informe sua senha de acesso.');
      return;
    }

    const payload: UserLogin = {
      email: isEmail ? identifier : null,
      np: !isEmail ? identifier : null,
      password: this.password
    };

    await this.authService.login(payload);
    const returnUrl = this.route.snapshot.queryParamMap.get('returnUrl');
    if (returnUrl && returnUrl.startsWith('/')) {
      await this.router.navigateByUrl(returnUrl);
    } else {
      await this.router.navigate(['/painel']);
    }
  }
}
