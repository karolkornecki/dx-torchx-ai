import request from 'supertest';
import { register } from '../authentication-api';

jest.mock('../user-service');
jest.mock('bcryptjs', () => ({
  compareSync: jest.fn(),
}));

import bcrypt from 'bcryptjs';
import { getUser } from '../user-service';
import { createServer } from './test-server';

const server = createServer(register);

describe('Authentication API Spec', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should return 400 if email or password is missing', async () => {
    const res = await request(server)
      .post('/api/authenticate')
      .send({ email: '', password: '' });

    expect(res.status).toBe(400);
    expect(res.text).toBe('Please enter email and password');
  });

  it('should return 401 if user not found', async () => {
    (getUser as jest.Mock).mockResolvedValue(null);

    const res = await request(server)
      .post('/api/authenticate')
      .send({ email: 'notfound@example.com', password: 'test' });

    expect(res.status).toBe(401);
  });

  it('should return 401 if password does not match', async () => {
    (getUser as jest.Mock).mockResolvedValue({
      firstName: 'John',
      lastName: 'Doe',
      password: 'hashed_password',
    });

    (bcrypt.compareSync as jest.Mock).mockReturnValue(false);

    const res = await request(server)
      .post('/api/authenticate')
      .send({ email: 'john@example.com', password: 'wrongpassword' });

    expect(res.status).toBe(401);
  });

  it('should return 200 and user info if authenticated', async () => {
    (getUser as jest.Mock).mockResolvedValue({
      firstName: 'Jane',
      lastName: 'Smith',
      password: 'hashed_password',
    });

    (bcrypt.compareSync as jest.Mock).mockReturnValue(true);

    const res = await request(server)
      .post('/api/authenticate')
      .send({ email: 'jane@example.com', password: 'correctpassword' });

    expect(res.status).toBe(200);
    expect(res.body).toEqual({
      firstName: 'Jane',
      lastName: 'Smith',
    });
  });
});
