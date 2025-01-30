<template>
  <div v-if="user.Availability">
    <h2>Account details</h2>
    <div id="user-account-list">
      <form @submit.prevent="updateProfile" enctype="multipart/form-data">
        <div class="label flex-container">
          Profile Picture
          <label for="profile-pic-input" id="profile-pic-label" v-show="modify">
            <i class="fa-solid fa-pen-to-square fa-lg"></i>
          </label>
          <button class="cancel-button" v-show="modify" @click.prevent="modify = false">
            <i class="fa-solid fa-circle-xmark fa-lg"></i>
            Cancel
          </button>
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
                <i class="fa-regular" :class="isChecked(i + '-0') ? 'fa-square-check' : 'fa-square'"></i>
              </td>
            </tr>
            <tr>
              <td>afternoon</td>
              <td v-for="i in 7">
                <i class="fa-regular" :class="isChecked(i + '-1') ? 'fa-square-check' : 'fa-square'"></i>
              </td>
            </tr>
            <tr>
              <td>evening</td>
              <td v-for="i in 7">
                <i class="fa-regular" :class="isChecked(i + '-2') ? 'fa-square-check' : 'fa-square'"></i>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="label">About Me</div>
        <div v-show="modify">
          <textarea type="text" name="description" rows="5" :value="user.Description"></textarea>
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
</template>

<script>
export default {
  data() {
    return {
      user: {},
      lessons: [],
      modify: false,
      imageUrl: "",
    };
  },
  created() {
    this.getProfile();
    this.getLessons();
  },
  methods: {
    async getProfile() {
      const response = await fetch("/api/users/me");
      this.user = await response.json();
      this.user.Availability = this.user.Availability.split(",");
    },
    async getLessons() {
      const response = await fetch("/api/users/me/lessons");
      this.lessons = await response.json();
    },
    async updateProfile() {
      let form = new FormData(event.target);

      let availability = [];
      for (let i = 0; i < 21; i++) {
        let index = `${Math.floor(i / 7)}-${i % 7}`;
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
  },
};
</script>

<style>
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

  button.edit-button,
  button.cancel-button {
    width: 110px;
    margin-left: auto;
    padding: 6px 8px;
    font-weight: bold;
  }
  button.cancel-button {
    color: var(--text1);
    background-color: var(--red);
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
</style>
