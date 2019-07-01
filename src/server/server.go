package main

import (
	"log"
	"net/http"
	"os"
	"strings"
)

// global element map. This variable is populated when the server starts by
// indexing the working directory's filesystem, and keeps all global state for
// mserver. Could think about better persistent storage in the future.
var ELEMENT_MAP ElementMap

// ENTRYPOINT
func main() {
	if len(os.Args) != 2 {
		log.Println("You need to pass the working directory context as the first argument to mserver")
		os.Exit(1)
	}
	workingDir := os.Args[1]
	exists, err := dirExists(workingDir)
	if !exists || err != nil {
		log.Println("You need to pass a working directory that exists.")
		os.Exit(1)
	}
	port := ":8080"

	// NOTE: populates ELEMENT_MAP synchronously
	err = indexComponentDirs(workingDir)

	if err != nil {
		panic("Could not index")
		os.Exit(1)
	}

	http.HandleFunc("/elementmap", handleElementMap)
	http.HandleFunc("/elements", handleElements)
	http.HandleFunc("/element", handleElement)

	log.Println("Listening on port 8080...")
	http.ListenAndServe(port, nil)
}

// HANDLERS
func handleElementMap(w http.ResponseWriter, r *http.Request) {
	serveJsonData(ELEMENT_MAP, w)
}

func handleElement(w http.ResponseWriter, r *http.Request) {
	query, ok := r.URL.Query()["q"]
	if !ok || len(values[0] < 1) {
		errorHandler(w, r, http.StatusBadRequest)
	}
	query = query[0]
	terms := strings.Split(query, "/")
	if len(terms) <= 1 {
		errorHandler(w, r, http.StatusBadRequest)
		return
	}
	serveJsonData(ELEMENT_MAP, w)
}

func handleElements(w http.ResponseWriter, r *http.Request) {
	id := getRequestValue("id", r)
	media := getRequestValue("media", r)
	// path := ELEMENTS_DIR + "/" + id + "/"
	// log.Println(path)
	log.Println(id)
	log.Println(media)
	// if media != "" {
	// 	path = path + "media/" + media
	// 	serveSymlink(path, w, r)
	// } else {
	// 	path = path + id + ".json"
	// 	serveJson(path, w, r)
	// }
}
