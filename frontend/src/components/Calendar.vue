<template>
  <div>
    <div class="calendar-control">
      <button v-show="index > 0" @click="decrementMonth">
        <i class="fa-solid fa-chevron-left fa-xl"></i>
      </button>
      <span class="calendar-control-date">{{ current_month.month_name }}</span>
      <button v-show="index < 23" @click="incrementMonth">
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
        <div class="day" :class="{ 'day-today': index == 12 && i == today.getDate() }">
          {{ i }}
        </div>
      </template>
    </div>
  </div>
</template>

<script>
var months = [];

for (let i = -12; i < 12; i++) {
  let date = new Date();
  date.setMonth(date.getMonth() + i);

  let month = date.getMonth();
  let year = date.getFullYear();
  months.push({
    days: new Date(year, month + 1, 0).getDate(),
    month: month,
    year: year,
    offset: new Date(year, month, 1).getDay(),
    month_name: new Intl.DateTimeFormat("en-US", { month: "long" }).format(date),
  });
}

export default {
  data() {
    return {
      index: 12,
      today: null,
      current_month: {},
    };
  },
  mounted() {
    this.current_month = months[this.index];
    this.today = new Date();
  },
  methods: {
    incrementMonth() {
      this.index += 1;
      this.current_month = months[this.index];
    },
    decrementMonth() {
      this.index -= 1;
      this.current_month = months[this.index];
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
