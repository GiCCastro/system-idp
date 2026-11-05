import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FeedbackBannerComponent } from './shared/components/feedback-banner/feedback-banner.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, FeedbackBannerComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {}
