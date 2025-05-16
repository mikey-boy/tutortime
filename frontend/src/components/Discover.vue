<template>
  <div id="discover-container">
    <div id="pages">
      <ul>
        <li :class="{ active: page == 'how-it-works' }" @click="changePage('how-it-works')">
          <span>How it works</span>
        </li>
        <li :class="{ active: page == 'giving-lessons' }" @click="changePage('giving-lessons')">
          <span>Giving lessons</span>
        </li>
        <li :class="{ active: page == 'taking-lessons' }" @click="changePage('taking-lessons')">
          <span>Taking lessons</span>
        </li>
        <li :class="{ active: page == 'faq' }" @click="changePage('faq')">
          <span>FAQ</span>
        </li>
      </ul>
    </div>
    <div id="page-container">
      <div class="page" v-show="page == 'how-it-works'">
        <h1>How it works</h1>
      </div>
      <div class="page" v-show="page == 'giving-lessons'">
        <h1>Giving lessons</h1>
      </div>
      <div class="page" v-show="page == 'taking-lessons'">
        <h1>Taking lessons</h1>
      </div>
      <div class="page" v-show="page == 'faq'">
        <h1>Frequently asked questions</h1>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      page: this.$route.query.page || "how-it-works",
    };
  },
  methods: {
    changePage(page) {
      this.page = page;
      this.$router.push({ path: `/discover`, query: { page: page } });
    },
  },
};
</script>

<style>
#discover-container {
  display: flex;
  margin: 0 auto;
  height: 890px;
}
#pages {
  flex: 1;
  margin: 60px 75px 0px 0px;

  ul {
    list-style: none;
    padding: 0;
    border: 2px solid var(--green0);
    border-radius: 3px;
  }
  li {
    cursor: pointer;
    color: var(--text0);
    text-align: center;
    border-radius: 3px;
    padding: 8px;
    &:hover {
      background-color: var(--base1);
    }
  }
  li.active {
    background-color: var(--base1);
  }
}
#page-container {
  flex: 7;

  .page {
  }
}
</style>
