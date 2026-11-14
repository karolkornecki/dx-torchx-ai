import Router from 'koa-router';
import { requireAuth } from './middleware/auth_middleware';
import { getPrediction } from './services/ml-engine-api';

export const register = (router: Router) => {
  router.post('/predict', requireAuth, async (ctx, next) => {
    const body = ctx.request.body as { image: string; filename?: string };
    const response = await getPrediction(body.image, body.filename);
    if (!response) {
      ctx.status = 400;
      return;
    }
    ctx.body = response;
  });
};
