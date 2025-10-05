package api

import "fmt"

type ApiError struct {
	Error   string
	Details string
}

func (err ApiError) String() string {
	return fmt.Sprintf(`{"error": "%s", "details": "%s"}`, err.Error, err.Details)
}

// Generic errors

var malformedJson = ApiError{
	Error:   "Malformed JSON provided",
	Details: "The user supplied a malformed JSON object that the server could not parse",
}
var malformedRequest = ApiError{
	Error:   "Malformed request",
	Details: "The request to the server contained malformed data",
}
var insufficientRequest = ApiError{
	Error:   "Insufficient request",
	Details: "The request to the server did not contain enough information",
}

// User errors

var userNotFound = ApiError{
	Error:   "User not found",
	Details: "The user you were looking for was not found",
}
var usernameTaken = ApiError{
	Error:   "Unable to create account",
	Details: "The username you have chosen is already taken",
}
var failedLogin = ApiError{
	Error:   "User not found",
	Details: "The username/password combination you have supplied is incorrect",
}
var failedLoginServer = ApiError{
	Error:   "User not found",
	Details: "The server encountered an issue when logging you in",
}
var missingSessionToken = ApiError{
	Error:   "Action not permitted",
	Details: "You are unauthorized due to missing session token",
}
var invalidSessionToken = ApiError{
	Error:   "Action not permitted",
	Details: "You are unauthorized due to invalid session token",
}
var expiredSessionToken = ApiError{
	Error:   "Action not permitted",
	Details: "You are unauthorized due to an expired session token",
}
var wrongSessionToken = ApiError{
	Error:   "Action not permitted",
	Details: "You are unauthorized due to using the wrong session token",
}

// OAuth errors

var unableToFetchAccessToken = ApiError{
	Error:   "OAuth2 error",
	Details: "Unable to fetch OAuth Access token using code supplied by user",
}
var unableToFetchUserDetails = ApiError{
	Error:   "OAuth2 error",
	Details: "Unable to fetch user details from identity provider using access token",
}

// Server errors

var resourceNotFound = ApiError{
	Error:   "Resource not found",
	Details: "The resource you were looking for was not found",
}
