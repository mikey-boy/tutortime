package api

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"time"
)

type Message struct {
	ID         uint
	RoomID     uint
	SenderID   uint
	RecieverID uint
	Message    string
	Lesson     *Lesson
}

type Room struct {
	ID          uint
	Messages    []Message
	User1ID     uint
	User1       User
	User2ID     uint
	User2       User
	LastMessage string
	UpdatedAt   time.Time
}

func parseSocketMessage(client_id uint, api_message Message) (ok bool, message Message) {
	if api_message.Lesson != nil && api_message.Lesson.ID != 0 {
		message = Message{ID: api_message.ID}
		message.Get()

		if client_id != message.SenderID && client_id != message.RecieverID {
			return false, Message{}
		}

		datetime := api_message.Lesson.Datetime.UTC()
		api_lesson := Lesson{ID: api_message.Lesson.ID, Status: api_message.Lesson.Status, Duration: api_message.Lesson.Duration, Datetime: datetime}
		lesson := Lesson{ID: api_message.Lesson.ID}
		lesson.Get()
		modified := lesson.merge(&api_lesson, client_id)
		if !modified {
			return false, Message{}
		}
		lesson.Update()

		// Reverse the sender/reciever if appropriate
		if client_id == message.RecieverID {
			message.RecieverID = message.SenderID
			message.SenderID = client_id
		}

		message.Lesson = &lesson
		message.Update()

		if message.Lesson.Status == LS_ACCEPTED || message.Lesson.Status == LS_CANCELLED || message.Lesson.Status == LS_CONFIRMED {
			var room Room
			room.Get(message.SenderID, message.RecieverID)
			service := Service{ID: api_message.Lesson.ServiceID}
			service.Get()
			system_message := Message{RoomID: room.ID, SenderID: 0, RecieverID: 0}
			system_message.Message = fmt.Sprintf("'%s' scheduled for %s has been %s", service.Title, datetime.Format(time.RFC3339), message.Lesson.Status)
			system_message.Add()
			sendMessage(message.SenderID, message.RecieverID, system_message)
		}
		if message.Lesson.Status == LS_CONFIRMED {
			tutor, student := User{ID: lesson.TutorID}, User{ID: lesson.StudentID}
			service := Service{ID: api_message.Lesson.ServiceID}
			tutor.Get()
			student.Get()
			service.Get()
			var duration uint
			if lesson.ModifiedDuration == 0 {
				duration = lesson.Duration
			} else {
				duration = lesson.ModifiedDuration
			}

			transferMinutes(&tutor, &student, &service, duration)
			var room Room
			room.Get(message.SenderID, message.RecieverID)
			system_message := Message{RoomID: room.ID, SenderID: 0, RecieverID: 0}
			system_message.Message = fmt.Sprintf("%d minutes transferred from %s to %s", duration, student.Username, tutor.Username)
			system_message.Add()
			sendMessage(message.SenderID, message.RecieverID, system_message)
		}
	} else if api_message.Lesson != nil && api_message.Lesson.ServiceID != 0 {
		lesson, ok := createLesson(client_id, &api_message)
		if ok {
			message = Message{SenderID: client_id, RecieverID: api_message.RecieverID}
			message.Lesson = &lesson
			message.Add()
		}
	} else if api_message.Message != "" {
		message = Message{SenderID: client_id, RecieverID: api_message.RecieverID, Message: api_message.Message}
		message.Add()
	} else {
		return false, Message{}
	}
	return true, message
}

// GET /api/users/:id/messages/
func GetOurMessages(writer http.ResponseWriter, request *http.Request) {
	id, err := strconv.ParseUint(request.PathValue("id"), 10, 0)
	if err != nil {
		http.Error(writer, malformedRequest.String(), http.StatusBadRequest)
		return
	}

	other := User{ID: uint(id)}
	if err := other.Get(); err != nil {
		http.Error(writer, userNotFound.String(), http.StatusNotFound)
		return
	}

	user, ok := UserFromRequest(*request)
	if !ok {
		http.Error(writer, invalidSessionToken.String(), http.StatusUnauthorized)
		return
	}

	messages := []Message{}
	MessagesGet(&messages, user, other)
	ret, _ := json.Marshal(messages)
	writer.Write(ret)
}

// GET /api/rooms
func GetRooms(writer http.ResponseWriter, request *http.Request) {
	user, ok := UserFromRequest(*request)
	if !ok {
		http.Error(writer, invalidSessionToken.String(), http.StatusUnauthorized)
		return
	}

	rooms := []Room{}
	RoomsGet(&rooms, user)
	ret, _ := json.Marshal(rooms)
	writer.Write(ret)
}
