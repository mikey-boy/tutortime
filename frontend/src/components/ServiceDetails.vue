<template>
  <div v-if="service && user" class="post-flex-container">
    <div class="post">
      <h2>{{ service.Title }}</h2>
      <div class="profile">
        <img :src="user.Image.Path" />
        <div class="profile-info">
          <RouterLink :to="{ path: `/users/${user.ID}` }">
            {{ user.Username }}
          </RouterLink>
          <span>taught this lesson {{ service.Lessons }} times<br />for a total of {{ service.Minutes }} minutes</span>
        </div>
      </div>
      <div class="image-container">
        <img :src="service.Image.Path" />
      </div>
      <p>{{ service.Description }}</p>
    </div>
    <div class="availability">
      <div class="post">
        * If you would like to book a lesson with {{ user.Username }} start by sending them a message
      </div>
      <div class="post">
        <h2>{{ user.Username }}'s availability</h2>
        <table class="availability-table">
          <thead>
            <tr>
              <td></td>
              <td>Mon</td>
              <td>Tue</td>
              <td>Wed</td>
              <td>Thu</td>
              <td>Fri</td>
              <td>Sat</td>
              <td>Sun</td>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>morning</td>
              <td v-for="i in 7">
                <i :class="isChecked(i + '-0')"></i>
              </td>
            </tr>
            <tr>
              <td>afternoon</td>
              <td v-for="i in 7">
                <i :class="isChecked(i + '-1')"></i>
              </td>
            </tr>
            <tr>
              <td>evening</td>
              <td v-for="i in 7">
                <i :class="isChecked(i + '-2')"></i>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="flex-container">
          <RouterLink :to="{ path: `/chat/${user.ID}` }">
            <button class="blue-button"><i class="fa-solid fa-paper-plane"></i> Send message</button>
          </RouterLink>
          <RouterLink :to="{ path: `/users/${user.ID}` }">
            <button class="green-button"><i class="fa-solid fa-user"></i> View profile</button>
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      user: null,
      service: null,
    };
  },
  async created() {
    const serviceResponse = await fetch(`/api/services/${this.$route.params.id}`);
    this.service = await serviceResponse.json();
    const userResponse = await fetch(`/api/users/${this.service.UserID}`);
    this.user = await userResponse.json();
  },
  methods: {
    isChecked(value) {
      if (this.user.Availability.includes(value)) {
        return "fa-solid fa-square-check";
      }
      return "fa-regular fa-square";
    },
  },
};
</script>

<style scoped>
@import "@/assets/styles/mixins.scss";
.fa-circle-info {
  margin-right: 5px;
}
.post-flex-container {
  display: flex;
  margin: 30px auto;
  max-width: 1000px;
  min-width: 800px;

  .post {
    flex: 4;
    margin: 0px 10px 10px 0px;
  }
  .availability {
    align-self: flex-start;
    flex: 3;
  }
  .flex-container {
    a {
      flex: 1;
      margin: 15px 10px 0px 10px;
    }
    button {
      padding: 8px;
    }
  }
}
.profile {
  display: flex;
  align-items: center;
  margin-bottom: 20px;

  img {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    border-right: 20px;
  }
  .profile-info {
    display: flex;
    align-items: center;

    a,
    p {
      font-size: larger;
      font-weight: bold;
      padding: 0px 13px;
    }
    span {
      padding-left: 10px;
      border-left: 1px solid var(--base2);
    }
  }
}
.image-container {
  position: relative;

  img {
    width: 300px;
    height: 170px;
  }
}
</style>
