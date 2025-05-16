<template>
  <div v-if="user.Availability">
    <div id="account-details">
      <h2>Account details</h2>
    </div>
    <div id="user-account-list">
      <div class="label">Profile Picture</div>
      <img id="profile-pic" :src="user.Image.Path" />

      <div class="label">Display Name</div>
      <div>
        <p>{{ user.Username }}</p>
      </div>

      <div class="label">Availability</div>
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
              <i :class="isChecked(i + '-0') ? 'fa-solid fa-square-check' : 'fa-regular fa-square'"></i>
            </td>
          </tr>
          <tr>
            <td>afternoon</td>
            <td v-for="i in 7">
              <i :class="isChecked(i + '-1') ? 'fa-solid fa-square-check' : 'fa-regular fa-square'"></i>
            </td>
          </tr>
          <tr>
            <td>evening</td>
            <td v-for="i in 7">
              <i :class="isChecked(i + '-2') ? 'fa-solid fa-square-check' : 'fa-regular fa-square'"></i>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="label">About Me</div>
      <div>
        <p v-if="user.Description">{{ user.Description }}</p>
        <p v-else><i>No description provided</i></p>
      </div>
    </div>
  </div>

  <h2>Service history</h2>
  <div v-if="services.length > 0">
    <table class="standard-table">
      <thead>
        <tr>
          <td>Service</td>
          <td>Description</td>
          <td>Lessons taught</td>
          <td>Minutes taught</td>
          <td>Status</td>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(service, index) in services" :key="service.ID">
          <RouterLink :to="{ path: `/services/${service.ID}` }">
            <td>
              <b>{{ service.Title }}</b>
            </td>
          </RouterLink>
          <td>{{ service.Description }}</td>
          <td>{{ service.Lessons }}</td>
          <td>{{ service.Minutes }}</td>
          <td>{{ service.Status }}</td>
        </tr>
      </tbody>
    </table>
  </div>
  <div v-else>
    <div class="empty-container">
      <div>
        <p>{{ user.Username }} doesn't offer any services!</p>
      </div>
    </div>
  </div>
</template>

<script>
import { store } from "@/utils/store";
import { parseDate, parseTime } from "@/utils/utils";

export default {
  data() {
    return {
      store,
      page: 1,
      user: {},
      lessons: [],
      services: [],
      modify: false,
      imageUrl: "",
    };
  },
  mounted() {
    this.getProfile();
    this.getServices();
  },
  methods: {
    parseDate,
    parseTime,
    async getProfile() {
      const response = await fetch(`/api/users/${this.$route.params.id}`);
      this.user = await response.json();
      this.user.Availability = this.user.Availability.split(",");
    },
    async getServices() {
      const response = await fetch(`/api/users/${this.$route.params.id}/services`);
      this.services = await response.json();
    },
    isChecked(value) {
      if (this.user.Availability.includes(value)) {
        return true;
      }
      return false;
    },
  },
};
</script>

<style scoped>
#account-details {
  max-width: 840px;
  display: flex;
  align-items: center;
  h3 {
    margin-left: auto;
    color: var(--text0);
  }
}
#user-account-list {
  max-width: 800px;
  border: 1px dashed var(--green0);
  padding: 20px;

  input {
    padding: 4px;
  }
  textarea {
    width: calc(100% - 8px);
  }

  .label {
    font-weight: bold;
    margin: 30px 0px 10px 0px;
  }
  .label:first-child {
    margin-top: 0px;
  }
  #profile-pic {
    width: 75px;
    height: 75px;
    border-radius: 50%;
  }
  #profile-pic-label {
    cursor: pointer;
    margin-left: 10px;
  }
}
</style>
