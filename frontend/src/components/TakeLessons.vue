<template>
  <div>
    <form id="service-filter-box" @submit.prevent="getServices">
      <select v-model="category">
        <option value="">All</option>
        <option value="language">Language learning</option>
        <option value="software">Software development</option>
        <option value="music">Music lessons</option>
        <option value="wellness">Wellness</option>
        <option value="other">Other</option>
      </select>
      <input v-model="query" type="text" placeholder="Search..." />
      <button><i class="fa-solid fa-magnifying-glass fa-lg"></i></button>
    </form>
    <div class="post-grid-container">
      <template v-for="service in services" :key="service.ID">
        <RouterLink :to="{ path: `/services/${service.ID}` }">
          <div class="post clickable">
            <div class="image-container">
              <img :src="service.Image.Path" :alt="service.Image.Name" />
            </div>
            <h3 class="truncated-text">{{ service.Title }}</h3>
            <p class="truncated-text">{{ service.Description }}</p>
            <p>{{ service.User.Username }}</p>
          </div>
        </RouterLink>
      </template>
    </div>
    <div id="service-page-control">
      <template v-if="page > 1">
        <button @click="getServices(page - 1)"><i class="fa-solid fa-chevron-left"></i> Previous</button>
      </template>

      <template v-for="i in total_pages">
        <template v-if="page == i">
          <button class="active-page">{{ i }}</button>
        </template>
        <template v-else-if="[1, page - 1, page, page + 1, total_pages].includes(i)">
          <button @click="getServices(i)">{{ i }}</button>
        </template>
        <template v-else-if="[2, total_pages - 1].includes(i)">
          <i class="fa-solid fa-ellipsis"></i>
        </template>
      </template>

      <template v-if="page < total_pages">
        <button @click="getServices(page + 1)">Next<i class="fa-solid fa-chevron-right"></i></button>
      </template>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      services: [],
      page: null,
      category: null,
      query: null,
      total_pages: null,
    };
  },
  mounted() {
    this.fetchServiceParams();
    this.getServices();
  },
  methods: {
    fetchServiceParams() {
      this.page = this.$route.query.page || 1;
      this.category = this.$route.query.category || "";
      this.query = this.$route.query.query || "";
    },
    getServices() {
      const url = new URL("/api/services", window.location.origin);
      const params = { category: this.category, query: this.query, page: this.page };
      url.search = new URLSearchParams(params).toString();
      fetch(url)
        .then((response) => response.json())
        .then((json) => {
          this.services = json.Services;
          this.page = json.Page;
          this.total_pages = json.TotalPages;
          if (params.category != "" || params.query != "" || params.page != 1) {
            this.$router.push({ path: "/", query: params });
          }
        });
    },
  },
  watch: {
    $route: function (val, oldVal) {
      if (val.fullPath == "/") {
        this.fetchServiceParams();
        this.getServices();
      }
    },
  },
};
</script>

<style lang="scss">
.post {
  padding: 15px;
  border-radius: 5px;
  border: 1px solid var(--green0);
  background-color: var(--base1);

  h2 {
    margin-top: 0px;
    margin-bottom: 15px;
  }
  p {
    color: var(--text0);
  }
  &.clickable:hover {
    background-color: var(--base0);
  }
}
.post-grid-container {
  display: grid;
  gap: 25px;
  grid-template-columns: repeat(auto-fill, 340px);
  padding-bottom: 40px;

  .post {
    width: 300px;
  }
}
.image-container {
  img {
    width: 300px;
    height: 170px;
  }
}
#service-filter-box {
  margin: 25px 10px;

  input {
    padding: 6px;
    margin-right: 8px;
    border-radius: 3px;
    width: 200px;
    border: 1px solid var(--base2);
  }
  select {
    padding: 6px;
    margin-right: 4px;
    border-radius: 3px;
    border: 1px solid var(--base2);
  }
  button {
    padding: 7px 10px;
    background-color: var(--green1);
    color: var(--text1);
  }
}
#service-page-control {
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: larger;
  margin-bottom: 50px;

  button {
    margin: 5px;
    padding: 3px 10px;
    font-size: large;
    color: var(--text1);
    border: 1px solid var(--green0);
  }
  button:hover {
    background-color: var(--base1);
  }
  button.active-page {
    border-radius: 3px;
    background-color: var(--green1);
  }
  .fa-ellipsis {
    color: var(--base2);
  }
}
</style>
