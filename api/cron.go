package api

import (
	"fmt"
	"math/rand"
	"time"

	"github.com/robfig/cron/v3"
	"github.com/wordgen/wordlists"
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
		room.Get(lesson.TutorID, lesson.StudentID)

		system_message := Message{RoomID: room.ID}
		system_message.Message = fmt.Sprintf("'%s' scheduled for %s has expired", lesson.Service.Title, lesson.Datetime.UTC().Format(time.RFC3339))
		system_message.Add()
		sendMessage(lesson.StudentID, lesson.TutorID, system_message)

		lesson_message := Message{ID: lesson.MessageID}
		db.Preload("Lesson").First(&lesson_message)
		hub.message <- lesson_message
	}
}

func sendMeetupLink() {
	var lessons []Lesson
	wl_len := len(wordlists.EffLarge)

	db.Where("datetime < ?", time.Now().Add(time.Minute*15)).Where("status = ? and link_sent = ?", LS_ACCEPTED, false).Find(&lessons)
	for _, lesson := range lessons {
		db.Model(&lesson).Update("link_sent", true)
		room := Room{}
		room.Get(lesson.TutorID, lesson.StudentID)

		system_message := Message{RoomID: room.ID}
		word1, word2, word3 := wordlists.EffLarge[rand.Intn(wl_len)], wordlists.EffLarge[rand.Intn(wl_len)], wordlists.EffLarge[rand.Intn(wl_len)]
		system_message.Message = fmt.Sprintf("lesson_upcoming|https://talky.io/%s-%s-%s", word1, word2, word3)
		system_message.Add()
		sendMessage(lesson.StudentID, lesson.TutorID, system_message)
	}
}

func sendConfirmationReminder() {
	var lessons []Lesson
	db.Where("datetime < ?", time.Now()).Where("status = ? and reminder_sent = ?", LS_ACCEPTED, false).Find(&lessons)
	for _, lesson := range lessons {
		if time.Now().After(lesson.Datetime.Add(time.Duration(lesson.Duration) * time.Minute)) {
			db.Model(&lesson).Update("reminder_sent", true)
			room := Room{}
			room.Get(lesson.TutorID, lesson.StudentID)
			system_message := Message{RoomID: room.ID, Message: "lesson_completed"}
			system_message.Add()
			sendMessage(lesson.StudentID, lesson.TutorID, system_message)
		}
	}
}

func confirmOldLessons() {
	var lessons []Lesson
	db.Where("datetime < ?", time.Now().Add(time.Hour*-24)).Where("status = ? or status = ? or status = ?", LS_ACCEPTED, LS_CONFIRMED_STUDENT, LS_CONFIRMED_TUTOR).Find(&lessons)
	for _, lesson := range lessons {
		room := Room{}
		service := Service{ID: lesson.ServiceID}
		tutor, student := User{ID: lesson.TutorID}, User{ID: lesson.StudentID}
		room.Get(lesson.TutorID, lesson.StudentID)
		service.Get()
		tutor.Get()
		student.Get()

		db.Model(&lesson).Update("status", LS_CONFIRMED)
		tutor.Minutes += int(lesson.Duration)
		tutor.Update()
		service.Minutes += lesson.Duration
		service.Lessons += 1
		service.Update()

		system_message := Message{RoomID: room.ID, SenderID: 0, RecieverID: 0}
		system_message2 := Message{RoomID: room.ID, SenderID: 0, RecieverID: 0}
		system_message.Message = fmt.Sprintf("'%s' scheduled for %s has been automatically %s", service.Title, lesson.Datetime.UTC().Format(time.RFC3339), lesson.Status)
		system_message2.Message = fmt.Sprintf("%d minutes transferred from %s to %s", lesson.Duration, student.Username, tutor.Username)
		system_message.Add()
		system_message2.Add()
		sendMessage(lesson.TutorID, lesson.StudentID, system_message)
		sendMessage(lesson.TutorID, lesson.StudentID, system_message2)
	}
}

func RegisterCrons() {
	cron := cron.New()

	// Check for any upcoming lessons every minute
	cron.AddFunc("*/1 * * * *", sendMeetupLink)

	// Check for any completed lessons every minute
	cron.AddFunc("*/1 * * * *", sendConfirmationReminder)

	// Check for expired lessons every minute
	cron.AddFunc("*/1 * * * *", expireLessons)

	// Check for old lessons every 30 minute
	cron.AddFunc("*/30 * * * *", confirmOldLessons)

	// Rotate the logs every day
	cron.AddFunc("0 0 * * *", LogRotate)

	cron.Start()
}
