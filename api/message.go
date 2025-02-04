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
		if api_message.Lesson.Status == ACCEPTED_TUTOR || api_message.Lesson.Status == ACCEPTED_STUDENT {
			if client_id == api_message.Lesson.TutorID {
				api_message.Lesson.Status = ACCEPTED_TUTOR
			} else {
				api_message.Lesson.Status = ACCEPTED_STUDENT
			}
		}

		sender := User{ID: client_id}
		service := Service{ID: api_message.Lesson.ServiceID}
		service.Get()
		sender.Get()

		api_lesson := Lesson{ID: api_message.Lesson.ID, Status: api_message.Lesson.Status, Duration: api_message.Lesson.Duration, Datetime: api_message.Lesson.Datetime}
		lesson := Lesson{ID: api_message.Lesson.ID}
		lesson.Get()
		lesson.merge(&api_lesson, client_id)
		lesson.Update()

		message.SenderID = client_id
		message.RecieverID = api_message.RecieverID
		message.Lesson = &lesson
		message.Update()

		if api_message.Lesson.Status == ACCEPTED || api_message.Lesson.Status == CANCELLED {
			system_message := Message{RoomID: message.RoomID}
			datetime := lesson.Datetime.UTC().Format(time.RFC3339)
			system_message.Message = fmt.Sprintf("%s %s '%s' scheduled for %s", sender.Username, api_message.Lesson.Status, service.Title, datetime)
			system_message.Add()
			sendMessage(message.SenderID, message.RecieverID, system_message)
		}
	} else if api_message.Lesson != nil && api_message.Lesson.ServiceID != 0 {
		service := Service{ID: api_message.Lesson.ServiceID}
		service.Get()

		message = Message{SenderID: client_id, RecieverID: api_message.RecieverID}
		lesson := Lesson{ServiceID: api_message.Lesson.ServiceID, TutorID: service.UserID, Duration: api_message.Lesson.Duration, Datetime: api_message.Lesson.Datetime}
		if service.UserID == message.SenderID {
			lesson.StudentID = message.RecieverID
			lesson.Status = ACCEPTED_TUTOR
		} else if service.UserID == message.RecieverID {
			lesson.StudentID = message.SenderID
			lesson.Status = ACCEPTED_STUDENT
		} else {
			return false, Message{}
		}
		message.Lesson = &lesson
		message.Add()
	} else {
		message = Message{SenderID: client_id, RecieverID: api_message.RecieverID, Message: api_message.Message}
		message.Add()
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

// GET /api/contacts
func GetContacts(writer http.ResponseWriter, request *http.Request) {
	user, ok := UserFromRequest(*request)
	if !ok {
		http.Error(writer, invalidSessionToken.String(), http.StatusUnauthorized)
		return
	}

	contacts := []User{}
	ContactsGet(&contacts, user)
	ret, _ := json.Marshal(contacts)
	writer.Write(ret)
}
