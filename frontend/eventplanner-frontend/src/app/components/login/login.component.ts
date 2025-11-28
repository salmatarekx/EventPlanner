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
  token: string | null = null;
  loading = false;
  showPassword = false;


  constructor(private authService: AuthService, private router: Router) {}

    togglePassword() {
    this.showPassword = !this.showPassword; 
  }

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
        this.token = res.access_token || null;
        if (this.token) {
          // Store token in localStorage for API calls
          localStorage.setItem('token', this.token);
          console.log('Access token stored:', this.token);
          // Navigate to events page after successful login
          setTimeout(() => {
            this.router.navigate(['/events']);
          }, 500);
        }
      },
      error: (err) => {
        this.loading = false;
        this.message = err.error?.detail || 'Invalid credentials';
        this.token = null;
        // Clear any existing token on error
        localStorage.removeItem('token');
      }
    });
  }

  goToHome() {
    this.router.navigate(['/']);
  }

  copyToken() {
    if (this.token) {
      navigator.clipboard.writeText(this.token).then(() => {
        this.message = 'Token copied to clipboard!';
        setTimeout(() => {
          if (this.token) {
            this.message = 'Login successful!';
          }
        }, 2000);
      });
    }
  }
}
