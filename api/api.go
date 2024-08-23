package api

import "fmt"

type ApiError struct {
	Title   string
	Details string
}

func (err ApiError) String() string {
	return fmt.Sprintf(`"title": "%s", "details": "%s"`, err.Title, err.Details)
}

var resourceNotFound = ApiError{
	Title:   "Resource not found",
	Details: "The resource you were looking for was not found",
}
