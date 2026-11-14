import { CommonModule } from '@angular/common';
import { Component, ViewChild } from '@angular/core';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';
import { Patient, PatientPage } from '../domain/types';
import { ApiService } from '../api.service';
import { MatPaginator } from '@angular/material/paginator';
import { MatTableModule } from '@angular/material/table';
import {
  MatAccordion,
  MatExpansionModule,
  MatExpansionPanel,
  MatExpansionPanelDescription,
  MatExpansionPanelTitle,
} from '@angular/material/expansion';
import { MatButton } from '@angular/material/button';
import { MatCard } from '@angular/material/card';
import { HeaderComponent } from '../shared/header/header.component';

interface GroupedPatient {
  patientId: number;
  patientGender: string;
  imagesNumber: number;
  records: Patient[];
}


@Component({
  selector: 'app-browse',
  standalone: true,
  imports: [CommonModule, MatExpansionModule, MatTableModule, MatPaginator, MatAccordion, MatExpansionPanel, MatExpansionPanelTitle, MatExpansionPanelDescription, MatButton, MatCard, HeaderComponent],
  templateUrl: './browse.component.html',
  styleUrls: ['./browse.component.css'],
})
export class BrowseComponent {
  imagesDict = new Map<string, SafeUrl | null>();
  base64Dict = new Map<string, string>();
  predictionDict = new Map<string, Record<string, number>>();
  page: number = 0;
  pageSize: number = 10;
  patientPage: PatientPage = {
    patients: {} as { [patientId: string]: Patient[] },
    total: 0,
  };
  patients: GroupedPatient[] = [];
  total: number = 0;

  @ViewChild(MatPaginator) paginator!: MatPaginator;

  constructor(private api: ApiService, private sanitizer: DomSanitizer) {
  }

  ngOnInit(): void {
    this.loadPatients(this.page, this.pageSize);
  }

  loadPatients(page: number, pageSize: number): void {
    this.api.getPatientsPage(page, pageSize).subscribe({
      next: (data) => {
        this.patientPage = data;
        this.patients = this.groupPatients(data.patients);
        this.total = data.total;
      },
      error: (err) => console.error('Error:', err),
    });
  }

  groupPatients(patients: { [id: string]: Patient[] }): GroupedPatient[] {
    return Object.values(patients).map(records => ({
      patientId: records[0].patientId,
      patientGender: records[0].patientGender,
      imagesNumber: records.length,
      records,
    }));
  }

  onPanelOpened(patientId: number) {
    this.patientPage.patients[patientId].map(patient => {
      this.api.getPatientImage(patient.image.split('.')[0]).subscribe({
        next: (imageBlob) => {
          this.storeBlobImage(patient.image, imageBlob);
          this.storeBase64Image(patient.image, imageBlob);
        },
        error: (err) => console.error('Error:', err),
      });
    });
  }

  blobToBase64(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64data = reader.result as string;
        resolve(base64data);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  storeBlobImage(imageId: string, blob: Blob): void {
    const objectUrl = URL.createObjectURL(blob);
    const safeUrl = this.sanitizer.bypassSecurityTrustUrl(objectUrl);
    this.imagesDict.set(imageId, safeUrl);
  }

  storeBase64Image(imageId: string, blob: Blob): void {
    this.blobToBase64(blob)
      .then(base64Data => {
        this.base64Dict.set(imageId, base64Data.split(',')[1]);
      })
      .catch(error => console.error('Blad podczas kodowania obrazu:', error));

  }

  getImage(image: string): SafeUrl | null {
    return this.imagesDict.get(image) || null;
  }

  getDiseaseLabel(disease: number | null): string {
    if (disease === null) {
      return '';
    }
    if (disease == 0) {
      return 'Nie';
    }
    return 'Tak';
  }

  getDiseaseStyle(disease: number | null): string {
    if (disease === null) {
      return '';
    }
    if (disease == 1) {
      return 'disease';
    }
    return 'no-disease';
  }

  hasImagePrediction(imageId: string): boolean {
    return !!this.predictionDict.get(imageId);
  }

  getImagePrediction(imageId: string, className: string): number | null {
    const value = this.predictionDict.get(imageId)?.[className];
    if (value === null || value === undefined) {
      return null;
    }
    return value;
  }

  diagnose(imageId: string): void {
    const base64Image = this.base64Dict.get(imageId);
    if (!base64Image) {
      alert('Nie znaleziono zdjęcia o identyfikatorze: ' + imageId);
      return;
    }

    this.api.predict(base64Image, imageId.split('.')[0])
      .subscribe({
        next: (result) => {
          const predictionsByClass: Record<string, number> = result.reduce((acc, item) => {
            acc[item.class_name] = item.y_predicted;
            return acc;
          }, {} as Record<string, number>);
          console.log(predictionsByClass);
          this.predictionDict.set(imageId, predictionsByClass);
        },
        error: (err) => alert('Błąd podczas diagnozowania!'),
      });
  }
}
