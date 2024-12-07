<template>
  <RouterLink :to="{ path: `/services/${service.ID}` }">
    <h3>{{ service.Title }}</h3>
  </RouterLink>
  <div>Date: {{ parseDate(lesson.Datetime) }}</div>
  <div>Time: {{ parseTime(lesson.Datetime) }}</div>
  <div>Duration: {{ lesson.Duration }} minutes</div>
  <div v-if="lesson.Status == 'confirmed' || lesson.Status == 'accepted'">Status: {{ lesson.Status }}</div>
  <div v-else>
    <button class="accept-button" @click="modifyLesson('accepted')">Confirm</button>
    <button class="modify-button">Modify</button>
    <button class="cancel-button" @click="modifyLesson('cancelled')">Cancel</button>
  </div>
</template>

<script>
export default {
  props: {
    lesson: Object,
    service: Object,
  },
  methods: {
    parseDate(datetime) {
      if (datetime) {
        return datetime.split("T")[0];
      }
    },
    parseTime(datetime) {
      if (datetime) {
        return datetime.split("T")[1].slice(0, 5);
      }
    },
    async modifyLesson(status) {
      this.lesson.Status = status;
      const lessonRequest = await fetch(`/api/lessons/${this.lesson.ID}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(this.lesson),
      });
      this.lesson = await lessonRequest.json();
    },
  },
  // computed: {
  //   getStatus() {
  //     if (lesson.Status == "completed")
  //   }
  // }
};
</script>

<style lang="scss" scoped>
button {
  font-size: medium;
  margin: 10px 2px auto;
  width: 65px;
  color: var(--text1);

  a {
    color: var(--text1);
  }
}
.accept-button {
  background-color: var(--green1);
}
.cancel-button {
  background-color: var(--red);
}
.modify-button {
  background-color: var(--orange);
}
.warning {
  border: 1px solid var(--red);
}
.warning-text {
  color: var(--orange);
  font-weight: bolder;
}
</style>
