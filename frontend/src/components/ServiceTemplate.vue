<template>
  <div id="service-creation">
    <form enctype="multipart/form-data" @submit.prevent="createOrEditService">
      <table id="service-creation-table">
        <tbody>
          <tr>
            <td>
              <label for="title">
                <i class="fa-solid fa-asterisk fa-2xs error-text" />
                Title:
              </label>
            </td>
            <td>
              <input type="text" v-model="service.title" name="title" required></input>
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
              <textarea v-model="service.description" rows="7" cols="120" name="description" required></textarea>
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
              <input type="file" name="images" accept="image/png, image/jpeg" multiple />
            </td>
          </tr>
        </tbody>
      </table>
      <div class="button-container">
        <button v-if="id == -1" type="submit">Create service</button>
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
      console.log(this.$route);
      if (this.$route.params.id) {
        fetch(`/api/services/${this.$route.params.id}`)
          .then((response) => response.json())
          .then(
            (data) => (
              (this.service.id = data.ID),
              (this.service.title = data.Title),
              (this.service.description = data.Description),
              (this.service.category = data.Category)
            )
          );
      }
    },
    createService() {
      fetch("/api/services", {
        method: "POST",
        body: JSON.stringify({
          title: this.service.title,
          description: this.service.description,
          category: this.service.category,
        }),
      });
    },
    editService() {
      fetch(`/api/services/${this.service.id}`, {
        method: "PUT",
        body: JSON.stringify({
          title: this.service.title,
          description: this.service.description,
          category: this.service.category,
        }),
      });
    },
    createOrEditService() {
      if (this.service.id == -1) {
        this.createService();
      } else {
        this.editService();
      }
      this.$router.push({ path: "/user/services", query: { status: "active" } });
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
  textarea, input {
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
  #service-creation-table > tbody > tr > td {
    padding-bottom: 30px;

    &:first-child {
      vertical-align: top;
      padding-right: 10px;
      min-width: 140px;
      font-weight: bold;
    }
  }
}
</style>
