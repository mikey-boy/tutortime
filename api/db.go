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

func ServicesGet(services *[]Service, query string, category ServiceCategory) {
	preloadFunc := func(db *gorm.DB) *gorm.DB {
		return db.Select("id", "username")
	}

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

func createTables() {
	db.AutoMigrate(&User{})
	db.AutoMigrate(&Session{})
	db.AutoMigrate(&Service{})
	db.AutoMigrate(&Image{})
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
