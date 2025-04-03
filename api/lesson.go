package api

import (
	"encoding/json"
	"net/http"
	"strconv"
	"time"
)

type Lesson struct {
	ID               uint
	ServiceID        uint
	TutorID          uint
	StudentID        uint
	MessageID        uint
	Duration         uint
	ModifiedDuration uint
	Datetime         time.Time
	CreatedAt        time.Time // managed by gorm
	Service          Service
	Student          User
	Tutor            User
	Status           LessonStatus
}

type LessonStatus string

const (
	LS_CANCELLED         LessonStatus = "cancelled"
	LS_EXPIRED           LessonStatus = "expired"
	LS_ACCEPTED          LessonStatus = "accepted"
	LS_ACCEPTED_STUDENT  LessonStatus = "accepted_student"
	LS_ACCEPTED_TUTOR    LessonStatus = "accepted_tutor"
	LS_CONFIRMED         LessonStatus = "confirmed"
	LS_CONFIRMED_STUDENT LessonStatus = "confirmed_student"
	LS_CONFIRMED_TUTOR   LessonStatus = "confirmed_tutor"
	LS_MODIFIED          LessonStatus = "modified"
)

var stringToLessonStatus = map[string]LessonStatus{
	"cancelled":         LS_CANCELLED,
	"expired":           LS_EXPIRED,
	"accepted":          LS_ACCEPTED,
	"accepted_student":  LS_ACCEPTED_STUDENT,
	"accepted_tutor":    LS_ACCEPTED_TUTOR,
	"confirmed":         LS_CONFIRMED,
	"confirmed_student": LS_CONFIRMED_STUDENT,
	"confirmed_tutor":   LS_CONFIRMED_TUTOR,
	"modified":          LS_MODIFIED,
}

func createLesson(sender_id uint, api_message *Message) (Lesson, bool) {
	service := Service{ID: api_message.Lesson.ServiceID}
	service.Get()

	// Verify that the message sender or reciever is offering this lesson
	if service.UserID != sender_id && service.UserID != api_message.RecieverID {
		return Lesson{}, false
	}

	lesson := Lesson{ServiceID: service.ID, TutorID: service.UserID, Duration: api_message.Lesson.Duration, Datetime: api_message.Lesson.Datetime}
	available := service.Status == SS_ACTIVE && lesson.Datetime.After(time.Now())
	if service.UserID == sender_id && available {
		lesson.StudentID = api_message.RecieverID
		lesson.Status = LS_ACCEPTED_TUTOR
	} else if service.UserID == api_message.RecieverID && available {
		lesson.StudentID = sender_id
		lesson.Status = LS_ACCEPTED_STUDENT
	} else {
		return Lesson{}, false
	}

	student := User{ID: lesson.StudentID}
	student.Get()
	if student.Minutes < int(lesson.Duration) {
		return Lesson{}, false
	}

	return lesson, true
}

func (current *Lesson) equals(other *Lesson) bool {
	return current.ID == other.ID && current.Datetime.UTC() == other.Datetime.UTC() && current.Duration == other.Duration && current.ModifiedDuration == other.ModifiedDuration && current.Status == other.Status
}

func (current *Lesson) merge(updated *Lesson, user_id uint) bool {
	lesson_started := current.Datetime.Before(time.Now())
	clone := *current

	// Only allow cancelations before lesson start
	if updated.Status == LS_CANCELLED && !lesson_started {
		current.Status = updated.Status
	} else if current.Status == LS_ACCEPTED_STUDENT && current.TutorID == user_id && updated.Status == LS_CONFIRMED {
		current.Status = LS_ACCEPTED
	} else if current.Status == LS_ACCEPTED_TUTOR && current.StudentID == user_id && updated.Status == LS_CONFIRMED {
		current.Status = LS_ACCEPTED
	} else if (current.Status == LS_ACCEPTED_STUDENT || current.Status == LS_ACCEPTED_TUTOR) && updated.Status == LS_MODIFIED {
		// Prior to lesson acceptance, participants can endlessly modify lesson parameters
		if user_id == current.TutorID {
			current.Status = LS_ACCEPTED_TUTOR
		} else {
			current.Status = LS_ACCEPTED_STUDENT
		}
		current.Datetime = updated.Datetime
		current.Duration = updated.Duration
	} else if (current.Status == LS_ACCEPTED || current.Status == LS_CONFIRMED_STUDENT || current.Status == LS_CONFIRMED_TUTOR) && updated.ModifiedDuration != current.ModifiedDuration && updated.Status == LS_MODIFIED {
		// After lesson acceptance, participants can only modify duration
		if user_id == current.TutorID && current.Status != LS_CONFIRMED_TUTOR {
			current.Status = LS_CONFIRMED_TUTOR
			current.ModifiedDuration = updated.ModifiedDuration
		} else if user_id == current.StudentID && current.Status != LS_CONFIRMED_STUDENT {
			current.Status = LS_CONFIRMED_STUDENT
			current.ModifiedDuration = updated.ModifiedDuration
		}
	} else if current.Status == LS_ACCEPTED && updated.Status == LS_CONFIRMED {
		if user_id == current.TutorID {
			current.Status = LS_CONFIRMED_TUTOR
		} else {
			current.Status = LS_CONFIRMED_STUDENT
		}
	} else if current.Status == LS_CONFIRMED_STUDENT && current.TutorID == user_id && updated.Status == LS_CONFIRMED {
		current.Status = LS_CONFIRMED
	} else if current.Status == LS_CONFIRMED_TUTOR && current.StudentID == user_id && updated.Status == LS_CONFIRMED {
		current.Status = LS_CONFIRMED
	}
	return !current.equals(&clone)
}

// GET /api/users/me/lessons/
func GetMyLessons(writer http.ResponseWriter, request *http.Request) {
	user, ok := UserFromRequest(*request)
	if !ok {
		http.Error(writer, invalidSessionToken.String(), http.StatusUnauthorized)
		return
	}

	var lessons []Lesson
	status := request.URL.Query().Get("status")
	UserLessonsGet(user, &lessons, stringToLessonStatus[status])
	ret, _ := json.Marshal(lessons)
	writer.Write(ret)
}

// GET /api/users/{id}/lessons/
func GetOurLessons(writer http.ResponseWriter, request *http.Request) {
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

	var lessons []Lesson
	OurLessonsGet(user, other, &lessons)
	ret, _ := json.Marshal(lessons)
	writer.Write(ret)
}
