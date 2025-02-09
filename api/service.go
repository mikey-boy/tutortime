package api

import (
	"encoding/json"
	"net/http"
	"strconv"

	"gorm.io/gorm"
)

type Service struct {
	ID          uint
	Title       string          `gorm:"not null"`
	Description string          `gorm:"not null"`
	Category    ServiceCategory `gorm:"default:'other'"`
	Status      ServiceStatus   `gorm:"default:'active'"`
	Minutes     uint            `gorm:"default:0"`
	Image       Image
	UserID      uint
	User        User `gorm:"foreignKey:UserID"`
}

type ServiceStatus string
type ServiceCategory string

const (
	SS_ACTIVE    ServiceStatus = "active"
	SS_PAUSED    ServiceStatus = "paused"
	SS_CANCELLED ServiceStatus = "cancelled"
)

const (
	SC_LANGUAGE ServiceCategory = "language"
	SC_MUSIC    ServiceCategory = "music"
	SC_SOFTWARE ServiceCategory = "software"
	SC_WELLNESS ServiceCategory = "wellness"
	SC_OTHER    ServiceCategory = "other"
)

var stringToStatus = map[string]ServiceStatus{
	"active":    SS_ACTIVE,
	"paused":    SS_PAUSED,
	"cancelled": SS_CANCELLED,
}

var stringToCategory = map[string]ServiceCategory{
	"language": SC_LANGUAGE,
	"music":    SC_MUSIC,
	"software": SC_SOFTWARE,
	"wellness": SC_WELLNESS,
	"other":    SC_OTHER,
}

// GET /api/services
func GetServices(writer http.ResponseWriter, request *http.Request) {
	var services []Service
	query := request.URL.Query().Get("query")
	category := request.URL.Query().Get("category")
	ServicesGet(&services, query, stringToCategory[category])
	ret, _ := json.Marshal(services)
	writer.Write(ret)
}

// GET /api/services/{id}
func GetService(writer http.ResponseWriter, request *http.Request) {
	id, _ := strconv.ParseUint(request.PathValue("id"), 10, 0)
	service := Service{ID: uint(id)}
	if err := service.Get(); err == gorm.ErrRecordNotFound {
		http.Error(writer, resourceNotFound.String(), http.StatusNotFound)
		return
	}

	ret, _ := json.Marshal(service)
	writer.Write(ret)
}

// GET /api/users/{id}/services/
func GetUserServices(writer http.ResponseWriter, request *http.Request) {
	var services []Service
	id, _ := strconv.ParseUint(request.PathValue("id"), 10, 0)
	user := User{ID: uint(id)}
	UserServicesGet(user, &services, false)
	ret, _ := json.Marshal(services)
	writer.Write(ret)
}

// GET /api/users/me/services/
func GetMyServices(writer http.ResponseWriter, request *http.Request) {
	var services []Service
	user, ok := UserFromRequest(*request)
	if !ok {
		http.Error(writer, invalidSessionToken.String(), http.StatusUnauthorized)
		return
	}
	UserServicesGet(user, &services, true)
	ret, _ := json.Marshal(services)
	writer.Write(ret)
}

// POST /api/services
func AddService(writer http.ResponseWriter, request *http.Request) {
	err := request.ParseMultipartForm(10 << 20) // 10 MB limit
	if err != nil {
		http.Error(writer, "error", http.StatusBadRequest)
		return
	}

	user, ok := UserFromRequest(*request)
	if !ok {
		http.Error(writer, wrongSessionToken.String(), http.StatusUnauthorized)
		return
	}

	image := Image{}
	category := stringToCategory[request.FormValue("category")]
	service := Service{UserID: user.ID, Title: request.FormValue("title"), Description: request.FormValue("description"), Category: category}
	file, file_header, formErr := request.FormFile("image")
	if formErr == nil {
		image.Upload(file, file_header.Filename)
	}
	if image.Name == "" {
		image.AddServiceImage(category) // Add default image if upload fails or user does not specify file
	}
	service.Image = image

	if err := service.Add(); err != nil {
		http.Error(writer, "error", http.StatusForbidden)
		return
	}

	ret, _ := json.Marshal(service)
	writer.Write(ret)
}

// PUT /api/services/{id}
func UpdateService(writer http.ResponseWriter, request *http.Request) {
	id, _ := strconv.ParseUint(request.PathValue("id"), 10, 0)
	service := Service{ID: uint(id)}

	// Verify service exists
	if err := service.Get(); err == gorm.ErrRecordNotFound {
		http.Error(writer, resourceNotFound.String(), http.StatusNotFound)
		return
	}

	// Verify user can modify this service
	if user, ok := UserFromRequest(*request); !ok || service.UserID != user.ID {
		http.Error(writer, wrongSessionToken.String(), http.StatusUnauthorized)
		return
	}

	if request.FormValue("title") != "" {
		service.Title = request.FormValue("title")
		service.Description = request.FormValue("description")
		service.Category = stringToCategory[request.FormValue("category")]

		file, file_header, formErr := request.FormFile("image")
		if formErr == nil {
			service.Image.Delete()
			service.Image.Upload(file, file_header.Filename)
		}
		if service.Image.Name == "" || file == nil {
			service.Image.AddServiceImage(service.Category) // Add default image if upload fails or user does not specify file
		}
	} else {
		var edited Service
		if err := json.NewDecoder(request.Body).Decode(&edited); err != nil {
			http.Error(writer, "error", http.StatusBadRequest)
			return
		}
		if edited.Status != "" {
			service.Status = edited.Status
		}
	}

	err := service.Update()
	if err != nil {
		http.Error(writer, "error", http.StatusForbidden)
		return
	} else {
		ret, _ := json.Marshal(service)
		writer.Write(ret)
	}
}
