package main

import (
	"log"
	"net/http"
	"encoding/json"
	"io/ioutil"
	"strings"
	"os"
)

// INTERNAL TYPES

type Config struct {
	Port int
	Etype string
}

type File struct {
	Path string
	Name string
	Ext string
}

type ElementDirKind int
const (
	Unspecified ElementDirKind = 0
	Selected	ElementDirKind = 1
	Analysed	ElementDirKind = 2
)

type Dir struct {
	Path string
	Name string
	Kind ElementDirKind
}

type ElementMap struct {
	Selected []EtypedDir
	Analysed []EtypedDir
}

// RESPONSE DATA TYPES

type EtypedDir struct {
	Path string
	Name string
	Kind ElementDirKind
	Elements []EtypedElement
}

type EtypedElement struct {
	Id string
	Etype string
	Media map[string][]string
}
type ElementIndex struct {
	Elements []string
}

type ElementsData struct {
	Elements []EtypedElement
}

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
	elementMap := indexAndCastElements(workingDir)
	log.Println(elementMap)

	// http.HandleFunc("/elementIndex", handleElementIndex)
	// http.HandleFunc("/elements", handleElements)
	// http.HandleFunc("/element", handleElement)

	log.Println("Listening on port 8080...")
	http.ListenAndServe(port, nil)
}

// HANDLERS
func handleElementIndex(w http.ResponseWriter, r *http.Request) {
	elementDirs := getDirsInDir(ELEMENTS_DIR, []string{"media", "elements"})
	var elementNames []string
	for i := range elementDirs {
		elementNames = append(elementNames, elementDirs[i].Name)
	}
	elementsData := ElementIndex{ Elements: elementNames }
	serveJsonData(elementsData, w)
}

func handleElements(w http.ResponseWriter, r *http.Request) {
	elementDirs := getDirsInDir(ELEMENTS_DIR, []string{"media", "elements"})
	var elements []EtypedElement
	for i := range elementDirs {
		path := ELEMENTS_DIR + "/" + elementDirs[i].Name + "/" + elementDirs[i].Name + ".json"
		element := loadTypedElement(path)
		elements = append(elements, element)
	}
	serveJsonData(elements, w)
}

func handleElement(w http.ResponseWriter, r *http.Request) {
	id := getRequestValue("id", r)
	media := getRequestValue("media", r)
	path := ELEMENTS_DIR + "/" + id + "/"
	log.Println(path)
	if media != "" {
		log.Println("we here")
		path = path + "media/" + media
		serveSymlink(path, w, r)
	} else {
		path = path + id + ".json"
		serveJson(path, w, r)
	}
}

// HELPERS

func enableCors(w *http.ResponseWriter) {
	(*w).Header().Set("Access-Control-Allow-Origin", "*")
}

func serveJson(file string, w http.ResponseWriter, r *http.Request) {
	enableCors(&w)
	http.ServeFile(w, r, file)
}

func serveSymlink(link string, w http.ResponseWriter, r *http.Request) {
	file := resolveSymlink(link)
	enableCors(&w)
	http.ServeFile(w, r, file)
}

func serveJsonData(data interface{}, w http.ResponseWriter) {
	enableCors(&w)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(data)
}

func loadConfig(path string) Config {
	file, err := ioutil.ReadFile(path)
	if err != nil {
		panic(err)
	}
	config := Config{}
	err = json.Unmarshal([]byte(file), &config)
	if err != nil {
		panic(err)
	}
	return config
}

func loadTypedElement(path string) EtypedElement {
	file, err := ioutil.ReadFile(path)
	if err != nil {
		panic(err)
	}
	element := EtypedElement{}
	err = json.Unmarshal([]byte(file), &element)
	if err != nil {
		panic(err)
	}
	return element
}

func getRequestValue(param string, r *http.Request) string {
	values, ok := r.URL.Query()[param]
	if !ok || len(values[0]) < 1 {
		return ""
	}
	return values[0]
}

func castElements(config Config) {
	elementDirs := getDirsInDir(ELEMENTS_DIR, []string{"media", "elements"})
	for i := 0; i < len(elementDirs); i++ {
		elementDir := elementDirs[i]
		elementId := strings.Replace(elementDir.Path, "/media", "", -1)
		elementId = strings.Replace(elementId, ELEMENTS_DIR + "/", "", -1)
		etype := getEtype(config.Etype)
		typedElement := castToEtype(elementDir.Path + "/media", etype, elementId)
		filepath := ELEMENTS_DIR + "/" + elementId + "/" + elementId + ".json"
		writeToJsonFile(filepath, typedElement)
	}
}

func indexAndCastElements(workingDir string) ElementMap {
	componentDirs := getComponentDirs(workingDir)
	for i := 0; i < len(componentDirs); i++ {
		elementDir := componentDirs[i]
		childDirs, _ := getChildDirs(elementDir.Path)
		// TODO: heuristic for deciding how to cast elements...
		for i := 0; i < len(childDirs); i++ {
			log.Println(childDirs[i])
		}
		// elementId := strings.Replace(elementDir.Path, "/media", "", -1)
		// elementId = strings.Replace(elementId, ELEMENTS_DIR + "/", "", -1)
		// etype := getEtype(config.Etype)
		// typedElement := castToEtype(elementDir.Path + "/media", etype, elementId)
		// filepath := ELEMENTS_DIR + "/" + elementId + "/" + elementId + ".json"
		// writeToJsonFile(filepath, typedElement)
	}

	return ElementMap{ Selected: []EtypedDir{}, Analysed: []EtypedDir{} }
}
