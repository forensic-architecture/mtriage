package main

import (
  "log"
  "net/http"
  "encoding/json"
  "io/ioutil"
  "strings"
  "fmt"
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

type Dir struct {
  Path string
  Name string
}

// RESPONSE DATA TYPES

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

  config := loadConfig(CONFIG_FILE)
  port := fmt.Sprintf(":%d", config.Port)
  castElements(config)

  http.HandleFunc("/elementIndex", handleElementIndex)
  http.HandleFunc("/elements", handleElements)
  http.HandleFunc("/element", handleElement)

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
  if media != "" {
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
