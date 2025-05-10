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
	"golang.org/x/crypto/bcrypt"
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
	result := db.Create(user)
	return result.Error
}

func (user *User) Update() error {
	result := db.Save(user)
	return result.Error
}

func (user *User) Login() error {
	var result *gorm.DB
	if user.OAuthLogin != "" {
		result = db.Where(&user, "o_auth_login").First(&user)
	} else {
		var tmp User
		result = db.Where(&user, "username").First(&tmp)
		if bcrypt.CompareHashAndPassword([]byte(tmp.Password), []byte(user.Password)) == nil {
			user.ID = tmp.ID
		} else {
			result.Error = fmt.Errorf("InvalidCredentials")
		}
	}
	return result.Error
}

func (user *User) Get() error {
	result := db.Preload("Image").First(&user)
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
	result := db.Preload("Image").First(&service)
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

func (image *Image) AddUserImage() error {
	result := db.Save(image)
	return result.Error
}

func (image *Image) AddServiceImage(category ServiceCategory) {
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
	if message.RoomID == 0 {
		var room Room
		if message.SenderID < message.RecieverID {
			db.FirstOrCreate(&room, Room{User1ID: message.SenderID, User2ID: message.RecieverID})
		} else {
			db.FirstOrCreate(&room, Room{User1ID: message.RecieverID, User2ID: message.SenderID})
		}
		message.RoomID = room.ID
	}
	result := db.Create(message)
	return result.Error
}
func (message *Message) Update() error {
	result := db.Save(message)
	return result.Error
}

func Paginate(page int, page_size int) func(db *gorm.DB) *gorm.DB {
	return func(db *gorm.DB) *gorm.DB {
		offset := (page - 1) * page_size
		return db.Offset(offset).Limit(page_size)
	}
}

func (search *ServicesSearch) ServicesGet() {
	preloadFunc := func(db *gorm.DB) *gorm.DB {
		return db.Select("id", "username")
	}
	if search.Page < 0 {
		search.Page = 1
	}
	if search.PageSize <= 0 || search.PageSize > 100 {
		search.PageSize = 24
	}

	var records int64
	// TODO: Probably really inefficient to Preload like this
	query := db.Preload("Image").Preload("User", preloadFunc).Where("status = ?", SS_ACTIVE).Scopes(Paginate(search.Page, search.PageSize))
	if search.Query != "" && search.Category != "" {
		query.Where("category = ?", search.Category).Where("title ILIKE @query OR description ILIKE @query", sql.Named("query", fmt.Sprint("%", search.Query, "%"))).Find(&search.Services)
		db.Model(&Service{}).Where("category = ?", search.Category).Where("title ILIKE @query OR description ILIKE @query", sql.Named("query", fmt.Sprint("%", search.Query, "%"))).Count(&records)
	} else if search.Query != "" {
		query.Where("title ILIKE @query OR description ILIKE @query", sql.Named("query", fmt.Sprint("%", search.Query, "%"))).Find(&search.Services)
		db.Model(&Service{}).Where("title ILIKE @query OR description ILIKE @query", sql.Named("query", fmt.Sprint("%", search.Query, "%"))).Count(&records)
	} else if search.Category != "" {
		query.Where("category = ?", search.Category).Find(&search.Services)
		db.Model(&Service{}).Where("category = ?", search.Category).Count(&records)
	} else {
		query.Find(&search.Services)
		db.Model(&Service{}).Count(&records)
	}
	search.TotalPages = int(records) / search.PageSize
	if int(records)%search.PageSize > 0 {
		search.TotalPages += 1
	}
}

func UserServicesGet(user User, services *[]Service, all bool) {
	if all {
		db.Where("user_id = ?", user.ID).Find(&services)
	} else {
		db.Where("user_id = ? AND status = ?", user.ID, SS_ACTIVE).Find(&services)
	}
}

func UserLessonsGet(user User, lessons *[]Lesson, status LessonStatus) {
	preloadFunc := func(db *gorm.DB) *gorm.DB {
		return db.Select("id", "username")
	}
	if status != "" {
		db.Preload("Student", preloadFunc).Preload("Tutor", preloadFunc).Preload("Service").Where("tutor_id = ? OR student_id = ?", user.ID, user.ID).Where("status = ?", status).Order("datetime ASC").Find(&lessons)
	} else {
		db.Preload("Student", preloadFunc).Preload("Tutor", preloadFunc).Preload("Service").Where("tutor_id = ? OR student_id = ?", user.ID, user.ID).Where("status != ? AND status != ?", LS_CANCELLED, LS_EXPIRED).Order("datetime ASC").Find(&lessons)
	}
}

func OurLessonsGet(user User, other User, lessons *[]Lesson) {
	db.Where("(tutor_id = ? AND student_id = ?) OR (tutor_id = ? AND student_id = ?)", user.ID, other.ID, other.ID, user.ID).Where("status != ? AND status != ?", LS_CANCELLED, LS_EXPIRED).Find(&lessons)
}

func (room *Room) Get(userID uint, otherID uint) {
	if userID < otherID {
		db.Where("user1_id = ? AND user2_id = ?", userID, otherID).First(&room)
	} else {
		db.Where("user1_id = ? AND user2_id = ?", otherID, userID).First(&room)
	}
}

func MessagesGet(messages *[]Message, user User, other User) {
	var room Room
	room.Get(user.ID, other.ID)
	db.Model(Message{}).Joins("Lesson").Where("room_id = ?", room.ID).Order("ID asc").Find(&messages)
}

func RoomsGet(rooms *[]Room, user User) {
	preloadFunc := func(db *gorm.DB) *gorm.DB {
		return db.Select("id", "username")
	}

	var rooms1 []Room
	var rooms2 []Room
	db.Model(&Room{}).Preload("User2", preloadFunc).Where("user1_id = ?", user.ID).Find(&rooms1)
	db.Model(&Room{}).Preload("User1", preloadFunc).Where("user2_id = ?", user.ID).Find(&rooms2)
	*rooms = append(rooms1, rooms2...)
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
