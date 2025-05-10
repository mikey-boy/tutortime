package config

type Config struct {
	Webserver Webserver `yaml:"webserver"`
	Database  Database  `yaml:"database"`
	OAuth     OAuth     `yaml:"oauth"`
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
type OAuth struct {
	GoogleClientID     string `yaml:"google_client_id"`
	GoogleClientSecret string `yaml:"google_client_secret"`
	GoogleRedirectURL  string `yaml:"google_redirect_url"`
}
