import { Pool } from 'pg';

const host = process.env.DB_HOST || 'localhost';
export const pool = new Pool({
  user: 'postgres',
  host: host,
  database: 'dx_torchx_ai',
  password: 'postgres',
  port: 5432,
});
