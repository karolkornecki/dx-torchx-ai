import { pool } from './db/pool';

export interface User {
  firstName: string;
  lastName: string;
  password: string;
}

export const getUser = async (email: string): Promise<User | null> => {
  const pwd = await pool.query(
    'SELECT FIRST_NAME, LAST_NAME, PASSWORD FROM USERS WHERE EMAIL = $1',
    [email],
  );
  if ((pwd.rowCount ?? 0) > 0) {
    return {
      firstName: pwd.rows[0].first_name,
      lastName: pwd.rows[0].last_name,
      password: pwd.rows[0].password,
    };
  }
  return null;
};