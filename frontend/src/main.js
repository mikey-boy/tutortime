import App from "./App.vue"

import { createApp } from 'vue'
import { createWebHashHistory, createRouter } from 'vue-router'

import TakeLessons from './components/TakeLessons.vue'
import GiveLessons from './components/GiveLessons.vue'
import ServiceTemplate from './components/ServiceTemplate.vue'
import UserLogin from './components/UserLogin.vue'

const routes = [
  { path: '/', component: TakeLessons },
  { path: '/user/services', component: GiveLessons },
  { path: '/user/services/template', component: ServiceTemplate },
  { path: '/user/services/:id/template', component: ServiceTemplate },
  { path: '/user/login', component: UserLogin },
  // { path: '/about', name: 'HowItWorks', component: HowItWorks },
  // { path: '/learning', name: 'LearningHub', component: LearningHub },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

const app = createApp(App)
app.use(router)
app.mount('#app')
