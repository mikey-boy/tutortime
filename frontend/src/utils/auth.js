import { store } from './store'

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

export function refreshUserID() {
  let cookie = getCookie('UserID')
  if (cookie == undefined) {
    store.UserID = 0;
  } else {
    store.UserID = Number(cookie)
  }
}

function removeCookie(name) {
  document.cookie = name + '=; Max-Age=0; path=/;';
}

export function logoutUser() {
  removeCookie('Token')
}