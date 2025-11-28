import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { EventService } from '../../service/event.service';

@Component({
  selector: 'app-events',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './events.component.html',
  styleUrls: ['./events.component.css']
})
export class EventsComponent implements OnInit {
  organizedEvents: any[] = [];
  invitedEvents: any[] = [];
  loading = false;
  message = '';
  showCreateForm = false;

  title = '';
  description = '';
  date = '';
  time = '';
  location = '';

  constructor(private eventService: EventService, private router: Router) {}

  ngOnInit() {
    this.loadEvents();
  }

  loadEvents() {
    this.loading = true;
    this.eventService.getMyEvents().subscribe({
      next: (res) => {
        this.organizedEvents = res || [];
        this.loading = false;
      },
      error: (err) => {
        this.loading = false;
        this.message = 'Error loading organized events';
      }
    });

    this.eventService.getInvitedEvents().subscribe({
      next: (res) => {
        this.invitedEvents = res || [];
      },
      error: (err) => {
      }
    });
  }

  toggleCreateForm() {
    this.showCreateForm = !this.showCreateForm;
    if (!this.showCreateForm) {
      this.resetForm();
    }
  }

  onCreateEvent() {
    if (!this.title || !this.description || !this.date || !this.time || !this.location) {
      this.message = 'Please fill all fields.';
      return;
    }

    this.loading = true;
    this.eventService.createEvent({
      title: this.title,
      description: this.description,
      date: this.date,
      time: this.time,
      location: this.location
    }).subscribe({
      next: (res) => {
        this.loading = false;
        this.message = res.message || 'Event created successfully!';
        this.resetForm();
        this.showCreateForm = false;
        this.loadEvents();
        setTimeout(() => this.message = '', 3000);
      },
      error: (err) => {
        this.loading = false;
        this.message = err.error?.detail || 'Error creating event';
      }
    });
  }

  resetForm() {
    this.title = '';
    this.description = '';
    this.date = '';
    this.time = '';
    this.location = '';
  }

  deleteEvent(eventId: string) {
    if (!confirm('Are you sure you want to delete this event?')) {
      return;
    }

    this.loading = true;
    this.eventService.deleteEvent(eventId).subscribe({
      next: (res) => {
        this.loading = false;
        this.message = res.message || 'Event deleted successfully!';
        this.loadEvents();
        setTimeout(() => this.message = '', 3000);
      },
      error: (err) => {
        this.loading = false;
        this.message = err.error?.detail || 'Error deleting event';
      }
    });
  }

  goToInvite(eventId: string) {
    this.router.navigate(['/events/invite', eventId]);
  }

  respondToEvent(eventId: string, response: 'Going' | 'Maybe' | 'Not Going') {
    this.loading = true;
    this.eventService.respondToEvent(eventId, response).subscribe({
      next: (res) => {
        this.loading = false;
        this.message = res.message || 'Response recorded successfully!';
        this.loadEvents(); // Reload to update response status
        setTimeout(() => this.message = '', 3000);
      },
      error: (err) => {
        this.loading = false;
        this.message = err.error?.detail || 'Error recording response';
      }
    });
  }

  goToAttendees(eventId: string) {
    this.router.navigate(['/events/attendees', eventId]);
  }

  goToSearch() {
    this.router.navigate(['/events/search']);
  }

  getResponseBadgeClass(response: string): string {
    if (!response) return '';
    return 'response-' + response.toLowerCase().replace(' ', '-');
  }
}

