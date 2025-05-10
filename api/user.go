package api

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/google/uuid"
	"golang.org/x/crypto/bcrypt"
)

type User struct {
	ID           uint
	Username     string `gorm:"unique,not null"`
	OAuthLogin   string `gorm:"unique,default:null"`
	Password     string `json:"-"`
	Availability string
	Description  string
	Minutes      int       `gorm:"default:60"`
	Image        Image     `json:",omitempty"`
	Services     []Service `json:",omitempty"`
	Sessions     []Session `json:",omitempty"`
	Lessons      []Session `json:",omitempty"`
}
type APIUser struct {
	Username string
	Password string
}

type Session struct {
	ID     uint
	UUID   string `gorm:"unique,not null"`
	UserID uint
	Expiry time.Time
}

type ContextKey string

const ContextUserKey ContextKey = "user"

func addSession(userID uint, writer http.ResponseWriter) {
	session := Session{UUID: uuid.NewString(), UserID: userID, Expiry: time.Now().Add(120 * time.Second)}
	if err := session.Add(); err == nil {
		http.SetCookie(writer, &http.Cookie{Name: "Token", Value: session.UUID, Path: "/"})
		http.SetCookie(writer, &http.Cookie{Name: "UserID", Value: fmt.Sprintf("%d", userID), Path: "/"})
	}
}

func transferMinutes(tutor *User, student *User, service *Service, lesson *Lesson, mins_transfered bool) {
	if lesson.Status == LS_ACCEPTED {
		student.Minutes -= int(lesson.Duration)
		student.Update()
	} else if lesson.Status == LS_CANCELLED && mins_transfered {
		student.Minutes += int(lesson.Duration)
		student.Update()
	} else if lesson.Status == LS_CONFIRMED {
		if lesson.ModifiedDuration != 0 {
			student.Minutes -= int(lesson.ModifiedDuration) - int(lesson.Duration)
			student.Update()

			tutor.Minutes += int(lesson.ModifiedDuration)
			service.Minutes += lesson.ModifiedDuration
		} else {
			tutor.Minutes += int(lesson.Duration)
			service.Minutes += lesson.Duration
		}
		tutor.Update()
		service.Lessons += 1
		service.Update()
	}
}

// GET /api/users/{id}
func GetUserProfile(writer http.ResponseWriter, request *http.Request) {
	id, err := strconv.ParseUint(request.PathValue("id"), 10, 0)
	if err != nil {
		http.Error(writer, malformedRequest.String(), http.StatusBadRequest)
		return
	}

	user := User{ID: uint(id)}
	if err := user.Get(); err != nil {
		http.Error(writer, userNotFound.String(), http.StatusNotFound)
		return
	}

	api_user := User{ID: uint(id), Username: user.Username, Description: user.Description, Availability: user.Availability, Image: user.Image}
	ret, _ := json.Marshal(api_user)
	writer.Write(ret)
}

// GET /api/users/me
func GetMyProfile(writer http.ResponseWriter, request *http.Request) {
	user, ok := UserFromRequest(*request)
	if !ok {
		http.Error(writer, invalidSessionToken.String(), http.StatusUnauthorized)
		return
	}
	if err := user.Get(); err != nil {
		http.Error(writer, userNotFound.String(), http.StatusNotFound)
		return
	}

	ret, _ := json.Marshal(user)
	writer.Write(ret)
}

// PUT /api/users/me
func UpdateMyProfile(writer http.ResponseWriter, request *http.Request) {
	user, ok := UserFromRequest(*request)
	if !ok {
		http.Error(writer, invalidSessionToken.String(), http.StatusUnauthorized)
		return
	}

	if request.FormValue("username") != "" {
		user.Username = request.FormValue("username")
		user.Description = request.FormValue("description")
		user.Availability = request.FormValue("availability")

		file, file_header, formErr := request.FormFile("image")
		if formErr == nil {
			image := Image{}
			image.Upload(file, file_header.Filename)
			// Change image only if upload successful
			if image.Name != "" {
				user.Image = image
			}
		}
		user.Update()
	}

	ret, _ := json.Marshal(user)
	writer.Write(ret)
}

// POST /api/users
func AddUser(writer http.ResponseWriter, request *http.Request) {
	var api_user APIUser
	if err := json.NewDecoder(request.Body).Decode(&api_user); err != nil {
		http.Error(writer, malformedJson.String(), http.StatusBadRequest)
		return
	}
	if api_user.Username == "" || api_user.Password == "" {
		http.Error(writer, insufficientRequest.String(), http.StatusBadRequest)
		return
	}

	hashed, _ := bcrypt.GenerateFromPassword([]byte(api_user.Password), bcrypt.DefaultCost)
	user := User{Username: api_user.Username, Password: string(hashed)}
	user.Image = Image{Name: "tux", Path: "/default/img/tux.png"}
	if err := user.Add(); err != nil {
		http.Error(writer, usernameTaken.String(), http.StatusBadRequest)
		return
	}
	addSession(user.ID, writer)
}

func (user *User) addOrGetOAuthUser() {
	if err := user.Login(); err == nil {
		return
	}

	user.Username = uuid.NewString()
	user.Image = Image{Name: "tux", Path: "/default/img/tux.png"}
	user.Add()

	user.Username = fmt.Sprintf("User_%d", user.ID)
	user.Update()
}
