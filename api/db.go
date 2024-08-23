package api

import (
	"encoding/json"
	"fmt"
	"log"

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
	Username     string `gorm:"unique"`
	Password     string
	Description  string
	Availability uint `gorm:"default:0"`
	Image_Path   string
	Minutes      uint `gorm:"default:60"`
	Services     []Service
}

type Service struct {
	ID          uint
	Title       string
	Description string
	Category    ServiceCategory `gorm:"default:'other'"`
	Status      ServiceStatus   `gorm:"default:'active'"`
	Minutes     uint            `gorm:"default:0"`
	UserID      uint
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
	result := db.First(&service)
	return result.Error
}

func (service *Service) Update() error {
	result := db.Save(service)
	return result.Error
}

func createTables() {
	db.AutoMigrate(&User{})
	db.AutoMigrate(&Service{})
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
