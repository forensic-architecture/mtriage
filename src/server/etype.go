package main

import (
  "regexp"
)

type MediaType struct {
  Key string
  Regex string
}

type Etype int

const (
  Any                   Etype = 0 + iota
  Image
  Video
  Audio
  Json
  ImageArray
  JsonArray
  AnnotatedVideo
  AnnotatedImageArray
  AnnotatedAudio
)

func (etype Etype) String() string {
  names := [...] string {
    "Any",
    "Image",
    "Video",
    "Audio",
    "Json",
    "ImageArray",
    "JsonArray",
    "AnnotatedVideo",
    "AnnotatedImageArray",
    "AnnotatedAudio",
  }
  if etype < Any || etype > AnnotatedImageArray {
    panic("Unrecognised Etype")
  }
  return names[etype]
}

func (etype Etype) MediaTypes() []MediaType {

  indexers := [...] []MediaType {

    []MediaType{ MediaType{ Key: "all", Regex: "." }},
    []MediaType{ MediaType{ Key: "image", Regex: ".[bB][mM][pP]" }},
    []MediaType{ MediaType{ Key: "video", Regex: ".[mM][pP][4]" }},
    []MediaType{ MediaType{ Key: "audio", Regex: ".([mM][pP][3])|([wW][aA][vV])" }},
    []MediaType{ MediaType{ Key: "json", Regex: ".[jJ][sS][oO][nN]" }},
    []MediaType{ MediaType{ Key: "images", Regex: ".[bB][mM][pP]" }},
    []MediaType{ MediaType{ Key: "jsons", Regex: ".[jJ][sS][oO][nN]" }},
    []MediaType{ MediaType{ Key: "video", Regex: ".[mM][pP][4]" },
                  MediaType{ Key: "json", Regex: ".[jJ][sS][oO][nN]" }},
    []MediaType{ MediaType{ Key: "image", Regex: ".[bB][mM][pP]" },
                  MediaType{ Key: "json", Regex: ".[jJ][sS][oO][nN]" }},
    []MediaType{ MediaType{ Key: "audio", Regex: ".([mM][pP][3])|([wW][aA][vV])" },
                  MediaType{ Key: "json", Regex: ".[jJ][sS][oO][nN]" }},
  }

  if etype < Any || etype > AnnotatedImageArray {
    panic("Unrecognised Etype")
  }
  return indexers[etype]
}

func getEtype(name string) Etype {
    switch name {
      case "Any":
        return Any
      case "Image":
        return Image
      case "Video":
        return Video
      case "Json":
        return Json
      case "ImageArray":
        return ImageArray
      case "JsonArray":
        return JsonArray
      case "AnnotatedVideo":
        return AnnotatedVideo
      case "AnnotatedImageArray":
        return AnnotatedImageArray
      case "AnnotatedAudio":
        return AnnotatedAudio
      default:
        panic("Unrecognised Etype")
    }
}

func globit(path string, regex string, is_single bool) []string {

  var globbed []string
  files := getFilesInDir(path, []string{".DS_Store"})
  for i := range files {
    file := files[i]
    match, _ := regexp.MatchString(regex, file.Name)
    if match {
      globbed = append(globbed, file.Name)
    }
  }
  if is_single && len(globbed) != 1 {
    panic("Too many files in " + path)
  }
  return globbed
}

func castToEtype(el_path string, etype Etype, elementId string) EtypedElement {
  return EtypedElement {
    Id: elementId,
    Etype: etype.String(),
    Media: getMedia(el_path, etype),
  }
}

func getMedia(el_path string, etype Etype) map[string][]string {
  media := make(map[string][]string)
  mediaTypes := etype.MediaTypes()
  for i := range mediaTypes {
    mediaType := mediaTypes[i]
    media[mediaType.Key] = globit(el_path, mediaType.Regex, false)
  }
  return media
}
