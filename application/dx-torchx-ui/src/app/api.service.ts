import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { DiagnosisPrediction, PatientPage, User } from './domain/types';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private baseUrl = '/api';

  constructor(private http: HttpClient) {
  }

  authenticate(email: string, password: string): Observable<User> {
    return this.http.post<User>(`${this.baseUrl}/authenticate`, {
      email,
      password,
    });
  }

  logout(): Observable<void> {
    return this.http.post<void>(`${this.baseUrl}/logout`, {});
  }
  getPatientsPage(page: number, pageSize: number): Observable<PatientPage> {
    return this.http.get<PatientPage>(`${this.baseUrl}/patients?page=${page}&pageSize=${pageSize}`);
  }

  getPatientImage(image: string): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/images/${image}`, {
      responseType: 'blob',
    });
  }

  predict(image: string, filename?: string): Observable<DiagnosisPrediction[]> {
    return this.http.post<DiagnosisPrediction[]>(`${this.baseUrl}/predict`, {
      image,
      filename,
    });
  }
}
