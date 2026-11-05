import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UserDetailResponse } from '../../core/models/auth/user.model';
import { PositionCompetenceDetailResponse } from '../../core/models/competence/position-competence.model';
import { AuthService } from '../../core/services/auth/auth.service';
import { PositionCompetenceService } from '../../core/services/competence/position-competence.service';
import { UserService } from '../../core/services/user/user.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.scss'
})
export class ProfileComponent implements OnInit {
  readonly authService = inject(AuthService);
  private readonly userService = inject(UserService);
  private readonly positionCompetenceService = inject(PositionCompetenceService);

  readonly userDetail = signal<UserDetailResponse | null>(null);
  readonly allPositionCompetences = signal<PositionCompetenceDetailResponse[]>([]);

  readonly myPositionCompetences = computed(() => {
    const posName = this.userDetail()?.position?.name ?? this.authService.currentUser()?.position;
    const posId = this.userDetail()?.position?.id;
    return this.allPositionCompetences().filter((item) =>
      posId ? item.position.id === posId : item.position.name === posName
    );
  });

  async ngOnInit(): Promise<void> {
    const currentUser = this.authService.currentUser();
    if (!currentUser) return;

    await Promise.allSettled([
      this.userService.getById(currentUser.id, true).then((d) => this.userDetail.set(d)),
      this.positionCompetenceService
        .list(1, 100)
        .then((r) => this.allPositionCompetences.set(r.items))
    ]);
  }
}
