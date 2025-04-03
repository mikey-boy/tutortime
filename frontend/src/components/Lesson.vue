<template>
  <RouterLink :to="{ path: `/services/${service.ID}` }">
    <h3>{{ service.Title }}</h3>
  </RouterLink>
  <div>
    Date:
    <span v-if="modify && !lessonCompleted">
      <input v-model="modifiedLesson.Date" type="date" :min="today" required />
    </span>
    <span v-else>{{ parseDate(lesson.Datetime) }}</span>
  </div>
  <div>
    Time:
    <span v-if="modify && !lessonCompleted">
      <input v-model="modifiedLesson.Time" type="time" required />
    </span>
    <span v-else>{{ parseTime(lesson.Datetime) }}</span>
  </div>
  <div>
    <span v-if="lesson.ModifiedDuration && lesson.Status != 'confirmed'">
      <div>Scheduled for: {{ lesson.Duration }} minutes</div>
      <span class="warning-text">Modified to: </span>
      <span class="warning-text" v-if="!modify">{{ lesson.ModifiedDuration }} minutes</span>
    </span>
    <span v-else-if="lesson.ModifiedDuration && lesson.Status == 'confirmed'">
      <span>Duration: {{ lesson.ModifiedDuration }} minutes</span>
    </span>
    <span v-else>
      <span>Duration: </span>
      <span v-if="!modify">{{ lesson.Duration }} minutes</span>
    </span>

    <span v-if="modify">
      <select v-if="pendingConfirmation" v-model="modifiedLesson.ModifiedDuration">
        <option v-for="(n, i) in 17" :value="i * 15">
          <span v-if="i <= 4">{{ i * 15 }} minutes</span>
          <span v-else>{{ i / 4 - (i % 4) * 0.25 }} hours {{ (i % 4) * 15 }} minutes </span>
        </option>
      </select>
      <select v-else v-model="modifiedLesson.Duration">
        <option v-for="i in 17" :value="i * 15">
          <span v-if="i <= 4">{{ i * 15 }} minutes</span>
          <span v-else>{{ i / 4 - (i % 4) * 0.25 }} hours {{ (i % 4) * 15 }} minutes </span>
        </option>
      </select>
    </span>
  </div>
  <template v-if="lessonCompleted && lesson.Status != 'confirmed'">
    <div>Status: pending confirmation</div>
  </template>
  <template v-else-if="pendingAcceptance">
    <div>Status: pending acceptance</div>
  </template>
  <template v-else>
    <div>Status: {{ lesson.Status }}</div>
  </template>

  <template v-if="pendingAcceptance && !sender && !modify">
    <button class="confirm-button" @click="modifyLesson('confirmed')">Confirm</button>
  </template>
  <template v-if="pendingConfirmation && !modify">
    <button class="confirm-button" @click="modifyLesson('confirmed')">Confirm</button>
  </template>
  <template v-if="modify">
    <button class="confirm-button" @click="modifyLesson('modified')">Confirm</button>
  </template>
  <template v-if="(pendingAcceptance || pendingConfirmation) && !modify">
    <button class="modify-button" @click="modify = true">Modify</button>
  </template>
  <template v-if="!modify && !lessonCompleted">
    <button class="cancel-button" @click="modifyLesson('cancelled')">Cancel</button>
  </template>
  <template v-else-if="modify">
    <button class="cancel-button" @click="modify = false">Cancel</button>
  </template>
</template>

<script>
import dayjs from "dayjs";
import { parseDate, parseTime } from "@/utils/utils";

export default {
  props: {
    lesson: Object,
    service: Object,
    sender: Boolean,
  },
  data() {
    return {
      today: dayjs().format("YYYY-MM-DD"),
      modify: false,
      modifiedLesson: Object.assign({}, this.lesson),
    };
  },
  created() {
    this.modifiedLesson.Date = this.parseDate(this.lesson.Datetime);
    this.modifiedLesson.Time = dayjs(this.lesson.Datetime).format("HH:mm");
  },
  methods: {
    parseDate,
    parseTime,
    modifyLesson(status) {
      this.modifiedLesson.Status = status;
      this.$emit("modify-lesson", this.modifiedLesson);
      this.modify = false;
    },
  },
  computed: {
    pendingAcceptance() {
      return this.lesson.Status.startsWith("accepted_");
    },
    pendingConfirmation() {
      return (
        dayjs().isAfter(dayjs(this.lesson.Datetime)) &&
        (this.lesson.Status == "accepted" || (this.lesson.Status.startsWith("confirmed_") && !this.sender))
      );
    },
    lessonCompleted() {
      return dayjs().isAfter(dayjs(this.lesson.Datetime));
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
.confirm-button {
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
