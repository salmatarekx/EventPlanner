import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute, RouterLink } from '@angular/router';
import { EventService } from '../../service/event.service';

@Component({
  selector: 'app-invite',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './invite.component.html',
  styleUrls: ['./invite.component.css']
})
export class InviteComponent implements OnInit {
  eventId: string = '';
  email = '';
  message = '';
  loading = false;

  constructor(
    private eventService: EventService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    this.eventId = this.route.snapshot.paramMap.get('id') || '';
    if (!this.eventId) {
      this.router.navigate(['/events']);
    }
  }

  onInvite() {
    if (!this.email) {
      this.message = 'Please enter an email address.';
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(this.email)) {
      this.message = 'Please enter a valid email address.';
      return;
    }

    this.loading = true;
    this.eventService.inviteUser(this.eventId, this.email).subscribe({
      next: (res) => {
        this.loading = false;
        this.message = res.message || 'User invited successfully!';
        this.email = '';
        setTimeout(() => {
          this.message = '';
        }, 3000);
      },
      error: (err) => {
        this.loading = false;
        this.message = err.error?.detail || 'Error inviting user';
      }
    });
  }
}


