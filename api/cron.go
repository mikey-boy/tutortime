package api

import (
	"fmt"
	"time"

	"github.com/robfig/cron/v3"
)

func expireLessons() {
	var scheduledEarly []Lesson
	var scheduledLate []Lesson

	// Lessons that start within 24 hours and have been created at least two days in advance
	oneDayFromNow := time.Now().Add(time.Hour * 24)
	db.Preload("Service").Where("datetime - created_at > interval '48 hours'").Where("datetime < ?", oneDayFromNow).Where("status = ? OR status = ?", LS_ACCEPTED_STUDENT, LS_ACCEPTED_TUTOR).Find(&scheduledEarly)
	// Lessons that are not accepted before their start time
	db.Preload("Service").Where("datetime < ?", time.Now()).Where("status = ? OR status = ?", LS_ACCEPTED_STUDENT, LS_ACCEPTED_TUTOR).Find(&scheduledLate)

	for _, lesson := range append(scheduledEarly, scheduledLate...) {
		db.Model(&lesson).Update("status", LS_EXPIRED)
		room := Room{}
		room.Get(User{ID: lesson.TutorID}, User{ID: lesson.StudentID})

		system_message := Message{RoomID: room.ID}
		system_message.Message = fmt.Sprintf("'%s' scheduled for %s has expired", lesson.Service.Title, lesson.Datetime.UTC().Format(time.RFC3339))
		system_message.Add()
		sendMessage(lesson.StudentID, lesson.TutorID, system_message)

		lesson_message := Message{ID: lesson.MessageID}
		db.Preload("Lesson").First(&lesson_message)
		hub.message <- lesson_message
	}
}

func RegisterCrons() {
	cron := cron.New()

	// Check for expired lessons every minute
	cron.AddFunc("*/1 * * * *", expireLessons)

	cron.Start()
}
