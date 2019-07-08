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
	http.HandleFunc("/element", handleElement)

	log.Println("Listening on port 8080...")
	http.ListenAndServe(port, nil)
}

// HANDLERS
func handleElementMap(w http.ResponseWriter, r *http.Request) {
	serveJsonData(ELEMENT_MAP, w)
}

func handleElement(w http.ResponseWriter, r *http.Request) {
	q, q_err := getQuery(r, "q")
	context, context_err := getQuery(r, "context")
	id, id_err := getQuery(r, "id")
	media, media_err := getQuery(r, "media")

	if q_err != nil || context_err != nil {
		errorHandler(w, r, http.StatusBadRequest)
		return
	}

	terms := strings.Split(q, "/")
	if len(terms) > 2 {
		errorHandler(w, r, http.StatusBadRequest)
		return
	}

	enableCors(&w)
	w.Header().Set("Cache-Control", "no-cache")
	var selector string = terms[0]
	var hasAnalyser bool = len(terms) > 1
	var hasElement bool = id_err == nil
	var hasMedia bool = media_err == nil

	if hasAnalyser {
		analyser := terms[1]
		var output AnalysedDir
		for i := 0; i < len(ELEMENT_MAP.Analysed); i++ {
			output = ELEMENT_MAP.Analysed[i]
			if output.Component == analyser {
				if context == "" || context == output.Context {
					if hasElement && hasMedia {
						elPath := getPathToAnalysedElementMedia(output, id, media)
						http.ServeFile(w, r, elPath)
					} else {
						serveJsonData(output, w)
					}
					return
				}
			}
		}
	} else {
		var output SelectedDir
		for i := 0; i < len(ELEMENT_MAP.Selected); i++ {
			output = ELEMENT_MAP.Selected[i]
			if output.Component == selector {
				if context == "" || context == output.Context {
					if hasElement && hasMedia {
						elPath := getPathToSelectedElementMedia(output, id, media)
						http.ServeFile(w, r, elPath)
					} else {
						serveJsonData(output, w)
					}
					return
				}
			}
		}
		// for i := 0; i < len(ELEMENT_MAP.Selected); i++ {
		// 	output := ELEMENT_MAP.Selected[i]
		// 	if output.Component == selector {
		// 		break
		// 	}
		// }
		// if counter == len(ELEMENT_MAP.Selected) {
		// 	errorHandler(w, r, http.StatusNotFound)
		// 	return
		// }
		// if id != -1 {
		// 	serveJsonData(output.Elements[id], w)
		// } else {
		// 	serveJsonData(output, w)
		// }
	}
}
