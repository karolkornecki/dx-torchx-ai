import request from 'supertest';
import { register } from '../patients-images-api';
import { requireAuth } from '../middleware/auth_middleware';
import { createServer } from './test-server';

jest.mock('fs');
import fs from 'fs';

jest.mock('../db/pool');

jest.mock('../middleware/auth_middleware', () => ({
  requireAuth: jest.fn((_: any, next: any) => next()),
}));

const server = createServer(register);

describe('Patients Images API Spec', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should return image stream if file exists', async () => {
    (fs.existsSync as jest.Mock).mockReturnValue(true);
    (fs.createReadStream as jest.Mock).mockReturnValue('fake image data');

    const res = await request(server).get('/api/images/123');

    expect(res.status).toBe(200);
    expect(res.headers['content-type']).toBe('image/png');
    expect(res.body.toString()).toBe('fake image data');
    expect(requireAuth).toHaveBeenCalled();
  });

  it('should return 404 if file does not exist', async () => {
    (fs.existsSync as jest.Mock).mockReturnValue(false);

    const res = await request(server).get('/api/images/999');

    expect(res.status).toBe(404);
    expect(res.text).toBe('Image not found');
    expect(requireAuth).toHaveBeenCalled();
  });
});
