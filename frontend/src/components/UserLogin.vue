<template>
  <div class="login-container">
    <div class="login-box">
      <h2 v-show="loginOptions != 2">Login</h2>
      <h2 v-show="loginOptions == 2">Create account</h2>

      <div v-show="loginOptions == -1">
        <button class="login-button" @click="googleAccount">
          <div><img src="@/assets/img/signin-assets/google.svg" /></div>
          Login with Google
        </button>
        <span v-if="testing">
          <button class="login-button" @click="localAccount(0)">
            <div><i class="fa-solid fa-user fa-xl" /></div>
            Login with Local Account
          </button>

          <p>or</p>

          <button class="login-button" @click="localAccount(1)">
            <div><i class="fa-solid fa-user fa-xl" /></div>
            Create a Local Account
          </button>
        </span>
      </div>

      <div v-show="loginOptions != -1" @submit.prevent>
        <form>
          <label>Username:</label>
          <input v-model="user.username" type="text" required />
          <label>Password: </label>
          <input v-model="user.password" type="password" required />
          <button v-if="loginOptions == 1" class="local-login-button" @click="localAccountLogin()">Login</button>
          <button v-else class="local-signup-button" @click="localAccountCreate()">Create account</button>
          <p class="error-text" v-show="error">{{ error }}</p>
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
      user: {},
      error: "",
      loginOptions: -1,
      testing: false,
    };
  },
  created() {
    this.navigateView();
    if (import.meta.env.DEV) {
      this.testing = true;
    }
  },
  methods: {
    navigateView() {
      if (this.$route.query.view == "localAccountLogin") {
        this.loginOptions = 1;
      } else if (this.$route.query.view == "localAccountCreation") {
        this.loginOptions = 2;
      } else {
        this.loginOptions = -1;
      }
      this.user = {};
      this.error = "";
    },
    googleAccount() {
      if (this.$route.query.redirect) {
        window.location.href = `/api/user/authorize/google?redirect=${this.$route.query.redirect}`;
      } else {
        window.location.href = "/api/user/authorize/google";
      }
    },
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
      })
        .then((response) => {
          if (response.status == 200) {
            refreshUserID();
            if (this.$route.query.redirect != null) {
              this.$router.push({ path: this.$route.query.redirect });
            } else {
              this.$router.push({ path: "/" });
            }
          }
          if (response.headers.get("Content-Length") == 0) {
            return null;
          }
          return response.json();
        })
        .then((data) => {
          if (data) {
            this.error = data.details;
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
      this.navigateView();
    },
  },
};
</script>

<style lang="scss">
@import "@/assets/styles/mixins.scss";

.error-text {
  margin: 10px 0px 0px;
}
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
    padding: 0px 30px 20px;
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
