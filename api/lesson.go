package api

import (
	"encoding/json"
	"net/http"
)

type Lesson struct {
	ID        uint
	TutorID   uint
	StudentID uint
	ServiceID uint
}

type LessonStatus string

const (
	CANCELLED         LessonStatus = "cancelled"
	EXPIRED           LessonStatus = "expired"
	ACCEPTED          LessonStatus = "accepted"
	ACCEPTED_STUDENT  LessonStatus = "accepted_student"
	ACCEPTED_TUTOR    LessonStatus = "accepted_tutor"
	CONFIRMED         LessonStatus = "confirmed"
	CONFIRMED_STUDENT LessonStatus = "confirmed_student"
	CONFIRMED_TUTOR   LessonStatus = "confirmed_tutor"
)

// GET /api/users/me/services/
func GetMyLessons(writer http.ResponseWriter, request *http.Request) {
	var lessons []Lesson
	user, ok := UserFromRequest(*request)
	if !ok {
		http.Error(writer, invalidSessionToken.String(), http.StatusUnauthorized)
		return
	}

	UserLessonsGet(user, &lessons)
	ret, _ := json.Marshal(lessons)
	writer.Write(ret)
}
