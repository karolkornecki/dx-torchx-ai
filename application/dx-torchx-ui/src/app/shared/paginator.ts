import { MatPaginatorIntl } from '@angular/material/paginator';

export const getPaginatorIntl = (): MatPaginatorIntl => {
  const paginatorIntl = new MatPaginatorIntl();
  paginatorIntl.itemsPerPageLabel = 'Ilość na stronie:';
  return paginatorIntl;
};


export const provideMatPaginatorIntl = () => {
  return {
    provide: MatPaginatorIntl,
    useFactory: getPaginatorIntl,
  };
};
