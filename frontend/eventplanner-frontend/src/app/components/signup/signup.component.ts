import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../service/auth.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-signup',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './signup.component.html',
  styleUrls: ['./signup.component.css']
})
export class SignupComponent {
  email = '';
  password = '';
  message = '';

  constructor(private authService: AuthService) {}

  onSignup() {
    this.authService.signup({ email: this.email, password: this.password }).subscribe({
      next: (res) => this.message = res.message,
      error: (err) => this.message = err.error.detail || 'Error occurred'
    });
  }
}
