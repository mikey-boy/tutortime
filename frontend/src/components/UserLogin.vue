<template>
  <div class="login-container">
    <div class="login-box">
      <h2>Login</h2>

      <div v-show="socialView">
        <a class="login-button" href="">
          <div><img src="@/assets/img/signin-assets/google.svg" /></div>
          Login with Google
        </a>
        <!-- <a class="login-button" href="">
          <img src="" />
          Login with Facebook
        </a> -->
        <a class="login-button local-account" @click="socialView = 0">
          <div><i class="fa-solid fa-user fa-xl" /></div>
          Login with Local Account
        </a>
      </div>

      <div v-show="!socialView" @submit.prevent>
        <form id="local-account-form">
          <label>Username:</label>
          <input v-model="user.username" type="text" required />
          <label>Password: </label>
          <input v-model="user.password" type="password" required />
          <button class="local-login-button" @click="localAccountLogin()">Login</button>
          <button class="local-signup-button" @click="localAccountCreate()">Create account</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { refreshUserID } from "../utils/auth";

export default {
  data() {
    return {
      socialView: 1,
      user: {},
    };
  },
  methods: {
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
    border: 3px solid var(--blue1);

    input {
      width: 100%;
      padding: 10px;
      margin-bottom: 10px;
      border-radius: 3px;
      border: none;
      box-sizing: border-box;
    }

    button {
      @include common-button;
      margin-top: 10px;
    }

    .login-button {
      display: flex;
      align-items: center;
      border: 2px solid var(--text0);
      border-radius: 3px;
      margin-top: 10px;
      font-weight: bold;
      color: var(--text0);
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
      background-color: var(--blue0);
    }

    .local-signup-button {
      background-color: var(--green1);
    }
  }
}
</style>
