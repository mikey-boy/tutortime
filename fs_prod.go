//go:build prod
// +build prod

package main

import (
	"embed"
	"io/fs"

	"github.com/mikey-boy/tutortime/api"
)

//go:embed frontend/dist
var embedFrontend embed.FS

func getFrontendAssets() fs.FS {
	f, err := fs.Sub(embedFrontend, "frontend/dist")
	if err != nil {
		panic(err)
	}

	return f
}

func newLogger() {
	api.NewLogger(false)
}
