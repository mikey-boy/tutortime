<template>
  <div v-if="activeRoom == null || activeRoom.Fetched == false" id="chat-container">
    <div id="contacts"><h2>Contacts</h2></div>
    <div id="chat">
      <div id="message-container"></div>
    </div>
    <div id="lessons"><h2>Lessons</h2></div>
  </div>
  <div v-else-if="activeRoom.Fetched && contacts.length == 0">
    <div class="empty-container empty-service">
      <div><p>Check out the lesson offerings and message a tutor to start chatting</p></div>
      <RouterLink to="/">
        <button>Browse lessons</button>
      </RouterLink>
    </div>
  </div>
  <div v-else id="chat-container">
    <div id="contacts">
      <h2>Contacts</h2>
      <ul v-for="contact in contacts">
        <li :class="{ active: contact.ID === activeRoom.User.ID }" @click="changeContact(contact.ID)">
          <span>{{ contact.Username }}</span>
        </li>
      </ul>
    </div>
    <div id="chat">
      <h2>{{ activeRoom.User.Username }}</h2>
      <div id="message-container">
        <template v-for="message in messages">
          <div v-if="message.RecieverID == activeRoom.User.ID" class="flex-container-user">
            <span v-if="message.Lesson && displayInChat(message.Lesson)" class="message-item lesson">
              <Lesson
                @modify-lesson="sendModifiedLesson"
                :lesson="message.Lesson"
                :service="findService(message.Lesson.ServiceID)"
                :sender="message.RecieverID == activeRoom.User.ID"
              />
            </span>
            <span v-else-if="message.Message" class="message-item">
              {{ message.Message }}
            </span>
          </div>
          <div v-else-if="message.RecieverID != 0" class="flex-container-peer">
            <span v-if="message.Lesson && displayInChat(message.Lesson)" class="message-item lesson">
              <Lesson
                @modify-lesson="sendModifiedLesson"
                :lesson="message.Lesson"
                :service="findService(message.Lesson.ServiceID)"
                :sender="message.RecieverID == activeRoom.User.ID"
              />
            </span>
            <span v-else-if="message.Message" class="message-item">
              {{ message.Message }}
            </span>
          </div>
          <div v-else class="flex-container-system">
            <span class="message-item-system">
              {{ parseSystemMessage(message.Message) }}
            </span>
          </div>
        </template>

        <div v-if="lessonRequest.Title" id="chat-lesson-request">
          <form @submit.prevent="sendLessonRequest()">
            <div class="flex-container">
              <h3 id="service-title">{{ lessonRequest.Title }}</h3>
              <div class="centered">
                <i
                  id="cancel-request-button"
                  @click="resetLessonRequest"
                  class="fa-regular fa-rectangle-xmark fa-xl"
                ></i>
              </div>
            </div>
            <label>Datetime: </label>
            <input v-model="lessonRequest.Date" type="date" class="date" required :min="today" />
            <input v-model="lessonRequest.Time" type="time" class="time" required />
            <label>Duration: </label>
            <select v-model="lessonRequest.Duration">
              <option v-for="i in 17" :value="i * 15">
                <span v-if="i <= 4">{{ i * 15 }} minutes</span>
                <span v-else>{{ i / 4 - (i % 4) * 0.25 }} hours {{ (i % 4) * 15 }} minutes </span>
              </option>
            </select>
            <button id="send-request-button">Send</button>
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
          required
        />
        <button id="send-message-button" @click="sendMessage()">Send</button>
      </div>
    </div>
    <div id="lessons">
      <h2>Lessons</h2>
      <div class="flex-container subnav" v-show="lessonView">
        <button :class="{ active: !completedView }" @click="completedView = false">Scheduled</button>
        <button :class="{ active: completedView }" @click="completedView = true">Completed</button>
      </div>
      <div v-if="lessonView" class="lesson-container">
        <template v-for="lesson in lessons">
          <div
            v-if="completedView && lessonCompleted(lesson) && lessonActive(lesson)"
            class="lesson"
            :class="{ warning: lesson.ModifiedDuration && lesson.Status != 'confirmed' }"
          >
            <Lesson
              @modify-lesson="sendModifiedLesson"
              :lesson="lesson"
              :service="findService(lesson.ServiceID)"
              :sender="messages[lesson.MessageID].RecieverID == activeRoom.User.ID"
            />
          </div>
          <div v-else-if="!completedView && !lessonCompleted(lesson) && lessonActive(lesson)" class="lesson">
            <Lesson
              @modify-lesson="sendModifiedLesson"
              :lesson="lesson"
              :service="findService(lesson.ServiceID)"
              :sender="messages[lesson.MessageID].RecieverID == activeRoom.User.ID"
            />
          </div>
        </template>
      </div>
      <div v-else>
        <div class="lesson-container without-subnav">
          <h3>As a student:</h3>
          <template v-for="service in services">
            <div>
              <label class="lesson-request-item" @click="newLessonRequest(service)">
                <input type="radio" name="service" id="service-{{ service.id }}" /> {{ service.Title }}
              </label>
            </div>
          </template>
          <div v-if="Object.keys(services).length == 0" class="empty-item">
            <span>
              <b>{{ activeRoom.User.Username }}</b> is currently not offering any lessons
            </span>
          </div>
          <h3>As a tutor:</h3>
          <template v-for="service in myServices">
            <div>
              <label class="lesson-request-item" @click="newLessonRequest(service)">
                <input type="radio" name="service" id="service-{{ service.id }}" /> {{ service.Title }}
              </label>
            </div>
          </template>
          <div v-if="Object.keys(myServices).length == 0" class="empty-item">
            <span>You are currently not offering any lessons</span>
          </div>
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
import { store } from "@/utils/store";
import { nextTick } from "vue";
import dayjs from "dayjs";

var socket;

export default {
  data() {
    return {
      text: "",
      rooms: {},
      activeRoom: null,
      contacts: [],
      messages: {},
      lessons: {},
      services: {},
      myServices: {},
      lessonView: true,
      completedView: false,
      today: dayjs().format("YYYY-MM-DD"),
      lessonRequest: {
        Date: dayjs().format("YYYY-MM-DD"),
        Time: dayjs().endOf("hour").add(1, "minute").format("HH:mm"),
        Duration: 15,
      },
    };
  },
  created() {
    this.fetchContacts();
    this.getMyServices();
    socket = new WebSocket("ws://localhost:8080/ws");
    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      const roomID = message.RoomID.toString();
      const contactID = Number(this.$route.params.id);

      let mc = document.getElementById("message-container");
      const atBottom = mc.scrollHeight - mc.clientHeight == mc.scrollTop;

      // System message
      if (message.SenderID == 0) {
        this.rooms[roomID].Messages[message.ID] = message;
      }
      // Normal message
      else if (Object.keys(this.rooms).includes(roomID)) {
        this.rooms[roomID].Messages[message.ID] = message;
        if (message.Lesson) {
          this.rooms[roomID].Lessons[message.Lesson.ID] = message.Lesson;
        }
      }
      // I am messaging a new person
      else if (contactID == message.RecieverID) {
        this.rooms[roomID] = this.rooms[0];
        this.rooms[roomID].Messages[message.ID] = message;
        if (message.Lesson) {
          this.rooms[roomID].Lessons[message.Lesson.ID] = message.Lesson;
        }
      }
      // A new person is  messaging me
      else if (store.UserID == message.RecieverID) {
        fetch(`/api/users/${message.SenderID}`)
          .then((response) => response.json())
          .then((contact) => {
            this.rooms[roomID] = {};
            this.rooms[roomID]["User"] = contact;
            this.rooms[roomID]["Lessons"] = {};
            this.rooms[roomID]["Messages"] = {};
            this.contacts.push(contact);
          });
      }

      if (store.UserID == message.SenderID || atBottom) {
        this.scrollToBottom();
      }
    };
  },
  components: {
    Lesson,
  },
  methods: {
    async initChat(userID, roomID) {
      if (Object.keys(this.rooms[roomID]).includes("Fetched") == false) {
        this.rooms[roomID]["Fetched"] = false;
        this.rooms[roomID]["Services"] = {};
        this.rooms[roomID]["Lessons"] = {};
        this.rooms[roomID]["Messages"] = {};
      }

      if (this.rooms[roomID].Fetched == false) {
        this.getServices(userID, roomID);
        this.getLessons(userID, roomID);
        await this.getMessages(userID, roomID);
        this.rooms[roomID].Fetched = true;
      }
      this.activeRoom = this.rooms[roomID];
      this.services = this.activeRoom.Services;
      this.lessons = this.activeRoom.Lessons;
      this.messages = this.activeRoom.Messages;
      this.scrollToBottom();
    },
    async fetchContacts() {
      let found = false;
      const contactID = Number(this.$route.params.id);
      const response = await fetch("/api/rooms");
      const tmp = await response.json();

      tmp.forEach((room) => {
        this.rooms[room.ID] = {};
        if (room.User1ID == store.UserID) {
          this.contacts.push(room.User2);
          this.rooms[room.ID]["User"] = room.User2;
        } else {
          this.contacts.push(room.User1);
          this.rooms[room.ID]["User"] = room.User1;
        }

        if (this.rooms[room.ID].User.ID == contactID) {
          found = true;
          this.initChat(this.rooms[room.ID].User.ID, room.ID);
        }
      });

      if (!found && contactID) {
        const response = await fetch(`/api/users/${contactID}`);
        const contact = await response.json();
        this.rooms[0] = {};
        this.rooms[0]["User"] = contact;
        this.contacts.push(contact);
        this.initChat(contactID, 0);
      } else if (!found && Object.keys(this.rooms).length > 0) {
        const roomID = Object.keys(this.rooms)[0];
        this.initChat(this.rooms[roomID].User.ID, roomID);
      } else if (!found) {
        this.activeRoom = { Fetched: true };
      }
    },
    async getMyServices() {
      const response = await fetch("/api/users/me/services");
      const services = await response.json();
      services.forEach((service) => {
        if (service.Status == "active") {
          this.myServices[service.ID] = service;
        }
      });
    },
    async getServices(userID, roomID) {
      const response = await fetch(`/api/users/${userID}/services`);
      const services = await response.json();
      services.forEach((service) => (this.rooms[roomID].Services[service.ID] = service));
    },
    async getLessons(userID, roomID) {
      const response = await fetch(`/api/users/${userID}/lessons`);
      const lessons = await response.json();
      lessons.forEach((lesson) => (this.rooms[roomID].Lessons[lesson.ID] = lesson));
    },
    async getMessages(userID, roomID) {
      const response = await fetch(`/api/users/${userID}/messages`);
      const messages = await response.json();
      messages.forEach((message) => (this.rooms[roomID].Messages[message.ID] = message));
    },
    async scrollToBottom() {
      await nextTick();
      let messageContainer = document.getElementById("message-container");
      messageContainer.scrollTop = messageContainer.scrollHeight;
    },
    async changeContact(userID) {
      this.$router.push({ path: `/chat/${userID}` });
      for (const [roomID, room] of Object.entries(this.rooms)) {
        if (room.User.ID == userID) {
          this.initChat(userID, roomID);
          break;
        }
      }
    },

    sendMessage() {
      if (this.text != "") {
        let message = { Message: this.text, RecieverID: this.activeRoom.User.ID };
        socket.send(JSON.stringify(message));
        this.text = "";
      }
    },
    sendLessonRequest() {
      this.lessonRequest.Datetime = dayjs(`${this.lessonRequest.Date} ${this.lessonRequest.Time}`).format();
      let message = {
        Message: "",
        RecieverID: this.activeRoom.User.ID,
        Lesson: this.lessonRequest,
      };
      socket.send(JSON.stringify(message));
      this.lessonView = true;
      this.resetLessonRequest();
    },
    sendModifiedLesson(lesson) {
      lesson.Datetime = dayjs(`${lesson.Date} ${lesson.Time}`).format();
      message = { ID: lesson.MessageID, Message: "", RecieverID: this.activeRoom.User.ID, Lesson: lesson };
      socket.send(JSON.stringify(message));
    },
    newLessonRequest(service) {
      this.lessonRequest.Title = service.Title;
      this.lessonRequest.ServiceID = service.ID;
      this.scrollToBottom();
    },
    resetLessonRequest() {
      this.lessonRequest.Title = "";
      let radios = document.getElementsByName("service");
      for (let i = 0; i < radios.length; i++) {
        radios[i].checked = false;
      }
    },
    parseSystemMessage(message) {
      // Original: mike cancelled yoga practice scheduled for 2025-01-13T14:00:00Z
      // Parsed: mike cancelled yoga practice scheduled for 2025-01-13 @ 09:00AM
      let index = message.indexOf("scheduled for ");
      if (index != -1) {
        let datetime = dayjs(message.slice(index + 14, index + 34)).format("YYYY-MM-DD @ hh:mmA");
        return message.slice(0, index + 14) + datetime + message.slice(index + 34);
      }
      return message;
    },
    findService(serviceID) {
      let ID = serviceID.toString();
      if (Object.keys(this.services).includes(ID)) {
        return this.services[ID];
      }
      return this.myServices[ID];
    },
    displayInChat(lesson) {
      return lesson.Status.startsWith("accepted_");
    },
    lessonActive(lesson) {
      return lesson.Status != "cancelled" && lesson.Status != "expired";
    },
    lessonCompleted(lesson) {
      return dayjs().isAfter(dayjs(lesson.Datetime));
    },
  },
};
</script>

<style lang="scss">
@import "@/assets/styles/mixins.scss";
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
      h3 {
        color: var(--blue0);
      }
    }
    .flex-container-peer {
      display: flex;
      justify-content: left;
      color: var(--orange);
      h3 {
        color: var(--orange);
      }
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
  }
  #chat-lesson-request {
    display: flex;
    justify-content: right;

    h3 {
      margin: 8px 0px;
      justify-content: left;
    }
    > form {
      padding: 0px 8px 12px;
      border: 1px dashed var(--green0);
      border-radius: 3px;
      width: 315px;

      input {
        padding: 4px;
        margin-bottom: 10px;
      }
      input.date {
        width: 128px;
        margin-right: 5px;
      }
      input.time {
        width: 75px;
      }
      select {
        padding: 4px;
        margin-right: 5px;
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
      margin-right: 3px;
      color: var(--red);
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
.lesson {
  padding: 5px 10px 10px 10px;
  margin-bottom: 10px;
  h3 {
    margin: 6px 0px;
  }
}
.empty-item {
  border: 1px dashed var(--green0);
  border-radius: 3px;
  padding: 13px;
}
</style>
