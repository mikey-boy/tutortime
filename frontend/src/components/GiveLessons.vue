<template>
  <div>
    <table id="user-service-nav">
      <thead>
        <tr>
          <th>
            <button class="service-status" :class="{ highlighted: status == 'active' }" @click="changeStatus('active')">
              Active
            </button>
          </th>
          <th>
            <button class="service-status" :class="{ highlighted: status == 'paused' }" @click="changeStatus('paused')">
              Paused
            </button>
          </th>
          <th><button id="new-service-button" @click="createService()">New service</button></th>
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
        <tr v-for="service in services" v-show="service.Status == status" :key="service.ID">
          <td class="truncated">{{ service.Title }}</td>
          <td class="truncated">{{ service.Description }}</td>
          <td class="actions">
            <button @click="editService(service.ID)">
              <i class="fa-regular fa-pen-to-square fa-xl"></i>
            </button>
            <button v-if="service.Status == 'active'" @click="editServiceStatus(service.ID, 'paused')">
              <i class="fa-regular fa-circle-pause fa-xl"></i>
            </button>
            <button v-if="service.Status == 'paused'" @click="editServiceStatus(service.ID, 'active')">
              <i class="fa-regular fa-circle-play fa-xl"></i>
            </button>
            <button @click="editServiceStatus(service.ID, 'cancelled')">
              <i class="fa-regular fa-trash-can fa-xl"></i>
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import ServiceTemplate from "./ServiceTemplate.vue";

export default {
  components: {
    ServiceTemplate,
  },
  beforeRouteUpdate(to, from) {
    this.status = to.query.status || "active";
  },
  data() {
    return {
      services: [],
      status: this.$route.query.status || "active",
    };
  },
  mounted() {
    this.getServices();
  },
  methods: {
    getServices() {
      fetch("/api/users/me/services")
        .then((response) => response.json())
        .then((data) => (this.services = data));
    },
    changeStatus(status) {
      this.$router.push({ path: "/user/services", query: { status: status } });
    },
    createService() {
      this.$router.push({ path: "/user/services/template" });
    },
    editService(serviceID) {
      this.$router.push({ path: `/user/services/${serviceID}/template` });
    },
    editServiceStatus(serviceID, status) {
      fetch(`/api/services/${serviceID}`, {
        method: "PUT",
        body: JSON.stringify({ status: status }),
      })
        .then(() => this.getServices())
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
  .highlighted {
    max-width: 300px;
    border: 1px solid var(--green0);
    border-radius: 3px;
    font-weight: bold;
  }
  .service-status {
    @include common-button();
    background-color: var(--base0);
    font-size: inherit;
  }
  #new-service-button {
    @include common-button();
    background-color: var(--green1);
    max-width: 130px;
  }
}

.user-service-table {
  table-layout: fixed;
  width: 100%;
  border: 1px dashed var(--green0);
  border-spacing: 0;
  padding: 10px;

  td,
  th {
    padding: 3px;
  }
  tbody tr:hover {
    background-color: var(--base1);
  }
  th {
    width: 70px;
  }
  th.description {
    width: 450px;
  }
  th.title {
    width: 150px;
  }
  .truncated {
    white-space: nowrap; /* Prevent text from wrapping */
    overflow: hidden; /* Hide overflowing text */
    text-overflow: ellipsis;
  }
  .actions {
    button {
      background-color: transparent;
    }
  }
}
</style>
