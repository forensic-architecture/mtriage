package main

import (
	"log"
	"net/http"
	"os"
	"strings"
	"strconv"
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
	http.HandleFunc("/element", handleElement)

	log.Println("Listening on port 8080...")
	http.ListenAndServe(port, nil)
}

// HANDLERS
func handleElementMap(w http.ResponseWriter, r *http.Request) {
	serveJsonData(ELEMENT_MAP, w)
}

func handleElement(w http.ResponseWriter, r *http.Request) {
	var context string = ""
	var id int64 = -1
	queries := r.URL.Query()["q"]
	_context := r.URL.Query()["context"]
	_id := r.URL.Query()["id"]
	if len(queries) <= 0 {
		errorHandler(w, r, http.StatusBadRequest)
		return
	}
	query := queries[0]
	terms := strings.Split(query, "/")
	if len(terms) > 2 {
		errorHandler(w, r, http.StatusBadRequest)
		return
	}
	if len(_context) > 0 {
		context = _context[0]
	}
	if len(_id) > 0 {
		theid, err := strconv.ParseInt(_id[0], 10, 64)
		id = theid
		if err != nil {
			errorHandler(w, r, http.StatusBadRequest)
			return
		}
	}

	var selector string = terms[0]
	var hasAnalyser bool = len(terms) > 1
	var counter int = 0

	// NOTE: SUPER shoddy code, just needed to get it working, will return
	// TODO(lachlan)
	if hasAnalyser {
		var output AnalysedDir
		analyser := terms[1]
		for i := 0; i < len(ELEMENT_MAP.Analysed); i++ {
			output = ELEMENT_MAP.Analysed[i]
			if output.Component == analyser {
				if context == "" || context == output.Context {
					break
				}
			}
			counter += 1
		}
		if counter == len(ELEMENT_MAP.Analysed) {
			errorHandler(w, r, http.StatusNotFound)
			return
		}
		if id != -1 {
			var pathToElement strings.Builder
			w.Header().Set("Cache-Control", "no-cache")
			pathToElement.WriteString(output.Path)
			pathToElement.WriteString("/")
			pathToElement.WriteString(output.Elements[id].Id)
			pathToElement.WriteString("/")
			// NOTE: just serve the first element for the time being
			pathToElement.WriteString(output.Elements[id].Media["all"][0])
			http.ServeFile(w, r, pathToElement.String())
		} else {
			serveJsonData(output, w)
		}
		return
	} else {
		var output SelectedDir
		for i := 0; i < len(ELEMENT_MAP.Selected); i++ {
			output = ELEMENT_MAP.Selected[i]
			if output.Component == selector {
				break
			}
			counter += 1
		}
		if counter == len(ELEMENT_MAP.Selected) {
			errorHandler(w, r, http.StatusNotFound)
			return
		}
		if id != -1 {
			serveJsonData(output.Elements[id], w)
		} else {
			serveJsonData(output, w)
		}
		return
	}
}
