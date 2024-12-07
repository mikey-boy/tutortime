<template>
  <div v-if="service" class="post-flex-container">
    <div class="post">
      <h2>{{ service.title }}</h2>
      <div class="profile">
        <img :src="service.Image.Path" />
        <div class="profile-info">
          <a href="">{{ service.User.Username }}</a>
          <span>has taught this lesson: nil times<br />for a total of: {{ service.Minutes }} minutes</span>
        </div>
      </div>
      <div class="image-container">
        <img :src="service.Image.Path" />
      </div>
      <p>{{ service.Description }}</p>
    </div>
    <div class="post availability">
      <h2>{{ service.User.Username }}'s availability</h2>
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
            <!-- {% for i in range(7) %} {% if i|string ~ "-0" in availability %}
            <td><i class="fa-regular fa-square-check"></i></td>
            {% else %} -->
            <td v-for="i in 7"><i class="fa-regular fa-square"></i></td>
            <!-- {% endif %} {% endfor %} -->
          </tr>
          <tr>
            <td>afternoon</td>
            <td v-for="i in 7"><i class="fa-regular fa-square"></i></td>
          </tr>
          <tr>
            <td>evening</td>
            <td v-for="i in 7"><i class="fa-regular fa-square"></i></td>
          </tr>
        </tbody>
      </table>
      <div class="flex-container">
        <button class="blue-button" @click="messageUser(service.User.ID)">
          <i class="fa-regular fa-paper-plane"></i> Message {{ service.User.Username }}
        </button>
        <button class="green-button">
          <i class="fa-regular fa-user"></i> View {{ service.User.Username }}'s profile
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      service: null,
    };
  },
  async created() {
    const response = await fetch(`/api/services/${this.$route.params.id}`);
    this.service = await response.json();
  },
  methods: {
    messageUser(UserID) {
      this.$router.push({ path: "/chat/", query: { user: UserID } });
    },
  },
};
</script>

<style>
.post-flex-container {
  display: flex;
  margin: 30px auto;
  max-width: 1000px;
  min-width: 800px;

  .post {
    flex: 4;
    margin-right: 10px;
  }
  .availability {
    align-self: flex-start;
    flex: 3;
  }
  .flex-container {
    button {
      flex: 1;
      margin: 15px 10px 0px 10px;
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
.availability-table {
  table-layout: fixed;
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 10px;

  tr {
    text-align: center;

    td:first-child {
      text-align: left;
      width: 70px;
    }
    .fa-square-check {
      color: var(--green0);
    }
  }
  tbody tr:hover {
    background-color: var(--base1);
  }
}
</style>
