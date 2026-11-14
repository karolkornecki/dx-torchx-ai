import { CommonModule, NgOptimizedImage } from '@angular/common';
import { Component } from '@angular/core';
import { MatCard } from '@angular/material/card';
import { User } from '../../domain/types';
import { ApiService } from '../../api.service';
import { MatButton } from '@angular/material/button';
import { Router } from '@angular/router';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, MatCard, MatButton, NgOptimizedImage],
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css'],
})
export class HeaderComponent {

  constructor(private api: ApiService, private router: Router) {
  }

  ngOnInit() {
    if (!localStorage.getItem('user')) {
      this.router.navigate(['/login']);
    }
  }

  getUser(): string | null {
    const user = localStorage.getItem('user');
    if (user) {
      const loggedInUser = JSON.parse(user) as User;
      return `${loggedInUser?.firstName} ${loggedInUser?.lastName}`;
    }
    return null;
  }

  logout() {
    this.api.logout().subscribe({
      next: () => {
        localStorage.removeItem('user');
        this.router.navigate(['/login']);
      },
      error: err => {
        console.error(err);
      },
    });
  }
}
