import { Routes } from '@angular/router';
import { HomeComponent } from './home/home';
import { LoginComponent } from './components/login/login.component';
import { SignupComponent } from './components/signup/signup.component';
import { EventsComponent } from './components/events/events.component';
import { InviteComponent } from './components/invite/invite.component';
import { SearchComponent } from './components/search/search.component';
import { AttendeesComponent } from './components/attendees/attendees.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'signup', component: SignupComponent },
  { path: 'login', component: LoginComponent },
  { path: 'events', component: EventsComponent },
  { path: 'events/invite/:id', component: InviteComponent },
  { path: 'events/search', component: SearchComponent },
  { path: 'events/attendees/:id', component: AttendeesComponent },
];



