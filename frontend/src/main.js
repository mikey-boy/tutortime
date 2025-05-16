import App from "./App.vue";

import { store } from "./utils/store";
import { createApp } from "vue";
import { createWebHashHistory, createRouter } from "vue-router";

import TakeLessons from "./components/TakeLessons.vue";
import ServiceDetails from "./components/ServiceDetails.vue";
import GiveLessons from "./components/GiveLessons.vue";
import ServiceTemplate from "./components/ServiceTemplate.vue";
import UserLogin from "./components/UserLogin.vue";
import UserProfile from "./components/UserProfile.vue";
import OtherProfile from "./components/OtherProfile.vue";
import Calendar from "./components/Calendar.vue";
import Chat from "./components/Chat.vue";
import Discover from "./components/Discover.vue";

function authenticated(to) {
  if (!store.UserID) {
    return { path: "/user/login", query: { redirect: to.path } };
  }
}

const routes = [
  { path: "/", component: TakeLessons },
  { path: "/services/:id/", component: ServiceDetails },
  { path: "/user/services", component: GiveLessons, beforeEnter: [authenticated] },
  { path: "/user/services/template", component: ServiceTemplate, beforeEnter: [authenticated] },
  { path: "/user/services/:id/template", component: ServiceTemplate, beforeEnter: [authenticated] },
  { path: "/user/login", component: UserLogin },
  { path: "/user/profile", component: UserProfile, beforeEnter: [authenticated] },
  { path: "/users/:id/", component: OtherProfile },
  { path: "/user/calendar", component: Calendar, beforeEnter: [authenticated] },
  { path: "/chat/:id?/", component: Chat, beforeEnter: [authenticated] },
  { path: "/discover", component: Discover },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

const app = createApp(App);
app.use(router);
app.mount("#app");
