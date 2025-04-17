<template>
  <div class="login-container">
    <div class="login-box">
      <h2 v-show="loginOptions != 2">Login</h2>
      <h2 v-show="loginOptions == 2">Create account</h2>

      <div v-show="loginOptions == -1">
        <button class="login-button" href="">
          <div><img src="@/assets/img/signin-assets/google.svg" /></div>
          Login with Google
        </button>
        <button class="login-button local-account" @click="localAccount(0)">
          <div><i class="fa-solid fa-user fa-xl" /></div>
          Login with Local Account
        </button>

        <p>or</p>

        <button class="login-button local-account" @click="localAccount(1)">
          <div><i class="fa-solid fa-user fa-xl" /></div>
          Create a Local Account
        </button>
      </div>

      <div v-show="loginOptions != -1" @submit.prevent>
        <form id="local-account-form">
          <label>Username:</label>
          <input v-model="user.username" type="text" required />
          <label>Password: </label>
          <input v-model="user.password" type="password" required />
          <button v-show="loginOptions == 1" class="local-login-button" @click="localAccountLogin()">Login</button>
          <button v-show="loginOptions == 2" class="local-signup-button" @click="localAccountCreate()">
            Create account
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { refreshUserID } from "@/utils/auth";

export default {
  data() {
    return {
      loginOptions: -1,
      user: {},
    };
  },
  methods: {
    localAccount(loginOrCreate) {
      if (loginOrCreate) {
        this.$router.push({ path: "/user/login", query: { ...this.$route.query, view: "localAccountCreation" } });
      } else {
        this.$router.push({ path: "/user/login", query: { ...this.$route.query, view: "localAccountLogin" } });
      }
    },
    localAccountLogin() {
      if (!this.user.username || !this.user.password) {
        return;
      }
      const json = JSON.stringify(this.user);
      fetch("/api/sessiontoken", {
        method: "POST",
        body: json,
      }).then((response) => {
        if (response.status == 200) {
          refreshUserID();
          if (this.$route.query.redirect != null) {
            this.$router.push({ path: this.$route.query.redirect });
          } else {
            this.$router.push({ path: "/" });
          }
        }
      });
    },
    localAccountCreate() {
      if (!this.user.username || !this.user.password) {
        return;
      }
      const json = JSON.stringify(this.user);
      fetch("/api/users", {
        method: "POST",
        body: json,
      }).then((response) => {
        if (response.status == 200) {
          refreshUserID();
          this.$router.push({ path: "/user/profile" });
        }
      });
    },
  },
  watch: {
    $route: function (val, oldVal) {
      if (val.query.view == "localAccountLogin") {
        this.loginOptions = 1;
      } else if (val.query.view == "localAccountCreation") {
        this.loginOptions = 2;
      } else {
        this.loginOptions = -1;
      }
    },
  },
};
</script>

<style lang="scss">
@import "@/assets/styles/mixins.scss";

.login-container {
  position: absolute;
  top: 40%;
  left: 50%;
  transform: translate(-50%, -50%);

  .login-box {
    display: flex;
    flex-direction: column;
    width: 300px;
    background-color: var(--base0);
    padding: 30px;
    padding-top: 0px;
    border-radius: 5px;
    border: 3px solid var(--text0);

    input {
      width: 100%;
      padding: 10px;
      margin-bottom: 10px;
      border-radius: 3px;
      border: none;
      box-sizing: border-box;
    }

    button {
      width: 100%;
      margin-top: 10px;
    }

    .login-button {
      font-size: medium;
      display: flex;
      align-items: center;
      border: 2px solid var(--text0);
      border-radius: 3px;
      margin-top: 10px;
      font-weight: bold;
      color: var(--text0);
      background-color: var(--base0);

      &:hover {
        background-color: var(--base1);
      }
    }

    .login-button div {
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 7px;
      margin-right: 15px;
      width: 30px;
      height: 30px;
    }

    .local-login-button {
      @include common-button;
      background-color: var(--blue0);
    }

    .local-signup-button {
      @include common-button;
      background-color: var(--green1);
    }
  }
}
</style>
