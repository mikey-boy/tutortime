<template>
  <div v-if="user.Availability">
    <div id="account-details">
      <h2>Account details</h2>
      <h3>Balance: {{ user.Minutes }} minutes</h3>
    </div>
    <div id="user-account-list" :class="modify ? 'editing' : ''">
      <form @submit.prevent="updateProfile" enctype="multipart/form-data">
        <div class="label flex-container">
          Profile Picture
          <label for="profile-pic-input" id="profile-pic-label" v-show="modify">
            <i class="fa-solid fa-pen-to-square fa-lg"></i>
          </label>
          <div class="cancel-button centered" v-show="modify" @click.prevent="modify = false">
            <i class="fa-solid fa-rectangle-xmark fa-2xl"></i>
          </div>
          <button class="edit-button" v-show="!modify" @click.prevent="modify = true">
            <i class="fa-solid fa-pen-to-square fa-lg"></i>
            Edit profile
          </button>
        </div>

        <input
          name="image"
          accept="image/*"
          style="display: none"
          type="file"
          id="profile-pic-input"
          @change="updateImage"
        />
        <img id="profile-pic" :src="imageUrl ? imageUrl : user.Image.Path" />

        <div class="label">Display Name</div>
        <div v-show="modify">
          <input type="text" name="username" :value="user.Username" />
        </div>
        <div v-show="!modify">
          <p>{{ user.Username }}</p>
        </div>

        <div class="label">Availability</div>
        <table name="availability-table" class="availability-table" v-show="modify">
          <thead>
            <tr>
              <td></td>
              <td>Mon</td>
              <td>Tue</td>
              <td>Wed</td>
              <td>Thu</td>
              <td>Fri</td>
              <td>Sat</td>
              <td>Sun</td>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>morning</td>
              <td v-for="i in 7">
                <input type="checkbox" :name="i + '-0'" :checked="isChecked(i + '-0')" />
              </td>
            </tr>
            <tr>
              <td>afternoon</td>
              <td v-for="i in 7">
                <input type="checkbox" :name="i + '-1'" :checked="isChecked(i + '-1')" />
              </td>
            </tr>
            <tr>
              <td>evening</td>
              <td v-for="i in 7">
                <input type="checkbox" :name="i + '-2'" :checked="isChecked(i + '-2')" />
              </td>
            </tr>
          </tbody>
        </table>
        <table class="availability-table" v-show="!modify">
          <thead>
            <tr>
              <td></td>
              <td>Mon</td>
              <td>Tue</td>
              <td>Wed</td>
              <td>Thu</td>
              <td>Fri</td>
              <td>Sat</td>
              <td>Sun</td>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>morning</td>
              <td v-for="i in 7">
                <i :class="isChecked(i + '-0') ? 'fa-solid fa-square-check' : 'fa-regular fa-square'"></i>
              </td>
            </tr>
            <tr>
              <td>afternoon</td>
              <td v-for="i in 7">
                <i :class="isChecked(i + '-1') ? 'fa-solid fa-square-check' : 'fa-regular fa-square'"></i>
              </td>
            </tr>
            <tr>
              <td>evening</td>
              <td v-for="i in 7">
                <i :class="isChecked(i + '-2') ? 'fa-solid fa-square-check' : 'fa-regular fa-square'"></i>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="label">About Me</div>
        <div v-show="modify">
          <textarea type="text" name="description" rows="3" :value="user.Description"></textarea>
        </div>
        <div v-show="!modify">
          <p v-if="user.Description">{{ user.Description }}</p>
          <p v-else><i>No description provided</i></p>
        </div>

        <div class="flex-container" style="justify-content: center" v-show="modify">
          <button class="submit-button">Update account</button>
        </div>
      </form>
    </div>
  </div>

  <div id="completed-lessons">
    <h2>Completed lessons</h2>
    <div v-if="lessons.length > 10" id="page-control">
      <button @click="prevPage">
        <i class="fa-solid fa-chevron-left fa-xl"></i>
      </button>
      <span>Page {{ page }}</span>
      <button @click="nextPage">
        <i class="fa-solid fa-chevron-right fa-xl"></i>
      </button>
    </div>
  </div>

  <div v-if="lessons.length > 0">
    <table class="standard-table">
      <thead>
        <tr>
          <td>Date</td>
          <td>Time</td>
          <td>Lesson title</td>
          <td>Tutor</td>
          <td>Student</td>
          <td>Minutes</td>
          <td>Balance</td>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(lesson, index) in lessons" :key="lesson.ID">
          <template v-if="0 <= index - (page - 1) * 10">
            <td>{{ parseDate(lesson.Datetime) }}</td>
            <td>{{ parseTime(lesson.Datetime) }}</td>
            <td>{{ lesson.Service.Title }}</td>
            <td>{{ lesson.Tutor.Username }}</td>
            <td>{{ lesson.Student.Username }}</td>
            <td v-if="lesson.TutorID == store.UserID" class="tutor-transaction">+{{ lesson.Duration }}</td>
            <td v-else class="student-transaction">-{{ lesson.Duration }}</td>
            <td>{{ getBalance(index) }}</td>
          </template>
        </tr>
        <tr>
          <td></td>
          <td></td>
          <td></td>
          <td></td>
          <td></td>
          <td></td>
          <td>{{ getBalance(lessons.length) }}</td>
        </tr>

        <tr></tr>
      </tbody>
    </table>
  </div>
  <div v-else>
    <div class="empty-container empty-service">
      <div><p>You haven't completed any lessons yet</p></div>
      <RouterLink to="/">
        <button>Browse lessons</button>
      </RouterLink>
    </div>
  </div>

  <h2>Service history</h2>
  <div v-if="services.length > 0">
    <table class="standard-table">
      <thead>
        <tr>
          <td>Service</td>
          <td>Description</td>
          <td>Lessons taught</td>
          <td>Minutes taught</td>
          <td>Status</td>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(service, index) in services" :key="service.ID">
          <RouterLink :to="{ path: `/services/${service.ID}` }">
            <td>
              <b>{{ service.Title }}</b>
            </td>
          </RouterLink>
          <td>{{ service.Description }}</td>
          <td>{{ service.Lessons }}</td>
          <td>{{ service.Minutes }}</td>
          <td>{{ service.Status }}</td>
        </tr>
      </tbody>
    </table>
  </div>
  <div v-else>
    <div class="empty-container">
      <div><p>You haven't created any services yet</p></div>
      <RouterLink to="/user/services">
        <button>Create a service</button>
      </RouterLink>
    </div>
  </div>
</template>

<script>
import { store } from "@/utils/store";
import { parseDate, parseTime } from "@/utils/utils";

export default {
  data() {
    return {
      store,
      page: 1,
      user: {},
      lessons: [],
      services: [],
      modify: false,
      imageUrl: "",
    };
  },
  mounted() {
    this.getProfile();
    this.getLessons();
    this.getServices();
  },
  methods: {
    parseDate,
    parseTime,
    async getProfile() {
      const response = await fetch("/api/users/me");
      this.user = await response.json();
      this.user.Availability = this.user.Availability.split(",");
    },
    async getLessons() {
      const url = new URL("/api/users/me/lessons", window.location.origin);
      url.search = new URLSearchParams({ status: "confirmed" }).toString();
      const response = await fetch(url);
      let lst = await response.json();
      this.lessons = lst.reverse();
    },
    async getServices() {
      const response = await fetch("/api/users/me/services");
      this.services = await response.json();
    },
    async updateProfile() {
      let form = new FormData(event.target);
      let availability = [];
      for (let i = 0; i < 21; i++) {
        let index = `${(i % 7) + 1}-${Math.floor(i / 7)}`;
        if (form.has(index)) {
          availability.push(index);
          form.delete(index);
        }
      }

      form.set("availability", availability);
      const response = await fetch("/api/users/me", { method: "PUT", body: form });
      this.user = await response.json();
      this.user.Availability = this.user.Availability.split(",");
      this.modify = false;
    },
    updateImage() {
      const file = event.target.files[0];
      this.imageUrl = URL.createObjectURL(file);
    },
    isChecked(value) {
      if (this.user.Availability.includes(value)) {
        return true;
      }
      return false;
    },
    getBalance(index) {
      if (index == 0) {
        this.balance = this.user.Minutes;
      } else {
        if (this.lessons[index - 1].TutorID == store.UserID) {
          this.balance -= this.lessons[index - 1].Duration;
        } else {
          this.balance += this.lessons[index - 1].Duration;
        }
      }
      return this.balance;
    },
    prevPage() {
      if (this.page > 1) {
        this.page--;
      }
    },
    nextPage() {
      if (this.page * 10 < this.lessons.length) {
        this.page++;
      }
    },
  },
};
</script>

<style scoped>
.tutor-transaction {
  color: var(--green1);
}
.student-transaction {
  color: var(--red1);
}
#account-details {
  max-width: 840px;
  display: flex;
  align-items: center;
  h3 {
    margin-left: auto;
    color: var(--text0);
  }
}
#user-account-list {
  max-width: 800px;
  border: 1px dashed var(--green0);
  padding: 20px;

  input {
    padding: 4px;
  }
  textarea {
    width: calc(100% - 8px);
  }

  .edit-button {
    width: 110px;
    margin-left: auto;
    padding: 6px 8px;
    font-weight: bold;
  }
  .cancel-button {
    cursor: pointer;
    margin-left: auto;
    color: var(--red1);
  }
  button.edit-button {
    color: var(--text1);
    background-color: var(--blue0);

    .fa-pen-to-square {
      color: inherit;
      margin-right: 2px;
    }
  }
  button.submit-button {
    width: 250px;
    padding: 10px;
    margin-top: 10px;
    color: var(--text1);
    background-color: var(--green1);
  }
  &.editing {
    border: 1px dashed var(--orange);
  }
  .label {
    font-weight: bold;
    margin: 30px 0px 10px 0px;
  }
  .label:first-child {
    margin-top: 0px;
  }
  #profile-pic {
    width: 75px;
    height: 75px;
    border-radius: 50%;
  }
  #profile-pic-label {
    cursor: pointer;
    margin-left: 10px;
  }
}
#completed-lessons {
  display: flex;
  align-items: center;

  #page-control {
    margin-left: auto;

    button {
      margin: 5px;
      background: none;
      color: var(--green1);
    }
  }
}
</style>
