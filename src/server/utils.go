package main

import (
	"log"
	"net/http"
	"path/filepath"
	"os"
	"encoding/json"
	"io/ioutil"
	"strings"

)

func enableCors(w *http.ResponseWriter) {
	(*w).Header().Set("Access-Control-Allow-Origin", "*")
}

func serveJson(file string, w http.ResponseWriter, r *http.Request) {
	enableCors(&w)
	http.ServeFile(w, r, file)
}

func serveJsonData(data interface{}, w http.ResponseWriter) {
	enableCors(&w)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(data)
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
// FILE PATHS
func dirExists(path string) (bool, error) {
	_, err := os.Stat(path)
	if err == nil { return true, nil }
	if os.IsNotExist(err) { return false, nil }
	return true, err
}

func getFilesInDir(dir string, skips []string) []File {
	var files []File
	err := filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		if info.IsDir() {
			return nil
		}
		for i := 0; i < len(skips); i++ {
			if info.Name() == skips[i] {
				return nil
			}
		}
		name := info.Name()
		ext := filepath.Ext(path)
		files = append(files, File{ Path: path, Name: name, Ext: ext })
		return nil
	})
	if err != nil {
		panic(err)
	}
	return files
}

func getChildDirs(path string) ([]Dir, error) {
	var dirs []Dir
	childDirs, err := ioutil.ReadDir(path)
	if err != nil {
		return dirs, err
	}
	for i := 0; i < len(childDirs); i++ {
		dir := childDirs[i]
		if !dir.IsDir() {
			continue
		}
		var str strings.Builder
		str.WriteString(path)
		str.WriteString("/")
		str.WriteString(dir.Name())
		dirs = append(dirs, Dir{ Name: dir.Name(), Path: str.String(), Kind: Unspecified })
	}
	return dirs, nil
}


func getComponentDirs(dir string) []Dir {
	DATA_DIR := "data"
	DERIVED_DIR := "derived"
	var dirs []Dir
	err := filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		// skip files
		if !info.IsDir() {
			return nil
		}
		name := info.Name()
		// append all selector elements
		if name == DATA_DIR {
			dirs = append(dirs, Dir{ Path: path, Name: name, Kind: Selected })
		}
		// append all derived folders
		if name == DERIVED_DIR {
			childDirs, err := getChildDirs(path)
			if err != nil {
				// NOTE: fail silently...
				panic("somthng")
			}
			for i := 0; i < len(childDirs); i++ {
				dir := childDirs[i]
				dir.Kind = Analysed
				dirs = append(dirs, dir)
			}
		}
		return nil
	})
	if err != nil {
		panic(err)
	}
	return dirs
}

func getDirsInDir(dir string, skips []string) []Dir {
	var dirs []Dir
	err := filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		if !info.IsDir() {
			return nil
		}
		for i := 0; i < len(skips); i++ {
			if info.Name() == skips[i] {
				return nil
			}
		}
		name := info.Name()
		dirs = append(dirs, Dir{ Path: path, Name: name })
		return nil
	})
	if err != nil {
		panic(err)
	}
	return dirs
}

func getPathBases(paths []string) []string {
	var bases []string
	for i := 0; i < len(paths); i++ {
		base := filepath.Base(paths[i])
		bases = append(bases, base)
	}
	return bases
}

func getPathBase(path string) string {
	return filepath.Base(path)
}

func resolveSymlink(symlink string) string {
	file, err := os.Readlink(symlink)
	if err != nil {
		// TODO - throw
	}
	return file
}

// IO

func writeToJsonFile(path string, jsonable interface{}) {
	file, err := json.MarshalIndent(jsonable, "", " ")
	if err != nil {
		panic(err)
	}
	err = ioutil.WriteFile(path, file, 0644)
	if err != nil {
		panic(err)
	}
}
