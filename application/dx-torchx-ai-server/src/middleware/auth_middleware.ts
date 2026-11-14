import type Koa from 'koa';

export const requireAuth = async (ctx: Koa.Context, next: Koa.Next) => {
  if (!ctx.session || !ctx.session.authenticated) {
    ctx.status = 401;
    ctx.body = { error: 'Unauthorized' };
    return;
  }

  await next();
};
