package api

type Image struct {
	ID        uint
	Name      string `gorm:"not null"`
	Path      string `gorm:"unique,not null"`
	OSPath    string `json:"-"`
	ServiceID *uint
	UserID    *uint
}
