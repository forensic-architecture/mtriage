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
