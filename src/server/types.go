package main

// INTERNAL TYPES
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

type EtypedElement struct {
	Id string
	Etype string
	Media map[string][]string
}

type EtypedDir struct {
	Path string
	ComponentName string
	Elements []EtypedElement
}

type SelectedDir EtypedDir
type AnalysedDir EtypedDir

type ElementMap struct {
	Selected []SelectedDir
	Analysed []AnalysedDir
}

