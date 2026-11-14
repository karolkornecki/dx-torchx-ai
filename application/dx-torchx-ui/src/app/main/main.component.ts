import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButton } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { Router } from '@angular/router';
import { HeaderComponent } from '../shared/header/header.component';

@Component({
  selector: 'app-main',
  standalone: true,
  imports: [CommonModule, MatButton, MatCardModule, HeaderComponent],
  templateUrl: './main.component.html',
  styleUrls: ['./main.component.css'],
})
export class MainComponent {

  constructor(private router: Router) {
  }

  onBrowse() {
    this.router.navigate(['/browse']);
  }

  onDiagnose() {
    this.router.navigate(['/diagnose']);
  }
}
