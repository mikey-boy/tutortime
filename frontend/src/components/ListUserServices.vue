<template>
  <div>
    <table id="user-service-nav">
      <thead>
        <tr>
          <th><button class="user-service-status">Active</button></th>
          <th><button class="user-service-status">Paused</button></th>
          <th><button id="new-service-button">New service</button></th>
        </tr>
      </thead>
    </table>
    <table class="user-service-table">
      <thead>
        <tr>
          <th class="title">Title</th>
          <th class="description">Description</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="service in services" :key="service.id">
          <td class="truncated">{{ service.Title }}</td>
          <td class="truncated">{{ service.Description }}</td>
          <td class="actions">
            <a href="/user/service/update/"><i class="fa-regular fa-pen-to-square fa-lg"></i></a>
            <a href="/user/service/pause/"><i class="fa-regular fa-circle-pause fa-lg"></i></a>
            <a href="/user/service/activate/"><i class="fa-regular fa-circle-play fa-lg"></i></a>
            <a href="/user/service/delete/"><i class="fa-regular fa-trash-can fa-lg"></i></a>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  data() {
    return {
      services: [],
    };
  },
  mounted() {
    this.getServices();
  },
  methods: {
    getServices() {
      fetch("/api/services")
        .then((response) => response.json())
        .then((data) => (this.services = data))
        .catch((error) => {
          console.error("Error fetching data:", error);
        });
    },
  },
};
</script>

<style lang="scss">
@import "@/assets/styles/mixins.scss";

#user-service-nav {
  width: 100%;
  table-layout: fixed;
  margin: 20px 0px;

  th {
    text-align: center;
  }
  .active-subnav-header {
    border: 1px solid var(--green0);
    border-radius: 3px;
    font-weight: bold;
  }
  .user-service-status {
    @include common-button();
    font-size: inherit;
    color: var(--text0);
    background-color: var(--base0);
  }
  #new-service-button {
    @include common-button();
    color: var(--green1);
    max-width: 130px;
  }
}
</style>
