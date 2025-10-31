import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../service/auth.service';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';

@Component({
  selector: 'app-signup',
  standalone: true,
  imports: [FormsModule, CommonModule, RouterLink],
  templateUrl: './signup.component.html',
  styleUrls: ['./signup.component.css']
})
export class SignupComponent {
  email = '';
  password = '';
  message = '';
  loading = false;
  showPassword = false;

  constructor(private authService: AuthService, private router: Router) {}

  togglePassword() {
    this.showPassword = !this.showPassword;
  }

  onSignup() {
    if (!this.email || !this.password) {
      this.message = 'Please fill all fields.';
      return;
    }

    this.loading = true;
    this.authService.signup({ email: this.email, password: this.password }).subscribe({
      next: (res) => {
        this.loading = false;
        this.message = res.message || 'Account created successfully!';
        setTimeout(() => this.router.navigate(['/login']), 1000);
      },
      error: (err) => {
        this.loading = false;
        this.message = err.error?.detail || 'Error occurred during signup.';
      }
    });
  }
}
