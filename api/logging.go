package api

import (
	"fmt"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/felixge/httpsnoop"
)

var (
	logger Logger
)

type Logger struct {
	file   *os.File
	mutex  sync.Mutex
	stdout bool
}

type RequestInfo struct {
	username     string
	method       string
	uri          string
	referer      string
	ip           string
	userAgent    string
	responseCode int
	responseSize int64
}

func NewLogger(stdout bool) {
	logger = Logger{stdout: stdout}
}

func LogRotate() {
	// Ensure log directory exists
	if logger.stdout {
		logger.file = os.Stdout
	} else {
		os.MkdirAll("instance/log", 0750)
		logger.mutex.Lock()
		logger.file.Close()
		now := time.Now()
		path := fmt.Sprintf("instance/log/%s.txt", now.Format("2006-01-02"))
		logger.file, _ = os.OpenFile(path, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0644)
		logger.mutex.Unlock()
	}
}

func LogClose() {
	logger.file.Close()
}

func LogRequestHandler(handler http.Handler) http.Handler {
	fn := func(writer http.ResponseWriter, request *http.Request) {
		username := "-"
		if user, present := UserFromRequest(*request); present {
			username = user.Username
		}

		// gather information about request and log it
		metrics := httpsnoop.CaptureMetrics(handler, writer, request)
		info := &RequestInfo{
			username:     username,
			method:       request.Method,
			uri:          request.URL.String(),
			referer:      request.Header.Get("Referer"),
			ip:           getIpAddress(request),
			userAgent:    request.Header.Get("User-Agent"),
			responseCode: metrics.Code,
			responseSize: metrics.Written,
		}
		logger.logHTTPReq(info)
	}

	// http.HandlerFunc wraps a function so that it
	// implements http.Handler interface
	return http.HandlerFunc(fn)
}

func getIpAddress(request *http.Request) string {
	header_real_ip := request.Header.Get("X-Real-Ip")
	if header_real_ip == "" {
		idx := strings.LastIndex(request.RemoteAddr, ":")
		if idx == -1 {
			return request.RemoteAddr
		}
		return request.RemoteAddr[:idx]
	}
	return header_real_ip
}

func (logger *Logger) logHTTPReq(info *RequestInfo) {
	logger.mutex.Lock()
	log := fmt.Sprintf("%s %s [%s] \"%s %s\" %d %d \"%s\"\n", info.ip, info.username, time.Now().Format(time.RFC3339), info.method, info.uri, info.responseCode, info.responseSize, info.userAgent)
	fmt.Fprint(logger.file, log)
	logger.mutex.Unlock()
}
