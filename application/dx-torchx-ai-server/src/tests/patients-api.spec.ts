import request from 'supertest';
import { register } from '../patients-api';
import { pool } from '../db/pool';
import { requireAuth } from '../middleware/auth_middleware';

import { createServer } from './test-server';

jest.mock('../db/pool');

jest.mock('../middleware/auth_middleware', () => ({
  requireAuth: jest.fn((_: any, next: any) => next()),
}));

const server = createServer(register);

describe('Patients API Spec', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should return paginated patients', async () => {
    (pool.query as jest.Mock).mockImplementationOnce(() =>
      Promise.resolve({
        rows: [{ count: '2' }],
      }),
    );

    (pool.query as jest.Mock).mockImplementationOnce(() =>
      Promise.resolve({
        rowCount: 2,
        rows: [
          {
            patient_id: 'P1',
            image: 'img1',
            follow_up: 1,
            patient_age: 45,
            patient_gender: 'M',
            view_position: 'PA',
            cardiomegaly: 1,
            emphysema: 0,
            effusion: 1,
            hernia: 0,
            infiltration: 0,
            mass: 0,
            nodule: 1,
            atelectasis: 1,
            pneumothorax: 0,
            pleural_thickening: 0,
            pneumonia: 0,
            fibrosis: 0,
            edema: 0,
            consolidation: 0,
          },
          {
            patient_id: 'P2',
            image: 'img2',
            follow_up: 2,
            patient_age: 60,
            patient_gender: 'F',
            view_position: 'AP',
            cardiomegaly: 0,
            emphysema: 1,
            effusion: 0,
            hernia: 1,
            infiltration: 1,
            mass: 0,
            nodule: 0,
            atelectasis: 0,
            pneumothorax: 1,
            pleural_thickening: 1,
            pneumonia: 0,
            fibrosis: 0,
            edema: 1,
            consolidation: 0,
          },
        ],
      }),
    );

    const res = await request(server).get('/api/patients?page=0&pageSize=50');

    expect(res.status).toBe(200);
    expect(res.body.total).toBe('2');
    expect(res.body.patients).toHaveProperty('P1');
    expect(res.body.patients).toHaveProperty('P2');

    expect(res.body.patients['P1'][0]).toMatchObject({
      patientId: 'P1',
      image: 'img1',
      followUp: 1,
      patientAge: 45,
      patientGender: 'M',
    });

    expect(requireAuth).toHaveBeenCalled();
  });

  it('should return empty array if no patients found', async () => {
    (pool.query as jest.Mock).mockImplementationOnce(() =>
      Promise.resolve({
        rows: [{ count: '0' }],
      }),
    );

    (pool.query as jest.Mock).mockImplementationOnce(() =>
      Promise.resolve({
        rowCount: 0,
        rows: [],
      }),
    );

    const res = await request(server).get('/api/patients?page=1&pageSize=10');

    expect(res.status).toBe(200);
    expect(res.body.total).toBe('0');
    expect(res.body.patients).toEqual([]);
  });
});
