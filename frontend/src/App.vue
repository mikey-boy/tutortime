<template>
  <NavBar />
  <main class="body-content">
    <RouterView />
  </main>
  <button id="theme-switch" @click="themeToggle">
    <i class="fa-solid fa-moon fa-2xl"></i>
  </button>
  <footer></footer>
</template>

<script>
import NavBar from "./components/NavBar.vue";
import { refreshUserID } from "./utils/auth";

var theme = null;

function setTheme() {
  document.querySelector("html").setAttribute("data-theme", theme);
}
function saveTheme() {
  localStorage.setItem("theme", theme);
}

export default {
  created() {
    refreshUserID();

    let localStorageTheme = localStorage.getItem("theme");
    let systemSettingDark = window.matchMedia("(prefers-color-scheme: dark)");
    if (localStorageTheme !== null) {
      theme = localStorageTheme;
    } else if (systemSettingDark.matches) {
      theme = "dark";
    } else {
      theme = "light";
    }
    setTheme();
  },
  components: {
    NavBar,
  },
  methods: {
    themeToggle() {
      theme = theme === "dark" ? "light" : "dark";
      setTheme();
      saveTheme();
    },
  },
};
</script>

<style lang="scss">
@import "@/assets/styles/globals.scss";

footer {
  width: 100%;
  height: 100px;
}

#theme-switch {
  position: fixed;
  display: flex;
  justify-content: center;
  align-items: center;
  right: 40px;
  bottom: 40px;
  border-radius: 50%;
  color: var(--base0);
  background: var(--base2);
  width: 45px;
  height: 45px;

  &:hover {
    background: var(--text0);
  }
}
.body-content {
  width: 90%;
  max-width: 1440px;
  margin: auto;
}
</style>
