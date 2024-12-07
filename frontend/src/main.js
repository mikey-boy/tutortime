import App from "./App.vue"

import { isLoggedIn } from "./utils/auth";
import { createApp } from 'vue'
import { createWebHashHistory, createRouter } from 'vue-router'

import TakeLessons from './components/TakeLessons.vue'
import ServiceDetails from './components/ServiceDetails.vue'
import GiveLessons from './components/GiveLessons.vue'
import ServiceTemplate from './components/ServiceTemplate.vue'
import UserLogin from './components/UserLogin.vue'
import Calendar from './components/Calendar.vue'
import Chat from './components/Chat.vue'

function authenticated(to) {
  if (!isLoggedIn()) {
    return { path: '/user/login', query: { redirect: to.path } }
  }
}

const routes = [
  { path: '/', component: TakeLessons },
  { path: '/services/:id/', component: ServiceDetails },
  { path: '/user/services', component: GiveLessons, beforeEnter: [authenticated] },
  { path: '/user/services/template', component: ServiceTemplate, beforeEnter: [authenticated] },
  { path: '/user/services/:id/template', component: ServiceTemplate, beforeEnter: [authenticated] },
  { path: '/user/login', component: UserLogin },
  { path: '/user/calendar', component: Calendar , beforeEnter: [authenticated] },
  { path: '/chat', component: Chat, beforeEnter: [authenticated]},
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
