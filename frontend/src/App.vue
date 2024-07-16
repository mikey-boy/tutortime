<template>
  <NavBar />
  <main class="body-content">
    <RouterView />
  </main>
</template>

<script>
import NavBar from "./components/NavBar.vue";

export default {
  components: {
    NavBar,
  },
};

function calculateSettingAsThemeString(localStorageTheme, systemSettingDark) {
  if (localStorageTheme !== null) {
    return localStorageTheme;
  }

  if (systemSettingDark.matches) {
    return "dark";
  }

  return "light";
}

function updateThemeOnHtmlEl(theme) {
  document.querySelector("html").setAttribute("data-theme", theme);
}

function themeToggle() {
  currentThemeSetting = currentThemeSetting === "dark" ? "light" : "dark";
  localStorage.setItem("theme", currentThemeSetting);
  updateThemeOnHtmlEl(currentThemeSetting);
}

// const localStorageTheme = localStorage.getItem("theme");
// const systemSettingDark = window.matchMedia("(prefers-color-scheme: dark)");

// let currentThemeSetting = calculateSettingAsThemeString(localStorageTheme, systemSettingDark);
// updateThemeOnHtmlEl(currentThemeSetting);
</script>

<style lang="scss">
@import "@/assets/styles/globals.scss";

.body-content {
  width: 90%;
  min-width: 720px;
  max-width: 1440px;
  margin: auto;
}
</style>
