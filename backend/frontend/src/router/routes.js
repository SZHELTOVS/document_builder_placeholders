const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', redirect: '/docs' },  // сразу открывать шаблоны
      { path: 'docs', component: () => import('pages/DocsPage.vue') },
      { path: 'data', component: () => import('pages/DataPage.vue') } // новый маршрут
    ]
  }
]

export default routes
