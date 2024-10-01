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
      <div class="post" v-for="service in services" :key="service.ID">
        <div class="image-container">
          <img :src="service.Image.Path" :alt="service.Image.Name" />
        </div>
        <RouterLink :to="{ path: `/services/${service.ID}` }">
          <h3 class="truncated-text">{{ service.Title }}</h3>
        </RouterLink>
        <p class="truncated-text">{{ service.Description }}</p>
        <p>{{ service.User.Username }}</p>
      </div>
    </div>
    <div id="service-page-control"></div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      services: [],
      category: "",
      query: "",
    };
  },
  mounted() {
    this.getServices();
  },
  methods: {
    getServices() {
      const url = new URL("/api/services", window.location.origin);
      url.search = new URLSearchParams({ category: this.category, query: this.query }).toString();
      fetch(url)
        .then((response) => response.json())
        .then((data) => (this.services = data));
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
</style>
