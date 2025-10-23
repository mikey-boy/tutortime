<template>
  <div id="nav-container">
    <div id="nav">
      <RouterLink to="/">
        <h1>Tutortime</h1>
      </RouterLink>
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
        <li>
          <RouterLink :to="{ path: '/discover' }">
            <h3>Discover</h3>
          </RouterLink>
        </li>
      </ul>
      <ul v-if="!store.UserID" class="user-buttons">
        <li>
          <RouterLink to="/user/login">
            <h3>Login</h3>
          </RouterLink>
        </li>
      </ul>
      <ul v-else class="user-buttons">
        <li>
          <RouterLink to="/user/calendar"><i class="fa-solid fa-calendar-days fa-lg"></i></RouterLink>
        </li>
        <li>
          <RouterLink to="/chat">
            <i v-if="unreadMessages" class="unreadMessages fa-solid fa-paper-plane fa-lg"></i>
            <i v-else class="fa-solid fa-paper-plane fa-lg"></i>
          </RouterLink>
        </li>
        <li>
          <span @click="modal = !modal"><i class="fa-solid fa-user fa-lg"></i></span>
        </li>
        <div class="relative-container" v-if="modal">
          <div id="user-modal-popout">
            <div>
              <div class="options" @click="navToProfile()">Profile</div>
              <div class="options" @click="logout()">Logout</div>
            </div>
          </div>
        </div>
      </ul>
    </div>
  </div>
</template>

<script>
import { store } from "@/utils/store";
import { logoutUser } from "@/utils/auth";

export default {
  data() {
    return {
      modal: false,
      unreadMessages: false,
      store,
    };
  },
  watch: {
    $route(to, from) {
      this.checkUnreadMessages();
    },
  },
  methods: {
    navToProfile() {
      this.modal = false;
      this.$router.push({ path: "/user/profile" });
    },
    logout() {
      logoutUser();
      this.modal = false;
      this.$router.push({ path: "/" });
    },
    async checkUnreadMessages() {
      if (store.UserID != 0) {
        const response = await fetch("/api/rooms");
        const tmp = await response.json();
        this.unreadMessages = false;
        tmp.forEach((room) => {
          if (room.User1ID == store.UserID && room.UnreadUser1) {
            this.unreadMessages = true;
          } else if (room.User2ID == store.UserID && room.UnreadUser2) {
            this.unreadMessages = true;
          }
        });
      }
    },
  },
};
</script>

<style lang="scss">
#nav-container {
  display: flex;
  justify-content: center;
  height: 70px;
  width: 100%;
  position: sticky;
  top: 0;
  background-color: var(--base1);

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
        color: var(--green0);
      }
      i.unreadMessages {
        color: var(--green0);
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
    color: var(--text0);
    padding: 5px 15px;
  }
  .options:hover {
    background-color: var(--base1);
  }
}
</style>
