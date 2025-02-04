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
	oneDayAgo, twoDaysAgo := time.Now().Add(time.Hour*-1), time.Now().Add(time.Hour*-2)
	db.Preload("Service").Where("datetime < ?", oneDayAgo).Where("created_at > ?", twoDaysAgo).Where("status = ? OR status = ?", ACCEPTED_STUDENT, ACCEPTED_TUTOR).Find(&scheduledEarly)
	// Lessons that are not accepted before their start time
	db.Preload("Service").Where("datetime < ?", time.Now()).Where("status = ? OR status = ?", ACCEPTED_STUDENT, ACCEPTED_TUTOR).Find(&scheduledLate)

	for _, lesson := range append(scheduledEarly, scheduledLate...) {
		room := Room{}
		room.Get(User{ID: lesson.TutorID}, User{ID: lesson.StudentID})
		message := Message{RoomID: room.ID}
		message.Message = fmt.Sprintf("Tutortime expired '%s' scheduled for %s", lesson.Service.Title, lesson.Datetime.UTC().Format(time.RFC3339))
		message.Add()
		sendMessage(lesson.StudentID, lesson.TutorID, message)
		db.Model(&lesson).Update("status", EXPIRED)
	}
}

func RegisterCrons() {
	cron := cron.New()

	// Check for expired lessons every minute
	cron.AddFunc("*/1 * * * *", expireLessons)

	cron.Start()
}
