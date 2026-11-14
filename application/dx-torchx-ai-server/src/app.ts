import Koa from 'koa';
import Router from 'koa-router';
import serve from 'koa-static';
import path from 'path';
import bodyParser from 'koa-bodyparser';
import session from 'koa-session';
import fs from 'fs';
import { register as registerAuthenticationApi } from './authentication-api';
import { register as registerPatientsApi } from './patients-api';
import { register as registerPatientsImagesApi } from './patients-images-api';
import { register as registerPredictionApi } from './prediction-api';

const app = new Koa();

const router = new Router({
  prefix: '/api',
});

registerAuthenticationApi(router);
registerPatientsApi(router);
registerPatientsImagesApi(router);
registerPredictionApi(router);

app.keys = ['3n$8#B@!4zXq7wKjFv2mP!d@Lc9Yr^Gt'];
app.use(session(app));
app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());
const staticPath = path.join(__dirname, 'frontend');
app.use(serve(staticPath));

app.use(async (ctx) => {
  const indexPath = path.join(staticPath, 'index.html');
  ctx.type = 'html';
  ctx.body = fs.createReadStream(indexPath);
});

export default app;
