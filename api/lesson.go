package api

import (
	"encoding/json"
	"net/http"
	"strconv"
	"time"

	"gorm.io/gorm"
)

type Lesson struct {
	ID        uint
	ServiceID uint
	TutorID   uint
	StudentID uint
	MessageID uint
	Duration  uint
	Datetime  time.Time
	Status    LessonStatus
}

type LessonStatus string

const (
	CANCELLED         LessonStatus = "cancelled"
	EXPIRED           LessonStatus = "expired"
	ACCEPTED          LessonStatus = "accepted"
	ACCEPTED_STUDENT  LessonStatus = "accepted_student"
	ACCEPTED_TUTOR    LessonStatus = "accepted_tutor"
	COMPLETED         LessonStatus = "completed"
	CONFIRMED         LessonStatus = "confirmed"
	CONFIRMED_STUDENT LessonStatus = "confirmed_student"
	CONFIRMED_TUTOR   LessonStatus = "confirmed_tutor"
)

func (current *Lesson) merge(updated *Lesson, user_id uint) {
	if updated.Status == CANCELLED {
		current.Status = updated.Status
	} else if current.Status == ACCEPTED_STUDENT && current.TutorID == user_id && updated.Status == ACCEPTED {
		current.Status = ACCEPTED
	} else if current.Status == ACCEPTED_TUTOR && current.StudentID == user_id && updated.Status == ACCEPTED {
		current.Status = ACCEPTED
	} else if (current.Status == ACCEPTED_STUDENT || current.Status == ACCEPTED_TUTOR) && (updated.Status == ACCEPTED_STUDENT || updated.Status == ACCEPTED_TUTOR) {
		current.Status = updated.Status
		current.Datetime = updated.Datetime
		current.Duration = updated.Duration
	} else if current.Status == COMPLETED && current.TutorID == user_id {
		if updated.Status == CONFIRMED {
			current.Status = updated.Status
		} else if updated.Status == CONFIRMED_TUTOR {
			current.Status = updated.Status
			current.Duration = updated.Duration
		}
	} else if current.Status == COMPLETED && current.StudentID == user_id {
		if updated.Status == CONFIRMED {
			current.Status = updated.Status
		} else if updated.Status == CONFIRMED_STUDENT {
			current.Status = updated.Status
			current.Duration = updated.Duration
		}
	}
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
	UserLessonsGet(user, other, &lessons)
	ret, _ := json.Marshal(lessons)
	writer.Write(ret)
}

// PATCH /api/lessons/{id}
func UpdateLesson(writer http.ResponseWriter, request *http.Request) {
	id, _ := strconv.ParseUint(request.PathValue("id"), 10, 0)
	lesson := Lesson{ID: uint(id)}

	// Verify lesson exists
	if err := lesson.Get(); err == gorm.ErrRecordNotFound {
		http.Error(writer, resourceNotFound.String(), http.StatusNotFound)
		return
	}

	// Verify user can modify this lesson
	var user User
	if user, ok := UserFromRequest(*request); !ok || (lesson.StudentID != user.ID && lesson.TutorID != user.ID) {
		http.Error(writer, wrongSessionToken.String(), http.StatusUnauthorized)
		return
	}

	var updated Lesson
	if err := json.NewDecoder(request.Body).Decode(&updated); err != nil {
		http.Error(writer, malformedJson.String(), http.StatusBadRequest)
		return
	}

	if updated.Status == CANCELLED {
		lesson.Status = updated.Status
	} else if lesson.Status == ACCEPTED_STUDENT && lesson.TutorID == user.ID {
		if updated.Status == ACCEPTED {
			lesson.Status = updated.Status
		} else if updated.Status == ACCEPTED_TUTOR {
			lesson.Status = updated.Status
			lesson.Datetime = updated.Datetime
			lesson.Duration = updated.Duration
		}
	} else if lesson.Status == ACCEPTED_TUTOR && lesson.StudentID == user.ID {
		if updated.Status == ACCEPTED {
			lesson.Status = updated.Status
		} else if updated.Status == ACCEPTED_STUDENT {
			lesson.Status = updated.Status
			lesson.Datetime = updated.Datetime
			lesson.Duration = updated.Duration
		}
	} else if lesson.Status == COMPLETED && lesson.TutorID == user.ID {
		if updated.Status == CONFIRMED {
			lesson.Status = updated.Status
		} else if updated.Status == CONFIRMED_TUTOR {
			lesson.Status = updated.Status
			lesson.Duration = updated.Duration
		}
	} else if lesson.Status == COMPLETED && lesson.StudentID == user.ID {
		if updated.Status == CONFIRMED {
			lesson.Status = updated.Status
		} else if updated.Status == CONFIRMED_STUDENT {
			lesson.Status = updated.Status
			lesson.Duration = updated.Duration
		}
	}
}
