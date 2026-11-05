import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FeedbackService } from '../../../core/services/feedback.service';

@Component({
  selector: 'app-feedback-banner',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './feedback-banner.component.html',
  styleUrl: './feedback-banner.component.scss'
})
export class FeedbackBannerComponent {
  readonly feedback = inject(FeedbackService);
}
