import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { EventService } from '../../service/event.service';

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.css']
})
export class SearchComponent implements OnInit {
  keyword = '';
  date = '';
  role: string = '';
  loading = false;
  message = '';
  searchResults: any[] = [];
  filtersApplied: any = {};

  constructor(private eventService: EventService, private router: Router) {}

  ngOnInit() {
    // Don't auto-search on page load - wait for user input
    this.message = '';
    this.searchResults = [];
  }

  performSearch() {
    // Validate that at least one search criterion is provided
    const hasKeyword = this.keyword.trim().length > 0;
    const hasDate = this.date.trim().length > 0;
    const hasRole = this.role.trim().length > 0;

    // Check if any search criteria is provided
    if (!hasKeyword && !hasDate && !hasRole) {
      this.message = 'Please enter at least one search criterion (keyword, date, or role).';
      this.searchResults = [];
      return;
    }

    this.loading = true;
    this.message = '';

    const params: any = {};
    if (hasKeyword) params.keyword = this.keyword.trim();
    if (hasDate) params.start_date = this.date.trim();
    if (hasRole) params.role = this.role.trim();

    this.eventService.searchEvents(params).subscribe({
      next: (res) => {
        this.loading = false;
        this.searchResults = res.results || [];
        this.filtersApplied = res.filters_applied || {};
        if (this.searchResults.length === 0) {
          this.message = 'No events found matching your search criteria.';
        } else {
          this.message = ''; // Clear any previous error messages
        }
      },
      error: (err) => {
        this.loading = false;
        this.message = err.error?.detail || 'Error searching events';
        this.searchResults = [];
      }
    });
  }

  clearFilters() {
    this.keyword = '';
    this.date = '';
    this.role = '';
    this.message = '';
    this.searchResults = [];
  }

  goToEvent(eventId: string) {
    this.router.navigate(['/events']);
  }
}

