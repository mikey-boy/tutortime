package api

import (
	"context"
	"encoding/json"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/google/uuid"
)

type User struct {
	ID           uint
	Username     string    `gorm:"unique,not null"`
	Password     string    `gorm:"not null" json:"-"`
	Description  string    `json:",omitempty"`
	Availability uint      `gorm:"default:0" json:",omitempty"`
	Minutes      uint      `gorm:"default:60" json:",omitempty"`
	Image        Image     `json:",omitempty"`
	Services     []Service `json:",omitempty"`
	Sessions     []Session `json:",omitempty"`
	Lessons      []Session `json:",omitempty"`
}

type Session struct {
	ID     uint
	UUID   string `gorm:"unique,not null"`
	UserID uint
	Expiry time.Time
}

type ContextKey string

const ContextUserKey ContextKey = "user"

// GET /users/{id}
func GetUser(writer http.ResponseWriter, request *http.Request) {
	path := strings.Split(request.URL.Path, "/")
	id, err := strconv.ParseUint(path[2], 10, 0)
	if err != nil {
		http.Error(writer, malformedRequest.String(), http.StatusBadRequest)
		return
	}

	user := User{ID: uint(id)}
	if err := user.Get(); err != nil {
		http.Error(writer, userNotFound.String(), http.StatusNotFound)
		return
	}

	ret, _ := json.Marshal(user)
	writer.Write(ret)
}

// POST /api/users
func AddUser(writer http.ResponseWriter, request *http.Request) {
	var user User

	if err := json.NewDecoder(request.Body).Decode(&user); err != nil {
		http.Error(writer, malformedJson.String(), http.StatusBadRequest)
		return
	}
	if err := user.Add(); err != nil {
		http.Error(writer, usernameTaken.String(), http.StatusBadRequest)
		return
	}

	session := Session{UUID: uuid.NewString(), UserID: user.ID, Expiry: time.Now().Add(120 * time.Second)}
	if err := session.Add(); err == nil {
		http.SetCookie(writer, &http.Cookie{Name: "Token", Value: session.UUID, Path: "/"})
	}
}

func UpdateUser(writer http.ResponseWriter, request *http.Request) {
}

func DeleteUser(writer http.ResponseWriter, request *http.Request) {
}

// POST /api/sessiontoken
func AddSessionToken(writer http.ResponseWriter, request *http.Request) {
	var user User

	if err := json.NewDecoder(request.Body).Decode(&user); err != nil {
		http.Error(writer, malformedJson.String(), http.StatusBadRequest)
		return
	}
	if err := user.Login(); err != nil {
		http.Error(writer, failedLogin.String(), http.StatusUnauthorized)
		return
	}

	session := Session{UUID: uuid.NewString(), UserID: user.ID, Expiry: time.Now().Add(120 * time.Second)}
	if err := session.Add(); err == nil {
		http.SetCookie(writer, &http.Cookie{Name: "Token", Value: session.UUID, Path: "/"})
	}
}

func UserFromRequest(request http.Request) (User, bool) {
	user, ok := request.Context().Value(ContextUserKey).(User)
	return user, ok
}

func ValidateSessionToken(endpointHandler func(writer http.ResponseWriter, request *http.Request)) http.HandlerFunc {
	return http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		cookies := request.CookiesNamed("Token")
		if len(cookies) > 0 {
			session := Session{UUID: cookies[0].Value}
			if err := session.Get(); err != nil {
				http.Error(writer, invalidSessionToken.String(), http.StatusUnauthorized)
				return
			}

			if session.Valid() {
				// Add user to request context for later use
				user := User{ID: session.UserID}
				if err := user.Get(); err == nil {
					ctx := context.WithValue(request.Context(), ContextUserKey, user)
					request = request.WithContext(ctx)
					endpointHandler(writer, request)
				}
			} else {
				http.Error(writer, expiredSessionToken.String(), http.StatusUnauthorized)
				return
			}
		} else {
			http.Error(writer, missingSessionToken.String(), http.StatusUnauthorized)
			return
		}
	})
}
