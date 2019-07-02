package main

import (
	"net/http"
	"path/filepath"
	"os"
	"encoding/json"
	"io/ioutil"
	"strings"
	"log"
)

const DATA_DIR = "data"
const DERIVED_DIR = "derived"

// run on server start
func indexComponentDirs(dir string) error {
	log.Println("Making element map...")
	ELEMENT_MAP = ElementMap{ Selected: []SelectedDir{}, Analysed: []AnalysedDir{} }
	err := filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		// skip files
		if !info.IsDir() {
			return nil
		}
		name := info.Name()
		// append all selector elements
		if name == DATA_DIR {
			elements, err := getChildDirsEtyped(path)
			if err != nil {
				panic("somthing")
			}
			allBits := strings.Split(path, "/")
			compName := allBits[len(allBits)-2]
			context := allBits[len(allBits)-3]

			dir := SelectedDir{
				Path: path,
				Context: context,
				Component: compName,
				Elements: elements,
			}
			ELEMENT_MAP.Selected = append(ELEMENT_MAP.Selected, dir)
		}
		// append all derived folders
		if name == DERIVED_DIR {
			childDirs, err := getChildDirs(path)
			if err != nil {
				panic("somthng")
			}
			for i := 0; i < len(childDirs); i++ {
				dir := childDirs[i]
				elements, err := getChildDirsEtyped(dir.Path)
				if err != nil {
					panic("somthing")
				}
				allBits := strings.Split(dir.Path, "/")
				selector := allBits[len(allBits)-3]
				context := allBits[len(allBits)-4]

				edir := AnalysedDir{
					Path: dir.Path,
					Selector: selector,
					Context: context,
					Component: dir.Name,
					Elements: elements,
				}
				ELEMENT_MAP.Analysed = append(ELEMENT_MAP.Analysed, edir)
			}
		}
		return nil
	})
	if err != nil {
		panic(err)
	}
	return nil
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

func getChildDirsEtyped(path string) ([]EtypedElement, error) {
	var els []EtypedElement
	childDirs, err := ioutil.ReadDir(path)
	if err != nil {
		return els, err
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
		elPath := str.String()
		// TODO: attempt other casts
		etypedEl := castToEtype(elPath, getEtype("Any"), dir.Name())
		els = append(els, etypedEl)
	}
	return els, nil

}

// IO
func errorHandler(w http.ResponseWriter, r* http.Request, status int) {
	w.WriteHeader(status)
}

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
