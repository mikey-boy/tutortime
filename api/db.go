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

type ServiceStatus string
type ServiceCategory string

const (
	Active    ServiceStatus = "active"
	Paused    ServiceStatus = "paused"
	Cancelled ServiceStatus = "cancelled"
)

const (
	Language ServiceCategory = "language"
	Music    ServiceCategory = "music"
	Software ServiceCategory = "software"
	Wellness ServiceCategory = "wellness"
	Other    ServiceCategory = "other"
)

var stringToStatus = map[string]ServiceStatus{
	"active":    Active,
	"paused":    Paused,
	"cancelled": Cancelled,
}

var stringToCategory = map[string]ServiceCategory{
	"language": Language,
	"music":    Music,
	"software": Software,
	"wellness": Wellness,
	"other":    Other,
}

type User struct {
	ID           uint
	Username     string `gorm:"unique,not null"`
	Password     string `gorm:"not null"`
	Description  string `gorm:"not null"`
	Availability uint   `gorm:"default:0"`
	Minutes      uint   `gorm:"default:60"`
	Image        Image
	Services     []Service
}

type Service struct {
	ID          uint
	Title       string          `gorm:"not null"`
	Description string          `gorm:"not null"`
	Category    ServiceCategory `gorm:"default:'other'"`
	Status      ServiceStatus   `gorm:"default:'active'"`
	Minutes     uint            `gorm:"default:0"`
	Image       Image
	UserID      uint
}

type Image struct {
	ID        uint
	Name      string `gorm:"not null"`
	Path      string `gorm:"unique,not null"`
	OSPath    string
	ServiceID *uint
	UserID    *uint
}

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
	fmt.Printf("%v\n", user)
	return result.Error
}

func (user *User) Get() error {
	result := db.First(&user)
	return result.Error
}

func (service *Service) Add() error {
	result := db.Create(service)
	fmt.Printf("%+v\n", service)
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
	if query != "" && category != "" {
		db.Preload("Image").Where("title ILIKE @query OR description ILIKE @query", sql.Named("query", fmt.Sprint("%", query, "%"))).Where("category = ?", category).Find(&services)
	} else if query != "" {
		db.Preload("Image").Where("title ILIKE @query OR description ILIKE @query", sql.Named("query", fmt.Sprint("%", query, "%"))).Find(&services)
	} else if category != "" {
		db.Preload("Image").Where("category = ?", category).Find(&services)
	} else {
		db.Preload("Image").Find(&services)
	}
}

func createTables() {
	db.AutoMigrate(&User{})
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
