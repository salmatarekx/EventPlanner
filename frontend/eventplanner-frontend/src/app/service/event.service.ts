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
}

