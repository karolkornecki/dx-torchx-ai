import Koa from 'koa';
import session from 'koa-session';
import bodyParser from 'koa-bodyparser';
import Router from 'koa-router';

export const createServer = (register: (r: Router) => void) => {
  const app = new Koa();
  app.keys = ['test-secret'];
  app.use(session(app));
  app.use(bodyParser());

  const router = new Router({
    prefix: '/api',
  });
  register(router);
  app.use(router.routes());

  return app.callback();
};
