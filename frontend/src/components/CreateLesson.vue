<template>
  <div id="user-service-creation">
    <form enctype="multipart/form-data" @submit.prevent="createLesson">
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
              <textarea rows="1" cols="120" name="title" required></textarea>
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
              <textarea rows="7" cols="120" name="description" required></textarea>
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
              <select name="category" required>
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
        <button type="submit">Create service</button>
      </div>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {};
  },
  methods: {
    createLesson(event) {
      const data = new FormData(event.target);
      fetch("/api/services", {
        method: "POST",
        body: data,
      }).catch((error) => {
        console.error("Error fetching data:", error);
      });
    },
  },
};
</script>

<style lang="scss">
@import "@/assets/styles/mixins.scss";

#user-service-creation {
  border: 1px dashed var(--green0);
  padding: 25px;
  margin: 20px;
  box-sizing: border-box;

  table {
    width: 100%;
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
  #service-creation-table > tbody > tr > td {
    padding-bottom: 30px;

    textarea {
      font-size: large;
    }
    &:first-child {
      vertical-align: top;
      padding-right: 10px;
      min-width: 140px;
      font-weight: bold;
    }
  }
}
</style>
