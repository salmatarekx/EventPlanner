import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute, RouterLink } from '@angular/router';
import { EventService } from '../../service/event.service';

@Component({
  selector: 'app-attendees',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './attendees.component.html',
  styleUrls: ['./attendees.component.css']
})
export class AttendeesComponent implements OnInit {
  eventId: string = '';
  eventTitle: string = '';
  attendees: any[] = [];
  responseSummary: any = {
    'Going': 0,
    'Maybe': 0,
    'Not Going': 0,
    'No Response': 0
  };
  totalAttendees: number = 0;
  loading = false;
  message = '';

  constructor(
    private eventService: EventService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    this.eventId = this.route.snapshot.paramMap.get('id') || '';
    if (!this.eventId) {
      this.router.navigate(['/events']);
      return;
    }
    this.loadAttendees();
  }

  loadAttendees() {
    this.loading = true;
    this.message = '';

    this.eventService.getEventAttendees(this.eventId).subscribe({
      next: (res) => {
        this.loading = false;
        this.eventTitle = res.event_title || 'Unknown Event';
        this.attendees = res.attendees || [];
        this.responseSummary = res.response_summary || {
          'Going': 0,
          'Maybe': 0,
          'Not Going': 0,
          'No Response': 0
        };
        this.totalAttendees = res.total_attendees || 0;
      },
      error: (err) => {
        this.loading = false;
        this.message = err.error?.detail || 'Error loading attendees';
        if (err.status === 403) {
          setTimeout(() => {
            this.router.navigate(['/events']);
          }, 2000);
        }
      }
    });
  }

  getResponseBadgeClass(response: string): string {
    switch (response) {
      case 'Going':
        return 'response-going';
      case 'Maybe':
        return 'response-maybe';
      case 'Not Going':
        return 'response-not-going';
      default:
        return 'response-none';
    }
  }
}

