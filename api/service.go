package api

import (
	"encoding/json"
	"net/http"
	"strconv"

	"gorm.io/gorm"
)

// GET /api/services
func GetServices(w http.ResponseWriter, r *http.Request) {
	var services []Service
	query := r.URL.Query().Get("query")
	category := r.URL.Query().Get("category")
	ServicesGet(&services, query, stringToCategory[category])
	ret, _ := json.Marshal(services)
	w.Write(ret)
}

// GET /api/services/{id}
func GetService(w http.ResponseWriter, r *http.Request) {
	id, _ := strconv.ParseUint(r.PathValue("id"), 10, 0)
	service := Service{ID: uint(id)}
	if err := service.Get(); err == gorm.ErrRecordNotFound {
		http.Error(w, resourceNotFound.String(), http.StatusNotFound)
		return
	}

	ret, _ := json.Marshal(service)
	w.Write(ret)
}

// POST /api/services
func AddService(w http.ResponseWriter, r *http.Request) {
	err := r.ParseMultipartForm(10 << 20) // 10 MB limit
	if err != nil {
		http.Error(w, "error", http.StatusBadRequest)
		return
	}

	image := Image{}
	category := stringToCategory[r.FormValue("category")]
	service := Service{Title: r.FormValue("title"), Description: r.FormValue("description"), Category: category}
	service.UserID = 1

	file, file_header, formErr := r.FormFile("image")
	if formErr == nil {
		image.Upload(file, file_header.Filename)
	}
	if image.Name == "" {
		image.Add(category) // Add default image if upload fails or user does not specify file
	}
	service.Image = image

	if err := service.Add(); err != nil {
		http.Error(w, "error", http.StatusForbidden)
		return
	}

	ret, _ := json.Marshal(service)
	w.Write(ret)
}

// PUT /api/services/{id}
func UpdateService(w http.ResponseWriter, r *http.Request) {
	id, _ := strconv.ParseUint(r.PathValue("id"), 10, 0)

	// Verify that the user can modify this service

	service := Service{ID: uint(id)}
	if err := service.Get(); err == gorm.ErrRecordNotFound {
		http.Error(w, resourceNotFound.String(), http.StatusNotFound)
		return
	}

	if r.FormValue("title") != "" {
		service.Title = r.FormValue("title")
		service.Description = r.FormValue("description")
		service.Category = stringToCategory[r.FormValue("category")]

		file, file_header, formErr := r.FormFile("image")
		if formErr == nil {
			service.Image.Delete()
			service.Image.Upload(file, file_header.Filename)
		}
		if service.Image.Name == "" || file == nil {
			service.Image.Add(service.Category) // Add default image if upload fails or user does not specify file
		}
	} else {
		var edited Service
		if err := json.NewDecoder(r.Body).Decode(&edited); err != nil {
			http.Error(w, "error", http.StatusBadRequest)
			return
		}
		if edited.Status != "" {
			service.Status = edited.Status
		}
	}

	err := service.Update()
	if err != nil {
		http.Error(w, "error", http.StatusForbidden)
		return
	} else {
		ret, _ := json.Marshal(service)
		w.Write(ret)
	}
}
