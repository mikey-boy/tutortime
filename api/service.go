package api

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"

	"gorm.io/gorm"
)

// GET /api/services
func GetServices(w http.ResponseWriter, r *http.Request) {
	var services []Service

	// Return services that are owned by the user and not cancelled

	db.Find(&services)
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
	var service Service

	if err := json.NewDecoder(r.Body).Decode(&service); err != nil {
		http.Error(w, "error", http.StatusBadRequest)
		return
	}

	fmt.Printf("Added service: %+v\n", service)
	service.UserID = 1

	if err := service.Add(); err != nil {
		http.Error(w, "error", http.StatusForbidden)
		return
	} else {
		ret, _ := json.Marshal(service)
		w.Write(ret)
	}
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
