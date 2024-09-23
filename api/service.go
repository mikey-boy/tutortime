package api

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"

	"gorm.io/gorm"
)

// GET /api/services
func GetServices(w http.ResponseWriter, r *http.Request) {
	var services []Service
	query := r.URL.Query().Get("query")
	category := r.URL.Query().Get("category")

	if query != "" && category != "" {
		db.Where("title ILIKE @query OR description ILIKE @query", sql.Named("query", fmt.Sprint("%", query, "%"))).Where("category = ?", category).Find(&services)
	} else if query != "" {
		db.Where("title ILIKE @query OR description ILIKE @query", sql.Named("query", fmt.Sprint("%", query, "%"))).Find(&services)
	} else if category != "" {
		db.Where("category = ?", category).Find(&services)
	} else {
		db.Preload("Image").Find(&services)
	}

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

	db.Find(&service)
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

	title := r.FormValue("title")
	description := r.FormValue("description")
	category := stringToCategory[r.FormValue("category")]
	service := Service{Title: title, Description: description, Category: category}
	service.UserID = 1

	image := Image{}
	var uploadErr error = nil
	file, file_header, formErr := r.FormFile("image")
	if formErr == nil {
		image.Name = file_header.Filename
		uploadErr = image.Upload(file)
	}
	if uploadErr != nil || file == nil {
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

	fmt.Printf("%+v", service)
	var edited Service
	if err := json.NewDecoder(r.Body).Decode(&edited); err != nil {
		http.Error(w, "error", http.StatusBadRequest)
		return
	}
	if edited.Title != "" {
		service.Title = edited.Title
	}
	if edited.Description != "" {
		service.Description = edited.Description
	}
	if edited.Category != "" {
		service.Category = edited.Category
	}
	if edited.Status != "" {
		service.Status = edited.Status
	}

	fmt.Printf("Modified service: %+v\n", service)
	err := service.Update()
	if err != nil {
		http.Error(w, "error", http.StatusForbidden)
		return
	} else {
		ret, _ := json.Marshal(service)
		w.Write(ret)
	}
}
