package api

import (
	"encoding/json"
	"net/http"
	"strconv"
)

// GET /api/services
func GetServices(w http.ResponseWriter, r *http.Request) {
	var services []Service
	db.Find(&services)
	ret, _ := json.Marshal(services)
	w.Write(ret)
}

// POST /api/services
func AddService(w http.ResponseWriter, r *http.Request) {
	title := r.PostFormValue("title")
	description := r.PostFormValue("description")
	category := stringToCategory[r.PostFormValue("category")]

	service := Service{Title: title, Description: description, Category: category, UserID: 1}
	err := service.Add()
	if err != nil {
		w.Write([]byte("{error:'Service already exist'}"))
	} else {
		ret, _ := json.Marshal(service)
		w.Write(ret)
	}
}

// PUT /api/services/{id}
func UpdateService(w http.ResponseWriter, r *http.Request) {
	id, _ := strconv.ParseUint(r.PostFormValue("id"), 10, 0)

	service := Service{ID: uint(id)}
	service.Get()
	if r.PostFormValue("title") != "" {
		service.Title = r.PostFormValue("title")
	}
	if r.PostFormValue("description") != "" {
		service.Description = r.PostFormValue("description")
	}
	if r.PostFormValue("category") != "" {
		service.Category = stringToCategory[r.PostFormValue("category")]
	}

	err := service.Update()
	if err != nil {
		w.Write([]byte("{error:'Service already exist'}"))
	} else {
		ret, _ := json.Marshal(service)
		w.Write(ret)
	}
}
