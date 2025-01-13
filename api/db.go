package api

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"mime/multipart"
	"os"

	"github.com/google/uuid"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

var db *gorm.DB

func (status *ServiceStatus) UnmarshalJSON(b []byte) error {
	var s string
	if err := json.Unmarshal(b, &s); err != nil {
		return err
	}

	*status = stringToStatus[s]
	return nil
}

func (status *ServiceCategory) UnmarshalJSON(b []byte) error {
	var s string
	if err := json.Unmarshal(b, &s); err != nil {
		return err
	}

	*status = stringToCategory[s]
	return nil
}

func (user *User) Add() error {
	result := db.Select("username", "password").Create(&user)
	return result.Error
}

func (user *User) Login() error {
	result := db.Where(&user, "username", "password").First(&user)
	return result.Error
}

func (user *User) Get() error {
	result := db.First(&user)
	return result.Error
}

func (session *Session) Add() error {
	result := db.Create(session)
	return result.Error
}

func (session *Session) Get() error {
	result := db.Where(&session, "uuid").First(&session)
	return result.Error
}

func (session *Session) Valid() bool {
	return true
}

func (service *Service) Add() error {
	result := db.Create(service)
	return result.Error
}

func (service *Service) Get() error {
	preloadFunc := func(db *gorm.DB) *gorm.DB {
		return db.Select("id", "username")
	}

	result := db.Preload("Image").Preload("User", preloadFunc).First(&service)
	return result.Error
}

func (service *Service) Update() error {
	result := db.Save(service)
	if result.Error != nil {
		return result.Error
	}
	result = db.Save(service.Image)
	return result.Error
}

func (lesson *Lesson) Add() error {
	result := db.Create(lesson)
	return result.Error
}

func (lesson *Lesson) Get() error {
	result := db.First(&lesson)
	return result.Error
}

func (lesson *Lesson) Update() error {
	result := db.Save(lesson)
	return result.Error
}

func (image *Image) Add(category ServiceCategory) {
	image.Name = fmt.Sprintf("%s.jpg", string(category))
	image.Path = fmt.Sprintf("/default/img/%s", image.Name)
}

func (image *Image) Upload(file multipart.File, name string) error {
	defer file.Close()
	path := "/img/" + uuid.New().String()
	outFile, err := os.Create("instance" + path)
	if err != nil {
		return err
	}

	defer outFile.Close()
	_, err = io.Copy(outFile, file)
	if err != nil {
		return err
	}

	image.Name = name
	image.Path = path
	image.OSPath = outFile.Name()
	return nil
}

func (image *Image) Delete() {
	if image.OSPath != "" {
		os.Remove(image.OSPath)
		image.OSPath = ""
	}
	image.Name = ""
	image.Path = ""
}

func (message *Message) Get() error {
	result := db.First(&message)
	return result.Error
}
func (message *Message) Add() error {
	var room Room
	if message.SenderID < message.RecieverID {
		db.FirstOrCreate(&room, Room{User1ID: message.SenderID, User2ID: message.RecieverID})
	} else {
		db.FirstOrCreate(&room, Room{User1ID: message.RecieverID, User2ID: message.SenderID})
	}

	message.RoomID = room.ID
	result := db.Create(message)
	return result.Error
}
func (message *Message) Update() error {
	result := db.Save(message)
	return result.Error
}

func ServicesGet(services *[]Service, query string, category ServiceCategory) {
	preloadFunc := func(db *gorm.DB) *gorm.DB {
		return db.Select("id", "username")
	}

	// TODO: Probably really inefficient to Preload like this
	if query != "" && category != "" {
		db.Preload("Image").Preload("User", preloadFunc).Where("title ILIKE @query OR description ILIKE @query", sql.Named("query", fmt.Sprint("%", query, "%"))).Where("category = ?", category).Find(&services)
	} else if query != "" {
		db.Preload("Image").Preload("User", preloadFunc).Where("title ILIKE @query OR description ILIKE @query", sql.Named("query", fmt.Sprint("%", query, "%"))).Find(&services)
	} else if category != "" {
		db.Preload("Image").Preload("User", preloadFunc).Where("category = ?", category).Find(&services)
	} else {
		db.Preload("Image").Preload("User", preloadFunc).Find(&services)
	}
}

func UserServicesGet(user User, services *[]Service, all bool) {
	if all {
		db.Where("user_id = ?", user.ID).Find(&services)
	} else {
		db.Where("user_id = ? AND status = ?", user.ID, Active).Find(&services)
	}
}

func UserLessonsGet(user User, other User, lessons *[]Lesson) {
	db.Where("tutor_id = ? AND student_id = ?", user.ID, other.ID).Or("tutor_id = ? AND student_id = ?", other.ID, user.ID).Find(&lessons)
}

func (room *Room) Get(user User, other User) {
	if user.ID < other.ID {
		db.Where("user1_id = ? AND user2_id = ?", user.ID, other.ID).First(&room)
	} else {
		db.Where("user1_id = ? AND user2_id = ?", other.ID, user.ID).First(&room)
	}
}

func MessagesGet(messages *[]Message, user User, other User) {
	var room Room
	room.Get(user, other)
	db.Model(Message{}).Joins("Lesson").Where("room_id = ?", room.ID).Order("ID asc").Find(&messages)
}

func ContactsGet(contacts *[]User, user User) {
	preloadFunc := func(db *gorm.DB) *gorm.DB {
		return db.Select("id", "username")
	}

	var rooms1 []Room
	var rooms2 []Room
	db.Model(&Room{}).Preload("User2", preloadFunc).Where("user1_id = ?", user.ID).Find(&rooms1)
	db.Model(&Room{}).Preload("User1", preloadFunc).Where("user2_id = ?", user.ID).Find(&rooms2)

	for _, room := range rooms1 {
		*contacts = append(*contacts, room.User2)
	}
	for _, room := range rooms2 {
		*contacts = append(*contacts, room.User1)
	}
}

func createTables() {
	db.AutoMigrate(&User{})
	db.AutoMigrate(&Session{})
	db.AutoMigrate(&Service{})
	db.AutoMigrate(&Image{})
	db.AutoMigrate(&Message{})
	db.AutoMigrate(&Lesson{})
	db.AutoMigrate(&Room{})
}

func CreateConnection(host string, user string, password string, dbname string, port uint16) {
	var err error

	dsn := fmt.Sprintf(
		"host=%s user=%s password=%s dbname=%s port=%d sslmode=disable TimeZone=America/Toronto",
		host,
		user,
		password,
		dbname,
		port,
	)

	db, err = gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatalf("Error connecting to database: %v", err)
	}

	createTables()
}
