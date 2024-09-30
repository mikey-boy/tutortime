<template>
  <div class="login-container">
    <div class="login-box">
      <h2>Login</h2>

      <div v-show="socialView">
        <a class="login-button" href="">
          <img src="@/assets/img/signin-assets/google.svg" />
          Login with Google
        </a>
        <!-- <a class="login-button" href="">
          <img src="" />
          Login with Facebook
        </a> -->
        <a class="login-button" @click="socialView = 0">
          <div><i class="fa-solid fa-user fa-lg" /></div>
          Use test credentials
        </a>
      </div>

      <div v-show="!socialView">
        <form id="local-account-form" @submit.prevent>
          <label for="username">Username:</label>
          <input type="text" name="username" required />
          <label for="password">Password: </label>
          <input type="password" name="password" required />
          <button class="local-login-button" @click="localAccount(true)">Login</button>
          <button class="local-signup-button" @click="localAccount(false)">Create account</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      socialView: 1,
    };
  },
  methods: {
    localAccount(login) {
      const form = new FormData(document.querySelector("#local-account-form"));
      const jsonObject = {};
      form.forEach((value, key) => {
        jsonObject[key] = value;
      });

      if (!jsonObject["username"] || !jsonObject["password"]) {
        return;
      }

      // Convert the object to JSON string
      const json = JSON.stringify(jsonObject);
      const path = login == true ? "/api/sessiontoken" : "/api/users";
      fetch(path, {
        method: "POST",
        body: json,
      })
        .then((response) => {
          if (response.status == 200) {
            this.$router.push({ path: "/" });
          } else {
          }
        })
        .catch((error) => {
          console.error("Error fetching data:", error);
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

    .login-button img,
    .login-button div {
      text-align: center;
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
