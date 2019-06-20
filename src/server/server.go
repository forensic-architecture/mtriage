package main

import (
  "log"
  "net/http"
  "encoding/json"
  "path/filepath"
  "os"
)

type ElementsData struct {
    Elements []string
}

func main() {

  http.HandleFunc("/elements", handleElements)
  http.HandleFunc("/element", handleElement)

  log.Println("Listening on port 8080...")
  http.ListenAndServe(":8080", nil)
}

func handleElements(w http.ResponseWriter, r *http.Request) {
  var files []string
  root := "elements"
  err := filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
    if !info.IsDir() {
      return nil
    }
    if info.Name() == "elements" {
      return nil
    }
    name := info.Name()
    files = append(files, name)
    return nil
  })
  if err != nil {
    panic(err)
  }
  w.Header().Set("Access-Control-Allow-Origin", "*")
  w.Header().Set("Content-Type", "application/json")
  w.WriteHeader(http.StatusCreated)
  elements := ElementsData{Elements: files}
  json.NewEncoder(w).Encode(elements)
}

func handleElement(w http.ResponseWriter, r *http.Request) {
  ids, ok := r.URL.Query()["id"]
  if !ok || len(ids[0]) < 1 {
        log.Println("Url Param 'id' is missing")
        return
  }
  id := ids[0]
  path := "elements/" + id + "/"
  media, ok := r.URL.Query()["media"]
  if ok {
    path = path + media[0]
  } else {
    path = path + id + ".json"
  }

  file, err := os.Readlink(path)
  if err != nil {
    panic(err)
  }

  w.Header().Set("Access-Control-Allow-Origin", "*")
  w.Header().Set("Content-Type", "application/json")

  http.ServeFile(w, r, file)
}
