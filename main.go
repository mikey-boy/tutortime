package main

import (
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/mikey-boy/tutortime/api"
	"gopkg.in/yaml.v3"
)

type Config struct {
	Webserver Webserver `yaml:"webserver"`
	Database  Database  `yaml:"database"`
}
type Webserver struct {
	Host string `yaml:"host"`
	Port uint   `yaml:"port"`
}
type Database struct {
	Host     string `yaml:"host"`
	Port     uint16 `yaml:"port"`
	User     string `yaml:"user"`
	Password string `yaml:"password"`
	Dbname   string `yaml:"dbname"`
}

func main() {
	var err error

	// Read the config file
	data, err := os.ReadFile("config.yaml")
	if err != nil {
		log.Fatalf("Error reading the config file: %v", err)
	}
	// And parse it's fields
	var config Config
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

	// The implementation of getFrontendAssets() will be filled in by either the code
	// in fs_dev.go or fs_prod.go, depending on whether the `prod` build tag is used
	frontend := getFrontendAssets()

	// Requests to the root are served frontend Vue JS
	mux := http.NewServeMux()
	mux.Handle("/", http.FileServer(http.FS(frontend)))

	// All other requests are served by the backend API
	// mux.HandleFunc("GET /api/users/{id}", api.GetUser)
	mux.HandleFunc("POST /api/users", api.AddUser)
	mux.HandleFunc("POST /api/accesstoken", api.AddAccessToken)

	mux.HandleFunc("GET /api/services", api.GetServices)
	mux.HandleFunc("GET /api/services/{id}", api.GetService)
	mux.HandleFunc("POST /api/services", api.AddService)
	mux.HandleFunc("PUT /api/services/{id}", api.UpdateService)

	addr := fmt.Sprintf("%s:%d", config.Webserver.Host, config.Webserver.Port)
	fmt.Printf("Serving the application on http://%s\n", addr)
	log.Fatal(http.ListenAndServe(addr, mux))
}
