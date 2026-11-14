export interface DiagnosisPrediction {
  class_name: string;
  y_prob: number;
  y_predicted: number;
  y_true?: number;
  threshold: number;
}

export interface User {
  firstName: string;
  lastName: string;
}

export interface Patient {
  patientId: number;
  image: string;
  followUp: number;
  patientAge: number;
  patientGender: 'M' | 'F';
  viewPosition: string;
  cardiomegaly: number;
  emphysema: number;
  effusion: number;
  hernia: number;
  infiltration: number;
  mass: number;
  nodule: number;
  atelectasis: number;
  pneumothorax: number;
  pleuralThickening: number;
  pneumonia: number;
  fibrosis: number;
  edema: number;
  consolidation: number;
}

export interface PatientPage {
  patients: {
    [patientId: number]: Patient[];
  };
  total: number;
}

export interface PredictRequest {
  image: string;
  filename?: string;
}
