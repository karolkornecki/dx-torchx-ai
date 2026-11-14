import Router from 'koa-router';
import fs from 'fs';
import path from 'path';
import { requireAuth } from './middleware/auth_middleware';

export const register = (router: Router) => {
  router.get('/images/:id', requireAuth, async (ctx, next) => {
    const filePath = path.join(__dirname, 'test_images', ctx.params.id + '.png');
    if (!fs.existsSync(filePath)) {
      ctx.status = 404;
      ctx.body = 'Image not found';
      return;
    }
    ctx.type = path.extname(filePath);
    ctx.body = fs.createReadStream(filePath);
  });
};
