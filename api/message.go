package api

import (
	"encoding/json"
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
