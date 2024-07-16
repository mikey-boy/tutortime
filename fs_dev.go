//go:build !prod
// +build !prod

package main

import (
	"io/fs"
	"os"
)

func getFrontendAssets() fs.FS {
	return os.DirFS("frontend/dist")
}
