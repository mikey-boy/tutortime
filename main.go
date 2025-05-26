package main

import (
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/mikey-boy/tutortime/api"
	"github.com/mikey-boy/tutortime/config"
	"gopkg.in/yaml.v3"
)

func main() {
	var err error

	// Read the config file
	data, err := os.ReadFile("config.yaml")
	if err != nil {
		log.Fatalf("Error reading the config file: %v", err)
	}
	// And parse it's fields
	var config config.Config
	err = yaml.Unmarshal(data, &config)
	if err != nil {
		log.Fatalf("Error parsing the config file: %v", err)
	}

	api.CreateConnection(
		config.Database.Host,
		config.Database.User,
		config.Database.Password,
		config.Database.Dbname,
		config.Database.Port,
	)
	api.RegisterCrons()
	api.RegisterOAuthClients(config.OAuth)
	api.CreateHub()
	go api.RunHub()

	// The implementation of getFrontendAssets() will be filled in by either the code
	// in fs_dev.go or fs_prod.go, depending on whether the `prod` build tag is used
	frontend := getFrontendAssets()

	// Requests to the root are served frontend Vue JS
	mux := http.NewServeMux()
	mux.Handle("/", http.FileServer(http.FS(frontend)))
	mux.Handle("GET /img/{uuid}", http.FileServer(http.Dir("./instance")))

	// Requests for websockets connections
	mux.HandleFunc("/ws", api.ValidateSessionToken(api.ServeWs))

	// All other requests to the API
	mux.HandleFunc("POST /api/users", api.AddUser)
	mux.HandleFunc("GET /api/users/{id}", api.GetUserProfile)
	mux.HandleFunc("GET /api/users/{id}/services", api.GetUserServices)
	mux.HandleFunc("GET /api/users/{id}/messages", api.ValidateSessionToken(api.GetOurMessages))
	mux.HandleFunc("GET /api/users/{id}/lessons", api.ValidateSessionToken(api.GetOurLessons))
	mux.HandleFunc("GET /api/users/me", api.ValidateSessionToken(api.GetMyProfile))
	mux.HandleFunc("PUT /api/users/me", api.ValidateSessionToken(api.UpdateMyProfile))
	mux.HandleFunc("GET /api/users/me/services", api.ValidateSessionToken(api.GetMyServices))
	mux.HandleFunc("GET /api/users/me/lessons", api.ValidateSessionToken(api.GetMyLessons))

	mux.HandleFunc("GET /api/user/authorize/google", api.UserAuthorizeGoogle)
	mux.HandleFunc("GET /api/user/callback/google", api.UserCallbackGoogle)
	mux.HandleFunc("POST /api/sessiontoken", api.AddSessionToken)
	mux.HandleFunc("GET /api/rooms", api.ValidateSessionToken(api.GetRooms))

	mux.HandleFunc("GET /api/services", api.GetServices)
	mux.HandleFunc("POST /api/services", api.ValidateSessionToken(api.AddService))
	mux.HandleFunc("GET /api/services/{id}", api.GetService)
	mux.HandleFunc("PUT /api/services/{id}", api.ValidateSessionToken(api.UpdateService))

	// Configure logging
	newLogger()
	defer api.LogClose()
	api.LogRotate()

	// Log every request, fetch session token on every request
	var handler http.Handler = mux
	handler = api.LogRequestHandler(handler)
	handler = api.FetchSessionToken(handler)

	// Start serving requests
	addr := fmt.Sprintf("%s:%d", config.Webserver.Host, config.Webserver.Port)
	fmt.Printf("Serving the application on http://%s\n", addr)
	log.Fatal(http.ListenAndServe(addr, handler))
}
