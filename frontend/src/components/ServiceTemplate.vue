<template>
  <div id="service-creation">
    <form @submit.prevent="createOrEditService" enctype="multipart/form-data">
      <table id="service-creation-table">
        <tbody>
          <tr>
            <td>
              <label for="title">
                <i class="fa-solid fa-asterisk fa-2xs error-text" />
                Title:
              </label>
            </td>
            <td class="flex-container">
              <input type="text" v-model="service.title" name="title" required />
              <div class="centered cancel-button">
                <i @click="$router.back()" class="fa-regular fa-rectangle-xmark fa-2xl"></i>
              </div>
            </td>
          </tr>
          <tr>
            <td>
              <label for="description">
                <i class="fa-solid fa-asterisk fa-2xs error-text"></i>
                Description:
              </label>
            </td>
            <td>
              <textarea v-model="service.description" rows="7" name="description" required></textarea>
            </td>
          </tr>
          <tr>
            <td>
              <label for="category">
                <i class="fa-solid fa-asterisk fa-2xs error-text"></i>
                Category:
              </label>
            </td>
            <td>
              <select v-model="service.category" name="category" required>
                <option value="" disabled selected>Select a category</option>
                <option value="language">Language learning</option>
                <option value="software">Software development</option>
                <option value="music">Music lessons</option>
                <option value="wellness">Wellness (i.e. meditation, yoga)</option>
                <option value="other">Other</option>
              </select>
            </td>
          </tr>
          <tr>
            <td>Upload images:</td>
            <td>
              <input type="file" name="image" accept="image/png, image/jpeg" />
            </td>
          </tr>
        </tbody>
      </table>
      <div class="button-container">
        <button v-if="service.id == -1" type="submit">Create service</button>
        <button v-else type="submit">Update service</button>
      </div>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      service: {
        id: -1,
        title: "",
        description: "",
        category: "",
      },
    };
  },
  mounted() {
    this.getService();
  },
  methods: {
    getService() {
      if (this.$route.params.id) {
        fetch(`/api/services/${this.$route.params.id}`)
          .then((response) => response.json())
          .then((data) => {
            this.service.id = data.ID;
            this.service.title = data.Title;
            this.service.description = data.Description;
            this.service.category = data.Category;
          });
      }
    },
    createService(form) {
      fetch("/api/services", {
        method: "POST",
        body: form,
      }).then(() => {
        this.$router.push({ path: "/user/services", query: { status: "active" } });
      });
    },
    editService(form) {
      fetch(`/api/services/${this.service.id}`, {
        method: "PUT",
        body: form,
      }).then(() => {
        this.$router.push({ path: "/user/services", query: { status: "active" } });
      });
    },
    createOrEditService() {
      const form = new FormData(event.target);
      if (this.service.id == -1) {
        this.createService(form);
      } else {
        this.editService(form);
      }
    },
  },
};
</script>

<style lang="scss">
@import "@/assets/styles/mixins.scss";

#service-creation {
  border: 1px dashed var(--green0);
  padding: 25px;
  margin: 20px;
  box-sizing: border-box;

  table {
    width: 100%;
  }
  input {
    padding: 3px;
    width: 350px;
    font-size: 15px;
  }
  textarea {
    width: 100%;
    box-sizing: border-box;
  }
  select {
    padding: 5px;
    min-width: 200px;
  }
  button {
    @include common-button;
    max-width: 250px;
    background-color: var(--green1);
  }
  .button-container {
    display: flex;
    justify-content: center;
    margin-top: 15px;
  }
  .cancel-button {
    cursor: pointer;
    color: var(--red);
    margin-left: auto;
  }
  #service-creation-table > tbody > tr > td {
    padding-bottom: 30px;

    &:first-child {
      vertical-align: top;
      padding-right: 10px;
      width: 140px;
      font-weight: bold;
    }
  }
}
</style>
