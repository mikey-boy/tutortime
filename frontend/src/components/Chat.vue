<template>
  <div id="chat-container">
    <div id="contacts">
      <h2>Contacts</h2>
      <ul v-for="contact in contacts">
        <li :class="{ active: contact.ID === activeContact.ID }" @click="changeContact(contact.ID)">
          <span>{{ contact.Username }}</span>
        </li>
      </ul>
    </div>
    <div id="chat">
      <h2 v-if="contacts.length > 0">{{ activeContact.Username }}</h2>
      <div id="message-container">
        <div
          v-for="message in messages"
          :class="{
            'flex-container-user': message.RecieverID == activeContact.ID,
            'flex-container-peer': message.RecieverID != activeContact.ID,
          }"
        >
          <span v-if="message.Lesson" class="message-item lesson">
            <Lesson :lesson="message.Lesson" :service="findService(message.Lesson)" />
          </span>
          <span v-else class="message-item">{{ message.Message }}</span>
        </div>
        <div v-if="lessonRequest.Title" id="chat-lesson-request">
          <form @submit.prevent="sendLessonRequest()">
            <div class="flex-container">
              <h3 id="service-title">{{ lessonRequest.Title }}</h3>
              <i id="cancel-request-button" @click="resetLessonRequest" class="fa-regular fa-circle-xmark fa-lg"></i>
            </div>
            <label>Datetime: </label>
            <input v-model="lessonRequest.Date" type="date" required :min="today" />
            <input v-model="lessonRequest.Time" type="time" required />
            <label>Duration: </label>
            <select v-model="lessonRequest.Duration">
              <option v-for="i in 17" :value="i * 15">
                <span v-if="i <= 4">{{ i * 15 }} minutes</span>
                <span v-else>{{ i / 4 - (i % 4) * 0.25 }} hours {{ (i % 4) * 15 }} minutes </span>
              </option>
            </select>
            <button id="send-request-button">Send</button>
            <button id="modify-request-button">Modify</button>
            <p id="lesson-request-error"></p>
          </form>
        </div>
      </div>
      <div id="chat-input">
        <input
          id="message"
          type="text"
          v-model="text"
          placeholder="Type your message..."
          @keydown.enter="sendMessage()"
        />
        <button id="send-message-button" @click="sendMessage()">Send</button>
      </div>
    </div>
    <div id="lessons">
      <h2>Lessons</h2>
      <div class="flex-container subnav" v-show="lessonView">
        <button :class="{ active: completed }" @click="completed = true">Scheduled</button>
        <button :class="{ active: !completed }" @click="completed = false">Completed</button>
      </div>
      <div v-if="lessonView" class="lesson-container">
        <div class="lesson" v-for="lesson in lessons" v-show="completed">
          <Lesson :lesson="lesson" :service="findService(lesson)" />
        </div>
      </div>
      <div v-else>
        <div class="lesson-container without-subnav">
          <h3>As a student:</h3>
          <template v-for="service in services">
            <div v-if="service.UserID != activeContact.ID">
              <label class="lesson-request-item" @click="newLessonRequest(service)">
                <input type="radio" name="service" id="service-{{ service.id }}" /> {{ service.Title }}
              </label>
            </div>
          </template>
          <h3>As a tutor:</h3>
          <template v-for="service in services">
            <div v-if="service.UserID == activeContact.ID">
              <label class="lesson-request-item" @click="newLessonRequest(service)">
                <input type="radio" name="service" id="service-{{ service.id }}" /> {{ service.Title }}
              </label>
            </div>
          </template>
        </div>
      </div>

      <button v-show="lessonView" class="lesson-view-switch request-lessons" @click="lessonView = !lessonView">
        <i class="fa-solid fa-handshake fa-lg"></i> Send lesson request
      </button>
      <button v-show="!lessonView" class="lesson-view-switch view-lessons" @click="lessonView = !lessonView">
        <i class="fa-regular fa-calendar-days fa-lg"></i> View lessons
      </button>
    </div>
  </div>
</template>

<script>
import Lesson from "./Lesson.vue";
import { nextTick } from "vue";

const socket = new WebSocket("ws://localhost:8080/ws");

export default {
  data() {
    return {
      text: "",
      activeContact: null,
      contacts: [],
      lessons: [],
      messages: [],
      services: [],
      lessonView: true,
      completed: true,
      lessonRequest: {
        LessonID: 0,
        ServiceID: 0,
        Title: "",
        Date: null,
        Time: null,
        Duration: 0,
      },
      today: new Date().toISOString().split("T")[0],
    };
  },
  created() {
    this.initChat();
    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.messages.push(message);
      this.scrollToBottom();
    };
  },
  components: {
    Lesson,
  },
  methods: {
    async initChat() {
      const contactID = Number(this.$route.query.user);
      const response = await fetch("/api/contacts");
      this.contacts = await response.json();

      const contact = this.contacts.find((contact) => contact.ID === contactID);
      if (contact) {
        this.activeContact = contact;
      } else if (contactID) {
        const response2 = await fetch(`/api/users/${contactID}`);
        this.contacts.unshift(await response2.json());
        this.activeContact = this.contacts[0];
      } else if (this.contacts.length > 0) {
        this.activeContact = this.contacts[0];
      } else {
        return;
      }

      await this.getServices(this.activeContact.ID);
      this.getLessons(this.activeContact.ID);
      this.getMessages();
    },
    async getServices(userID) {
      let myServicesUrl = "/api/users/me/services";
      let yourServicesUrl = `/api/users/${userID}/services`;

      const myServices = await fetch(myServicesUrl);
      const yourServices = await fetch(yourServicesUrl);

      let a1 = await myServices.json();
      let a2 = await yourServices.json();
      this.services = [].concat(a1, a2);
    },
    async getLessons(userID) {
      const response = await fetch(`/api/users/${userID}/lessons`);
      this.lessons = await response.json();
    },
    async getMessages() {
      const response = await fetch(`/api/users/${this.activeContact.ID}/messages`);
      this.messages = await response.json();
      this.scrollToBottom();
    },
    async scrollToBottom() {
      await nextTick();
      let messageContainer = document.getElementById("message-container");
      messageContainer.scrollTop = messageContainer.scrollHeight;
    },

    changeContact(userID) {
      this.$router.push({ path: "/chat/", query: { user: userID } });
      this.activeContact = this.contacts.find((contact) => contact.ID === userID);
      this.getServices(userID);
      this.getLessons(userID);
      this.getMessages();
    },
    sendMessage() {
      let message = { Message: this.text, RecieverID: this.activeContact.ID };
      socket.send(JSON.stringify(message));
      this.text = "";
    },
    sendLessonRequest() {
      let message = { Message: "", RecieverID: this.activeContact.ID, Lesson: this.lessonRequest };
      socket.send(JSON.stringify(message));
      this.resetLessonRequest();
    },
    findService(lesson) {
      return this.services.find((service) => service.ID == lesson.ServiceID);
    },
    newLessonRequest(service) {
      this.lessonRequest.Title = service.Title;
      this.lessonRequest.ServiceID = service.ID;
      this.scrollToBottom();
    },
    modifyLessonRequest(lesson) {},
    resetLessonRequest() {
      this.lessonRequest.Title = "";
      this.lessonRequest.LessonID = 0;
      this.lessonRequest.ServiceID = 0;
      this.lessonRequest.Duration = 0;
      this.lessonRequest.Date = null;
      this.lessonRequest.Time = null;

      let radios = document.getElementsByName("service");
      for (let i = 0; i < radios.length; i++) {
        radios[i].checked = false;
      }
    },
  },
};
</script>

<style lang="scss">
#chat-container {
  display: flex;
  margin: 0 auto;
  padding: 20px;
}
#contacts {
  flex: 1;

  h2 {
    margin-bottom: 10px;
  }
  ul {
    list-style: none;
    padding: 0;
  }
  li {
    cursor: pointer;
    color: var(--text0);
    text-align: center;
    border-radius: 3px;
    padding: 5px;
    margin-bottom: 5px;
    &:hover {
      background-color: var(--base1);
    }
  }
  li.active {
    background-color: var(--base1);
  }
  li span.new-messages {
    color: var(--green0);
  }
}
#chat {
  flex: 5;
  border-radius: 5px;
  border: 2px solid var(--green0);
  background-color: var(--base1);
  padding: 0px 40px;
  margin: 0px 10px;

  #chat-input {
    display: flex;
    margin: 20px 0px;

    input {
      flex: 1;
      padding: 7px 10px;
      border: none;
      border-radius: 3px;
      margin-right: 10px;
    }
    #send-message-button {
      color: var(--text1);
      padding: 7px 25px;
      background-color: var(--green1);
    }
  }
  #message-container {
    height: 527px;
    min-width: 330px;
    overflow-y: scroll;
    padding: 0px 10px;

    &.minimized {
      height: 388px;
    }
    .flex-container-user {
      display: flex;
      justify-content: right;
      color: var(--blue0);
    }
    .flex-container-peer {
      display: flex;
      justify-content: left;
      color: var(--orange);
    }
    .flex-container-system {
      display: flex;
      justify-content: center;
      font-size: medium;
      margin: 5px 0px;
      color: var(--text0);
    }
    .message-item {
      border: 2px solid;
      border-radius: 3px;
      margin-bottom: 7px;
      padding: 5px 10px;
      background: var(--base3);
    }
    .message-item-system {
      margin: 5px 0px;
    }
    .lesson {
      h3 {
        margin: 0px;
      }
    }
  }
  #chat-lesson-request {
    display: flex;
    justify-content: right;

    h3 {
      margin-top: 0px;
      justify-content: left;
    }
    > form {
      padding: 8px;
      background-color: var(--base1);
      border: 1px dashed var(--green0);
      border-radius: 3px;
      width: 330px;

      select,
      input {
        padding: 4px;
        margin-bottom: 10px;
      }
    }
    .truncated-text {
      -webkit-line-clamp: 1;
    }
    .flex-container {
      display: flex;
      justify-content: space-between;
    }
    #send-request-button {
      background-color: var(--blue0);
      color: var(--text1);
      padding: 6px 27px;
    }
    #modify-request-button {
      background-color: var(--orange);
      color: var(--text1);
      padding: 6px 21px;
    }
    #cancel-request-button {
      background-color: var(--base1);
      color: var(--base2);
      margin-top: 10px;
      cursor: pointer;
    }
    #lesson-request-error {
      margin: 0px;
      color: var(--red);
      font-weight: bold;
    }
  }
}
#lessons {
  flex: 2;
  margin: 0px 20px;
  height: 670px;

  h2 {
    margin-bottom: 0px;
  }
  .subnav {
    margin: 10px 0px;

    button {
      flex: 1;
      font-size: medium;
      padding: 5px 10px;
      background-color: var(--base0);
      color: var(--text0);
      width: 100%;

      &.active {
        border: 1px solid var(--green0);
      }
    }
  }
  .lesson-container {
    min-width: 180px;
    height: 521px;
    overflow-y: scroll;

    .lesson {
      background-color: var(--base1);
      padding: 10px;
      margin-bottom: 10px;
      h3 {
        margin: 0px;
      }
      p {
        margin-bottom: 0px;
      }
    }
  }
  .lesson-container.without-subnav {
    height: 575px;
  }
  .lesson-request-item {
    display: block;
    margin-bottom: 10px;
    border: 1px dashed var(--green0);
    border-radius: 3px;
    padding: 13px;
    cursor: pointer;
  }
  .warning {
    border: 1px solid var(--red);
  }
  .lesson-empty-item {
    border: 1px dashed var(--green0);
    background-color: var(--base1);
    padding: 20px;
  }
  .warning-text {
    color: var(--orange);
    font-weight: bolder;
  }
  .lesson-view-switch {
    padding: 8px;
    margin-top: 15px;
    width: 100%;
    color: var(--text1);

    &.view-lessons {
      background-color: var(--orange);
    }
    &.request-lessons {
      background-color: var(--blue0);
    }
  }
}
</style>
