<template>
  <RouterLink :to="{ path: `/services/${service.ID}` }">
    <h3>{{ service.Title }}</h3>
  </RouterLink>
  <div>
    Date:
    <span v-if="modify">
      <input v-model="modifiedLesson.Date" type="date" :min="today" required />
    </span>
    <span v-else>{{ this.parseDate(this.lesson.Datetime) }}</span>
  </div>
  <div>
    Time:
    <span v-if="modify">
      <input v-model="modifiedLesson.Time" type="time" required />
    </span>
    <span v-else>{{ this.parseTime(this.lesson.Datetime) }}</span>
  </div>
  <div>
    Duration:
    <span v-if="modify">
      <select v-model="modifiedLesson.Duration">
        <option v-for="i in 17" :value="i * 15">
          <span v-if="i <= 4">{{ i * 15 }} minutes</span>
          <span v-else>{{ i / 4 - (i % 4) * 0.25 }} hours {{ (i % 4) * 15 }} minutes </span>
        </option>
      </select>
    </span>
    <span v-else>{{ this.lesson.Duration }} minutes</span>
  </div>
  <template v-if="statusPending">
    <div>Status: pending confirmation</div>
  </template>

  <template v-if="statusPending && !sender && !modify">
    <button class="accept-button" @click="modifyLessonStatus('accepted')">Confirm</button>
  </template>

  <template v-if="statusPending && !modify">
    <button class="modify-button" @click="modify = true">Modify</button>
  </template>
  <template v-else-if="statusPending && modify">
    <button class="accept-button" @click="modifyLesson()">Confirm</button>
  </template>

  <template v-if="!modify">
    <button class="cancel-button" @click="modifyLessonStatus('cancelled')">Cancel</button>
  </template>
  <template v-else>
    <button class="cancel-button" @click="modify = false">Cancel</button>
  </template>
</template>

<script>
import dayjs from "dayjs";

export default {
  props: {
    lesson: Object,
    service: Object,
    sender: Boolean,
  },
  data() {
    return {
      today: new Date().toISOString().split("T")[0],
      modify: false,
      modifiedLesson: Object.assign({}, this.lesson),
    };
  },
  created() {
    this.modifiedLesson.Date = this.parseDate(this.lesson.Datetime);
    this.modifiedLesson.Time = dayjs(this.lesson.Datetime).format("HH:mm");
  },
  methods: {
    parseDate(datetime) {
      if (datetime) {
        return dayjs(datetime).format("YYYY-MM-DD");
      }
    },
    parseTime(datetime) {
      if (datetime) {
        return dayjs(datetime).format("hh:mm A");
      }
    },
    modifyLesson() {
      this.$emit("modify-lesson", this.modifiedLesson);
      this.modify = false;
    },
    modifyLessonStatus(status) {
      this.modifiedLesson.Status = status;
      this.$emit("modify-lesson", this.modifiedLesson);
    },
  },
  computed: {
    statusPending() {
      if (this.lesson.Status.startsWith("accepted_")) {
        return true;
      }
      return false;
    },
  },
};
</script>

<style lang="scss" scoped>
button {
  font-size: medium;
  margin: 10px 2px auto;
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
