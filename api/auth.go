package api

import (
	"context"
	"encoding/json"
	"io"
	"net/http"

	"github.com/mikey-boy/tutortime/config"
	"golang.org/x/oauth2"
)

type googleResponse struct {
	Sub      string `json:"sub"`
	Picture  string `json:"picture"`
	Email    string `json:"email"`
	Verified bool   `json:"email_verified"`
}

var google_client oauth2.Config

func RegisterOAuthClients(config config.OAuth) {
	google_client = oauth2.Config{
		ClientID:     config.GoogleClientID,
		ClientSecret: config.GoogleClientSecret,
		RedirectURL:  config.GoogleRedirectURL,
		Scopes:       []string{"email"},
		Endpoint: oauth2.Endpoint{
			AuthURL:  "https://accounts.google.com/o/oauth2/auth",
			TokenURL: "https://oauth2.googleapis.com/token",
		},
	}
}

func UserFromRequest(request http.Request) (User, bool) {
	user, ok := request.Context().Value(ContextUserKey).(User)
	return user, ok
}

func FetchSessionToken(endpointHandler func(writer http.ResponseWriter, request *http.Request)) http.HandlerFunc {
	return http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		cookies := request.CookiesNamed("Token")
		if len(cookies) > 0 {
			session := Session{UUID: cookies[0].Value}
			if err := session.Get(); err == nil && session.Valid() {
				// Add user to request context for later use
				user := User{ID: session.UserID}
				if err := user.Get(); err == nil {
					ctx := context.WithValue(request.Context(), ContextUserKey, user)
					request = request.WithContext(ctx)
				}
			}
		}
		endpointHandler(writer, request)
	})
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

// POST /api/sessiontoken
func AddSessionToken(writer http.ResponseWriter, request *http.Request) {
	var api_user APIUser
	if err := json.NewDecoder(request.Body).Decode(&api_user); err != nil {
		http.Error(writer, malformedJson.String(), http.StatusBadRequest)
		return
	}
	if api_user.Username == "" || api_user.Password == "" {
		http.Error(writer, insufficientRequest.String(), http.StatusBadRequest)
		return
	}

	user := User{Username: api_user.Username, Password: api_user.Password}
	if err := user.Login(); err != nil {
		http.Error(writer, failedLogin.String(), http.StatusUnauthorized)
		return
	}
	addSession(user.ID, writer)
}

// GET /api/user/authorize/google
func UserAuthorizeGoogle(writer http.ResponseWriter, request *http.Request) {
	state := request.URL.Query().Get("redirect")
	url := google_client.AuthCodeURL(state, oauth2.AccessTypeOffline)
	http.Redirect(writer, request, url, http.StatusFound)
}

// GET /api/user/callback/google
func UserCallbackGoogle(writer http.ResponseWriter, request *http.Request) {
	client := &http.Client{}
	ctx := context.Background()
	code := request.FormValue("code")
	redirect := request.FormValue("state")

	// Exchange the code provided by the user for an access token
	token, err := google_client.Exchange(ctx, code)
	if err != nil {
		http.Error(writer, unableToFetchAccessToken.String(), http.StatusUnauthorized)
		return
	}

	// Use the access token to retrieve the user's email address
	req, _ := http.NewRequest("GET", "https://openidconnect.googleapis.com/v1/userinfo", nil)
	req.Header.Add("Authorization", "Bearer "+token.AccessToken)
	resp, err := client.Do(req)
	if err != nil {
		http.Error(writer, unableToFetchUserDetails.String(), http.StatusUnauthorized)
		return
	}

	// Parse response from identity provider
	var user_details googleResponse
	body, _ := io.ReadAll(resp.Body)
	if err := json.Unmarshal(body, &user_details); err != nil {
		http.Error(writer, malformedJson.String(), http.StatusInternalServerError)
		return
	}

	// Create user if doesn't exist
	user := User{OAuthLogin: user_details.Email}
	user.addOrGetOAuthUser()
	addSession(user.ID, writer)

	// Redirect user if present, otherwise send them to Profile
	if redirect == "" {
		redirect = "/user/profile"
	}
	http.Redirect(writer, request, "/#"+redirect, http.StatusFound)
}
