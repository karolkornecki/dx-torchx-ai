import Router from 'koa-router';
import { pool } from './db/pool';
import { requireAuth } from './middleware/auth_middleware';

const query = `
    WITH unique_patients AS (SELECT DISTINCT PATIENT_ID
                             FROM TEST_SET_IMAGES
                             ORDER BY PATIENT_ID
        LIMIT $1
    OFFSET $2)
    SELECT i.PATIENT_ID,
           i.IMAGE,
           i.FOLLOW_UP,
           i.PATIENT_AGE,
           i.PATIENT_GENDER,
           i.VIEW_POSITION,
           i.CARDIOMEGALY,
           i.EMPHYSEMA,
           i.EFFUSION,
           i.HERNIA,
           i.INFILTRATION,
           i.MASS,
           i.NODULE,
           i.ATELECTASIS,
           i.PNEUMOTHORAX,
           i.PLEURAL_THICKENING,
           i.PNEUMONIA,
           i.FIBROSIS,
           i.EDEMA,
           i.CONSOLIDATION
    FROM TEST_SET_IMAGES i
             JOIN unique_patients p ON i.PATIENT_ID = p.PATIENT_ID
    ORDER BY i.PATIENT_ID
`;

export const register = (router: Router) => {
  router.get('/patients', requireAuth, async (ctx, next) => {
    const params = ctx.request.query as { page: string; pageSize: string };
    const offset = (parseInt(params.page) || 0) * (parseInt(params.pageSize) || 50);
    const limit = parseInt(params.pageSize) || 50;
    const total = (await pool.query('SELECT COUNT(DISTINCT PATIENT_ID) FROM TEST_SET_IMAGES', []))
      .rows[0].count;
    const patients = await pool.query(query, [limit, offset]);
    if ((patients.rowCount ?? 0) > 0) {
      const patientPage = patients.rows.map((row) => ({
        patientId: row.patient_id,
        image: row.image,
        followUp: row.follow_up,
        patientAge: row.patient_age,
        patientGender: row.patient_gender,
        viewPosition: row.view_position,
        cardiomegaly: row.cardiomegaly,
        emphysema: row.emphysema,
        effusion: row.effusion,
        hernia: row.hernia,
        infiltration: row.infiltration,
        mass: row.mass,
        nodule: row.nodule,
        atelectasis: row.atelectasis,
        pneumothorax: row.pneumothorax,
        pleuralThickening: row.pleural_thickening,
        pneumonia: row.pneumonia,
        fibrosis: row.fibrosis,
        edema: row.edema,
        consolidation: row.consolidation,
      }));
      ctx.body = {
        patients: groupBy(patientPage, (patient) => patient.patientId),
        total: total,
      };
    } else {
      ctx.body = {
        patients: [],
        total: total,
      };
    }
  });
};

function groupBy<T, K extends keyof any>(list: T[], keyGetter: (item: T) => K): Record<K, T[]> {
  return list.reduce(
    (acc, item) => {
      const key = keyGetter(item);
      (acc[key] ||= []).push(item);
      return acc;
    },
    {} as Record<K, T[]>,
  );
}
