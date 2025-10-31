import { Component } from '@angular/core';
import { AuthService } from '../../service/auth.service';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';

@Component({
  selector: 'app-login',
  standalone: true,
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
  imports: [CommonModule, FormsModule, RouterLink]
})
export class LoginComponent {
  email = '';
  password = '';
  message = '';
  loading = false;

  constructor(private authService: AuthService, private router: Router) {}

  onLogin() {
    if (!this.email || !this.password) {
      this.message = 'Please enter email and password.';
      return;
    }

    this.loading = true;
    this.authService.login({ email: this.email, password: this.password }).subscribe({
      next: (res) => {
        this.loading = false;
        this.message = res.message || 'Login successful!';
        setTimeout(() => this.router.navigate(['/']), 1000);
      },
      error: (err) => {
        this.loading = false;
        this.message = err.error?.detail || 'Invalid credentials';
      }
    });
  }
}
