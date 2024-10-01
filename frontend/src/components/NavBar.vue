<template>
  <div id="nav-container">
    <div id="nav">
      <h1>Tutortime</h1>
      <ul>
        <li>
          <RouterLink to="/">
            <h3>Take lessons</h3>
          </RouterLink>
        </li>
        <li>
          <RouterLink :to="{ path: '/user/services', query: { status: 'active' } }">
            <h3>Give lessons</h3>
          </RouterLink>
        </li>
        <!-- <li>
          <RouterLink to="/">
            <h3>How it works</h3>
          </RouterLink>
        </li>
        <li>
          <RouterLink to="/">
            <h3>Learning hub</h3>
          </RouterLink>
        </li> -->
      </ul>
      <ul v-if="!isLoggedIn()" class="user-buttons">
        <li>
          <RouterLink to="/user/login">
            <h3>Login</h3>
          </RouterLink>
        </li>
      </ul>
      <ul v-else class="user-buttons">
        <li>
          <RouterLink to="/"><i class="fa-regular fa-calendar-days fa-lg"></i></RouterLink>
        </li>
        <li>
          <RouterLink to="/"><i class="fa-regular fa-paper-plane fa-lg"></i></RouterLink>
        </li>
        <li>
          <span @click="modal = !modal"><i class="fa-regular fa-user fa-lg"></i></span>
        </li>
        <div class="relative-container" v-if="modal">
          <div id="user-modal-popout">
            <div>
              <RouterLink to="/"><div class="options">Profile</div></RouterLink>
              <RouterLink to="/"><div class="options">Logout</div></RouterLink>
            </div>
          </div>
        </div>
      </ul>
    </div>
  </div>
</template>

<script>
import { isLoggedIn } from "../utils/auth";

export default {
  data() {
    return {
      modal: false,
    };
  },
  methods: {
    isLoggedIn() {
      return isLoggedIn();
    },
  },
};
</script>

<style lang="scss">
#nav-container {
  display: flex;
  justify-content: center;
  background-color: var(--base1);
  height: 70px;
  width: 100%;

  #nav {
    display: flex;
    flex-direction: row;
    text-align: center;
    align-items: center;
    max-width: 1440px;
    width: 100%;

    h1,
    h3 {
      padding: 25px;
      margin: 0px;
    }

    i {
      padding: 4px;
    }

    ul {
      margin: 0px;
      padding: 0px;
      display: flex;
      list-style: none;
      align-items: center;
    }

    .user-buttons {
      justify-content: flex-end;
      margin-left: auto;
      padding: 10px;
      cursor: pointer;

      i {
        color: var(--text0);
      }
      i:hover {
        color: var(--text1);
      }
    }
  }
}
#user-modal-popout {
  position: absolute;
  z-index: 100;
  top: 15px;
  right: 3px;
  text-align: left;
  background-color: var(--base0);
  border: 2px solid var(--green0);
  border-radius: 3px;
  font-weight: 600;

  .options {
    color: var(--text1);
    padding: 5px 15px;
  }
  .options:hover {
    background-color: var(--base1);
  }
}
</style>
