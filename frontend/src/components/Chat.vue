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

      <div v-if="Object.keys(messages).length == 0" id="message-container">
        <div class="flex-container-system">
          <span class="message-item-system">
            This is your chat with {{ activeRoom.User.Username }}! You can begin by:
            <ul>
              <li>Introducing yourself</li>
              <li>Explaining why you are interested in the subject they teach</li>
              <li>Describing your current skill level, and any learning objectives you may have</li>
            </ul>
          </span>
        </div>
      </div>
      <div v-else id="message-container">
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
                <div class="centered cancel-circle-button">
                  <i @click="resetLessonRequest" class="fa-solid fa-xmark fa-xl"></i>
                </div>
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
        <div id="modal" v-show="modalText">
          <div>
            <p>{{ modalText }}</p>
          </div>
          <div class="centered">
            <div class="centered cancel-circle-button">
              <i @click="modalText = ''" class="fa-solid fa-xmark fa-lg"></i>
            </div>
          </div>
        </div>
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
      <h2 id="lessons-title">Lessons</h2>
      <div id="minutes-bubble">
        You have <b>{{ self.Minutes }} minutes</b>
        <div class="tooltip">
          <i class="fa-solid fa-circle-info"></i>
          <span class="tooltiptext bottomleft">
            To earn more, you can
            <b>
              <RouterLink :to="{ path: 'discover', query: { page: 'giving-lessons' } }">
                offer lessons to other students
              </RouterLink>
            </b>
          </span>
        </div>
      </div>

      <div v-if="Object.keys(messages).length != 0" class="lesson-tabs">
        <button class="request-lessons left-button" :class="{ inactive: lessonView }" @click="lessonView = !lessonView">
          <i class="fa-solid fa-handshake fa-lg"></i> Request a lesson
        </button>
        <button class="view-lessons right-button" :class="{ inactive: !lessonView }" @click="lessonView = !lessonView">
          <i class="fa-regular fa-calendar-days fa-lg"></i> Lessons booked
        </button>
      </div>
      <div class="lesson-tabs sub-tabs" v-show="lessonView">
        <button class="left-button" :class="{ inactive: completedView }" @click="completedView = false">
          Scheduled
        </button>
        <button class="right-button" :class="{ inactive: !completedView }" @click="completedView = true">
          Completed
        </button>
      </div>

      <div v-if="Object.keys(messages).length == 0">
        <div id="empty-messages">
          <div>
            You will be able to request a lesson from <b>{{ activeRoom.User.Username }}</b> after you have sent them an
            initial message
          </div>
        </div>
      </div>
      <div v-else-if="lessonView" class="lesson-container">
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
          <h3>{{ activeRoom.User.Username }} offers these services</h3>
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
        </div>
      </div>
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
      modalText: "",
      self: {},
      rooms: {},
      activeRoom: null,
      contacts: [],
      messages: {},
      lessons: {},
      services: {},
      myServices: {},
      lessonView: false,
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
    this.fetchSelf();
    this.fetchContacts();
    this.getMyServices();
    socket = new WebSocket(`ws://${window.location.host}/ws`);
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
          this.fetchSelf();
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

      this.modalText = "";
      this.resetLessonRequest();
      this.scrollToBottom();
    },
    async fetchSelf() {
      const response = await fetch(`/api/users/me`);
      this.self = await response.json();
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
      if (this.lessonRequest.Duration > this.self.Minutes) {
        this.modalText = "You do not have enough minutes for this lesson";
        return;
      }
      if (dayjs().isAfter(`${this.lessonRequest.Date} ${this.lessonRequest.Time}`)) {
        this.modalText = "You cannot schedule lessons in the past";
        return;
      }

      this.modalText = "";
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
      if (lesson.StudentID == this.self.ID && lesson.ModifiedDuration - lesson.Duration > this.self.Minutes + 60) {
        this.modalText = "You do not have enough minutes to accomodate the modified duration";
        return;
      }
      lesson.Datetime = dayjs(`${lesson.Date} ${lesson.Time}`).format();
      let message = { ID: lesson.MessageID, Message: "", RecieverID: this.activeRoom.User.ID, Lesson: lesson };
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
#empty-messages {
  border: 1px dashed var(--green0);
  border-radius: 3px;
  padding: 10px;
  margin-top: 20px;
}
#chat-container {
  display: flex;
  margin: 0 auto;
  padding: 20px;
  height: 890px;
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
    margin-top: 36px;
    position: relative;

    input {
      flex: 1;
      padding: 7px 10px;
      border: none;
      border-radius: 3px;
      margin-right: 10px;
    }
    #modal {
      display: flex;
      position: absolute;
      z-index: 1;
      bottom: 40px;
      width: 100%;
      background-color: var(--base0);
      border: 1px solid var(--red1);
      border-radius: 3px;

      p {
        margin: 3px 10px;
      }
      .centered {
        margin-left: auto;
      }
    }
    #send-message-button {
      color: var(--text1);
      padding: 7px 25px;
      background-color: var(--green1);
    }
  }
  #message-container {
    height: 725px;
    min-width: 330px;
    overflow-y: scroll;

    &.minimized {
      height: 388px;
    }
    .flex-container-user {
      display: flex;
      margin-left: 70px;
      justify-content: right;
      color: var(--blue0);
      h3 {
        color: var(--blue0);
      }
    }
    .flex-container-peer {
      display: flex;
      margin-right: 70px;
      justify-content: left;
      color: var(--text2);
      h3 {
        color: var(--blue0);
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
    .flex-container-peer .message-item {
      border: 2px solid var(--base2);
    }
    .message-item-system {
      margin: 5px 0px;
    }
  }
  #chat-lesson-request {
    display: flex;
    justify-content: right;
    margin-bottom: 10px;

    h3 {
      margin: 8px 0px;
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
    #lesson-request-error {
      margin: 0px;
      color: var(--red1);
      font-weight: bold;
    }
  }
}
#lessons {
  flex: 2;
  margin: 0px 10px;

  .lesson-tabs {
    display: flex;

    button {
      flex: 1;
      padding: 8px;
      color: var(--text1);
      font-weight: bold;
      border: 1px solid var(--green0);
      background-color: var(--green1);
    }
    button.inactive {
      color: var(--text0);
      background: var(--base1);
    }
    &.sub-tabs {
      margin-top: 10px;
      margin-bottom: 15px;
    }
    .view-lessons {
      background-color: var(--orange);
    }
    .request-lessons {
      background-color: var(--blue0);
    }
    .right-button {
      border-radius: 0 3px 3px 0;
    }
    .left-button {
      border-radius: 3px 0 0 3px;
      border-right: none;
    }
  }
  .lesson-container {
    min-width: 180px;
    height: 710px;
    overflow-y: scroll;

    h3 {
      margin-bottom: 15px;
    }
    p {
      color: var(--text0);
      font-size: medium;
      margin-top: 5px;
    }
    .lesson {
      background-color: var(--base1);
    }
  }
  .lesson-container.without-subnav {
    height: 760px;
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
    border: 1px solid var(--red1);
  }

  #lessons-title {
    margin-bottom: 12px;
  }
  #minutes-bubble {
    margin-bottom: 10px;
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
