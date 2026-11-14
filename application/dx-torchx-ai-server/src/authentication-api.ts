import Router from 'koa-router';
import bcrypt from 'bcryptjs';
import Koa from 'koa';
import { getUser, User } from './user-service';


const checkCredentials = (user: User, enteredPassword: string): boolean => {
  return bcrypt.compareSync(enteredPassword, user.password);
};

export const register = (router: Router) => {
  router.post('/authenticate', async (ctx: Koa.Context, next: Koa.Next) => {
    const body = ctx.request.body as { email: string; password: string };
    if (!body.email || !body.password) {
      ctx.response.status = 400;
      ctx.body = 'Please enter email and password';
    } else {
      const user = await getUser(body.email);
      if (!user || !checkCredentials(user, body.password)) {
        ctx.response.status = 401;
      } else {
        ctx.session.authenticated = true;
        ctx.session.user = { email: body.email };
        ctx.body = {
          firstName: user.firstName,
          lastName: user.lastName,
        };
        ctx.response.status = 200;
      }
    }
  });

  router.post('/logout', async (ctx: Koa.Context, next: Koa.Next) => {
    ctx.session = null;
    ctx.body = { message: 'Logged out' };
  });
};
