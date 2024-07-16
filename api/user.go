package api

import (
	"encoding/json"
	"net/http"
	"strconv"
	"strings"
)

// GET /users/{id}
func GetUser(w http.ResponseWriter, r *http.Request) {
	path := strings.Split(r.URL.Path, "/")
	id, err := strconv.ParseUint(path[2], 10, 0)
	if err != nil {
		w.Write([]byte("{}"))
		return
	}

	user_struct := User{ID: uint(id)}
	user := user_struct.Get()

	ret, _ := json.Marshal(user)
	w.Write(ret)
}

// POST /api/users
func AddUser(w http.ResponseWriter, r *http.Request) {
	username := r.PostFormValue("username")
	password := r.PostFormValue("password")

	user := User{Username: username, Password: password}
	err := user.Add()

	if err != nil {
		w.Write([]byte("{error:'Username already exist'}"))
	} else {
		ret, _ := json.Marshal(user)
		w.Write(ret)
	}
}

func UpdateUser(w http.ResponseWriter, r *http.Request) {
}

func DeleteUser(w http.ResponseWriter, r *http.Request) {
}

// POST /api/accesstoken
func AddAccessToken(w http.ResponseWriter, r *http.Request) {
	username := r.PostFormValue("username")
	password := r.PostFormValue("password")

	user := User{Username: username, Password: password}
	err := user.Get()

	if err != nil {
		w.Write([]byte("{error:'Login failed'}"))
	} else {
		ret, _ := json.Marshal(user)
		w.Write(ret)
	}
}
