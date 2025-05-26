//go:build !prod
// +build !prod

package main

import (
	"io/fs"
	"os"

	"github.com/mikey-boy/tutortime/api"
)

func getFrontendAssets() fs.FS {
	return os.DirFS("frontend/dist")
}

func newLogger() {
	api.NewLogger(true)
}
