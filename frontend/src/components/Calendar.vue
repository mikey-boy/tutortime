<template>
  <div>
    <div class="calendar-control">
      <button @click="decrementMonth">
        <i class="fa-solid fa-chevron-left fa-xl"></i>
      </button>
      <span class="calendar-control-date">{{ current_month.month }}</span>
      <button @click="incrementMonth">
        <i class="fa-solid fa-chevron-right fa-xl"></i>
      </button>
      <span class="calendar-control-date">{{ current_month.year }}</span>
      <span class="calendar-control-legend">
        <span class="calendar-control-legend-tutor"><i class="fa-solid fa-square"></i> - Tutor</span>
        <span class="calendar-control-legend-student"><i class="fa-solid fa-square"></i> - Student</span>
      </span>
    </div>
    <div class="calendar">
      <span class="day-name">Sun</span>
      <span class="day-name">Mon</span>
      <span class="day-name">Tue</span>
      <span class="day-name">Wed</span>
      <span class="day-name">Thu</span>
      <span class="day-name">Fri</span>
      <span class="day-name">Sat</span>
      <template v-for="i in current_month.offset">
        <div class="day"></div>
      </template>
      <template v-for="i in current_month.days">
        <div class="day" :class="{ 'day-today': i == current_month.today }">
          {{ i }}
          <div v-for="lesson in lessonsToday(i)" class="relative-container">
            <button
              class="calendar-lesson"
              :class="lessonType(lesson)"
              @click="display_modal == lesson.ID ? (display_modal = -1) : (display_modal = lesson.ID)"
            >
              <b>{{ parseTime(lesson.Datetime) }}</b>
              <br />
              <template v-if="lesson.Status.startsWith('accepted_')">{{ lesson.Service.Title }} (pending)</template>
              <template v-else>{{ lesson.Service.Title }}</template>
            </button>
            <span class="lesson-modal" :class="modalPosition(i)" v-show="display_modal == lesson.ID">
              <button class="cancel-circle-button" @click="display_modal = -1">
                <i class="fa-solid fa-xmark fa-lg"></i>
              </button>
              <RouterLink :to="{ path: `/services/${lesson.Service.ID}` }">
                <h3 class="truncated-text">{{ lesson.Service.Title }}</h3>
              </RouterLink>
              <p>Time: {{ parseTime(lesson.Datetime) }}</p>
              <p>Duration: {{ lesson.Duration }} minutes</p>
              <p class="truncated-text">Description: {{ lesson.Service.Description }}</p>
            </span>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import dayjs from "dayjs";
import { store } from "@/utils/store";

export default {
  data() {
    return {
      lessons: [],
      months: {},
      current: dayjs(),
      current_month: {},
      display_modal: -1,
    };
  },
  created() {
    this.getLessons();
  },
  methods: {
    async getLessons() {
      const response = await fetch(`/api/users/me/lessons`);
      this.lessons = await response.json();
      this.fetchCurrentMonth();
      this.current_month.today = dayjs().date();
    },
    fetchCurrentMonth() {
      let key = this.current.format("YYYY-MM");
      if (!(key in this.months)) {
        this.months[key] = {
          days: this.current.daysInMonth(),
          month: this.current.format("MMMM"),
          year: this.current.format("YYYY"),
          offset: this.current.startOf("month").day(),
          lessons: this.lessons.filter((lesson) => lesson.Datetime.startsWith(key)),
        };
      }
      this.current_month = this.months[key];
    },
    incrementMonth() {
      this.current = this.current.add(1, "month");
      this.fetchCurrentMonth();
    },
    decrementMonth() {
      this.current = this.current.subtract(1, "month");
      this.fetchCurrentMonth();
    },
    parseTime(datetime) {
      if (datetime) {
        return dayjs(datetime).format("hh:mm A");
      }
    },
    lessonsToday(i) {
      return this.current_month.lessons.filter((lesson) => Number(lesson.Datetime.slice(8, 10)) == i);
    },
    lessonType(lesson) {
      if (lesson.Status.startsWith("accepted_")) {
        return "pending";
      } else if (lesson.TutorID == store.UserID) {
        return "tutor";
      }
      return "student";
    },
    modalPosition(i) {
      var modal_class;
      if ((this.current_month.offset + i - 1) % 7 <= 3) {
        modal_class = "open-right";
      } else {
        modal_class = "open-left";
      }

      if (this.current_month.offset + i <= 21) {
        modal_class = `${modal_class} open-down`;
      } else {
        modal_class = `${modal_class} open-up`;
      }
      return modal_class;
    },
  },
};
</script>

<style lang="scss">
.calendar-control {
  font-weight: bolder;
  font-size: 20px;
  margin: 20px;

  button {
    background: none;
    color: var(--green0);
  }
  &-date {
    display: inline-block;
    text-align: center;
    width: 110px;
  }
  &-legend {
    float: right;

    &-tutor {
      color: var(--orange);
      margin: 15px;
    }
    &-student {
      color: var(--blue0);
    }
  }
}
.calendar {
  display: grid;
  width: 100%;
  grid-template-columns: repeat(7, 1fr);
  grid-template-rows: 50px;
  grid-auto-rows: minmax(120px, auto);
  overflow: auto;
}
.calendar-lesson {
  display: block;
  width: 100%;
  text-decoration: none;
  text-align: left;
  border: 2px solid;
  border-radius: 3px;
  margin: 5px 0px;
  padding: 2px 10px;
  font-size: 14px;
  background: var(--base3);

  &.pending {
    color: var(--base2);
  }
  &.tutor {
    color: var(--orange);
  }
  &.student {
    color: var(--blue0);
  }
}
.lesson-modal {
  position: absolute;
  z-index: 100;
  padding-left: 10px;
  width: 250px;
  background-color: var(--base0);
  border: 2px solid var(--green0);
  border-radius: 3px;

  > h3 {
    margin: 15px 0px;
  }
  > p {
    margin: 0px 0px 10px;
  }
  > button {
    float: right;
    background-color: var(--base0);
    color: var(--base2);
    margin: 15px 8px;
  }
  &.open-left {
    right: 105%;
  }
  &.open-right {
    left: 105%;
  }
  &.open-down {
    top: 10%;
  }
  &.open-up {
    bottom: 10%;
  }
}
.day {
  padding: 10px;
  border-bottom: 1px solid var(--base2);
  border-right: 1px solid var(--base2);

  &:nth-of-type(n + 1):nth-of-type(-n + 7) {
    grid-row: 2;
  }
  &:nth-of-type(n + 8):nth-of-type(-n + 14) {
    grid-row: 3;
  }
  &:nth-of-type(n + 15):nth-of-type(-n + 21) {
    grid-row: 4;
  }
  &:nth-of-type(n + 22):nth-of-type(-n + 28) {
    grid-row: 5;
  }
  &:nth-of-type(n + 29):nth-of-type(-n + 35) {
    grid-row: 6;
  }
  &:nth-of-type(7n + 1) {
    grid-column: 1 / 1;
    border-left: 1px solid var(--base2);
  }
  &:nth-of-type(7n + 2) {
    grid-column: 2 / 2;
  }
  &:nth-of-type(7n + 3) {
    grid-column: 3 / 3;
  }
  &:nth-of-type(7n + 4) {
    grid-column: 4 / 4;
  }
  &:nth-of-type(7n + 5) {
    grid-column: 5 / 5;
  }
  &:nth-of-type(7n + 6) {
    grid-column: 6 / 6;
  }
  &:nth-of-type(7n + 7) {
    grid-column: 7 / 7;
  }
  &-name {
    font-size: 12px;
    text-transform: uppercase;
    text-align: center;
    line-height: 50px;
    font-weight: 500;
    border-bottom: 1px solid var(--base2);
    border-top: 1px solid var(--base2);

    &:nth-of-type(7n + 7) {
      border-right: 1px solid var(--base2);
    }
    &:nth-of-type(7n + 1) {
      border-left: 1px solid var(--base2);
    }
  }
  &-today {
    background-color: var(--green0);
  }
}
</style>
