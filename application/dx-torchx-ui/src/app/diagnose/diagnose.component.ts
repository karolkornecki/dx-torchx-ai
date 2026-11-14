import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { ApiService } from '../api.service';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatCard } from '@angular/material/card';
import { MatButton, MatIconButton } from '@angular/material/button';
import { DiagnosisPrediction } from '../domain/types';
import { HeaderComponent } from '../shared/header/header.component';


@Component({
  selector: 'app-diagnose',
  standalone: true,
  imports: [CommonModule, MatExpansionModule, MatInputModule, MatIconModule, MatCard, MatIconButton, MatButton, HeaderComponent],
  templateUrl: './diagnose.component.html',
  styleUrls: ['./diagnose.component.css'],
})
export class DiagnoseComponent {
  base64Image: string | null = null;
  fileName: string = '';
  filePreviewUrl: string | ArrayBuffer | null = null;
  diagnosisPredictions: DiagnosisPrediction[] = [];

  constructor(private api: ApiService) {
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;

    if (input.files && input.files[0]) {
      const file = input.files[0];
      this.fileName = file.name;

      if (file.type !== 'image/png') {
        alert('Tylko pliki w formacie PNG są dozwolone!');
        return;
      }

      const reader = new FileReader();
      reader.onload = () => {
        this.base64Image = (reader.result as string).split(',')[1];
        this.filePreviewUrl = reader.result;
      };
      reader.readAsDataURL(file);
    }
  }

  scrollToDiagnoseTable() {
    setTimeout(() => {
      const el = document.getElementById('diagnose-table');
      if (el) {
        el.scrollIntoView({ behavior: 'smooth' });
      }
    }, 0);
  }

  upload(): void {
    if (!this.base64Image) {
      alert('Nie wybrano obrazu!');
      return;
    }
    this.api.predict(this.base64Image, this.fileName.split('.')[0]).subscribe({
      next: (result) => {
        this.diagnosisPredictions = result;
        this.scrollToDiagnoseTable();
      },
      error: (err) => alert('Błąd podczas uploadu pliku!'),
    });
  }

  getDiseaseStyle(disease?: number): string {
    if (disease == 1) {
      return 'disease';
    }
    return 'no-disease';
  }

  getDiseaseLabel(disease?: number): string {
    if (disease === 2) {
      return '-';
    }
    if (disease == 0) {
      return 'Nie';
    }
    return 'Tak';
  }

  reset() {
    this.base64Image = null;
    this.fileName = '';
    this.filePreviewUrl = null;
    this.diagnosisPredictions = [];
  }
}
