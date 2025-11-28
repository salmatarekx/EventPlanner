import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class EventService {

  private apiUrl = 'http://127.0.0.1:8000/events';

  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('token') || '';
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }

  createEvent(data: { title: string; description: string; date: string; time: string; location: string }): Observable<any> {
    return this.http.post(`${this.apiUrl}/create`, data, { headers: this.getHeaders() });
  }

  getMyEvents(): Observable<any> {
    return this.http.get(`${this.apiUrl}/my-events`, { headers: this.getHeaders() });
  }

  getInvitedEvents(): Observable<any> {
    return this.http.get(`${this.apiUrl}/invited`, { headers: this.getHeaders() });
  }

  getAllUserEvents(): Observable<any> {
    return this.http.get(`${this.apiUrl}/me`, { headers: this.getHeaders() });
  }

  inviteUser(eventId: string, email: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/invite`, { event_id: eventId, email }, { headers: this.getHeaders() });
  }

  deleteEvent(eventId: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${eventId}`, { headers: this.getHeaders() });
  }

  searchEvents(params: { keyword?: string; start_date?: string; end_date?: string; role?: string }): Observable<any> {
    let queryParams = new URLSearchParams();
    if (params.keyword) queryParams.append('keyword', params.keyword);
    if (params.start_date) queryParams.append('start_date', params.start_date);
    if (params.end_date) queryParams.append('end_date', params.end_date);
    if (params.role) queryParams.append('role', params.role);
    
    const queryString = queryParams.toString();
    const url = queryString ? `${this.apiUrl}/search?${queryString}` : `${this.apiUrl}/search`;
    return this.http.get(url, { headers: this.getHeaders() });
  }

  respondToEvent(eventId: string, response: 'Going' | 'Maybe' | 'Not Going'): Observable<any> {
    return this.http.post(`${this.apiUrl}/${eventId}/respond`, { response }, { headers: this.getHeaders() });
  }

  getEventAttendees(eventId: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/${eventId}/attendees`, { headers: this.getHeaders() });
  }
}

