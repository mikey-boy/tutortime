package api

import (
	"encoding/json"
	"net/http"
)

// POST /api/services
func AddService(w http.ResponseWriter, r *http.Request) {
	title := r.PostFormValue("title")
	description := r.PostFormValue("description")
	category, ok := stringToCategory[r.PostFormValue("category")]
	if !ok {
		w.Write([]byte("{error:'Service category does not exist'}"))
	}

	service := Service{Title: title, Description: description, Category: category, UserID: 1}
	err := service.Add()
	if err != nil {
		w.Write([]byte("{error:'Service already exist'}"))
	} else {
		ret, _ := json.Marshal(service)
		w.Write(ret)
	}
}

// GET /api/services
func GetServices(w http.ResponseWriter, r *http.Request) {
	var services []Service
	db.Find(&services)
	ret, _ := json.Marshal(services)
	w.Write(ret)
}
