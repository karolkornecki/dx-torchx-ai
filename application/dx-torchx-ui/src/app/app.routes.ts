import { Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { MainComponent } from './main/main.component';
import { BrowseComponent } from './browse/browse.component';
import { DiagnoseComponent } from './diagnose/diagnose.component';

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'main', component: MainComponent },
  { path: 'browse', component: BrowseComponent },
  { path: 'diagnose', component: DiagnoseComponent },
  { path: '**', redirectTo: 'login' }
];
