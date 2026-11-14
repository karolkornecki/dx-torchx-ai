import request from 'supertest';
import { getPrediction } from '../services/ml-engine-api';
import { createServer } from './test-server';
import { register } from '../prediction-api';
import { requireAuth } from '../middleware/auth_middleware';

jest.mock('../services/ml-engine-api');

jest.mock('../middleware/auth_middleware', () => ({
  requireAuth: jest.fn((_: any, next: any) => next()),
}));

const server = createServer(register);

describe('Prediction API Spec', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('returns 200 with prediction if valid input', async () => {
    (getPrediction as jest.Mock).mockResolvedValue({
      result: 'some prediction',
    });

    const res = await request(server)
      .post('/api/predict')
      .send({ image: 'base64string', filename: 'x.png' });

    expect(res.status).toBe(200);
    expect(res.body).toEqual({ result: 'some prediction' });
    expect(getPrediction).toHaveBeenCalledWith('base64string', 'x.png');
    expect(requireAuth).toHaveBeenCalled();
  });

  it('returns 400 if getPrediction returns null', async () => {
    (getPrediction as jest.Mock).mockResolvedValue(null);

    const res = await request(server)
      .post('/api/predict')
      .send({ image: 'invalid base64', filename: 'x.png' });

    expect(res.status).toBe(400);
  });
});
