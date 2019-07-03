package main

import (
  "fmt"
  "github.com/jroimartin/gocui"
)

// OPTION INTERFACE

type option interface {
  Present(g *gocui.Gui, v *gocui.View) error
  Name() string
  IsModuleConfig() bool
}

// MULTIOPTION

type multiOption struct {
  options []string
  name string
  isModuleConfig bool
}

func (mo multiOption) Present(g *gocui.Gui, v *gocui.View) error {
  for _, option := range mo.options {
    fmt.Fprintln(v, option)
  }
  v.Highlight = true
  if _, err := g.SetCurrentView("main"); err != nil {
    return err
  }
  return nil
}

func (mo multiOption) Name() string {
  return mo.name
}

func (mo multiOption) IsModuleConfig() bool {
  return mo.isModuleConfig
}

// TEXTINPUTOPTION

type textInputOption struct {
  prompt string
  name string
  isModuleConfig bool
}

func (to textInputOption) Present(g *gocui.Gui, v *gocui.View) error {
  fmt.Fprintln(v, to.prompt)
  v.Highlight = false
  maxX, maxY := g.Size()
  if iView, err := g.SetView("input", maxX/2-30, maxY/2, maxX/2+30, maxY/2+2); err != nil {
    if err != gocui.ErrUnknownView {
      return err
    }
    iView.Editable = true
    if _, err := g.SetCurrentView("input"); err != nil {
      return err
    }
  }
  return nil
}

func (to textInputOption) Name() string {
  return to.name
}

func (to textInputOption) IsModuleConfig() bool {
  return to.isModuleConfig
}

// SAVEOPTION

type saveOption struct {}

func (so saveOption) Present(g *gocui.Gui, v *gocui.View) error {

  fmt.Fprintln(v, "SAVE CONFIG")
  fmt.Fprintln(v, "-----------")
  fmt.Fprintln(v, "")
  fmt.Fprintln(v, "Please choose a file name for this workflow\nconfiguration.\n\nIt will be saved as a yaml file in your workflows\ndirectory.")

  maxX, maxY := g.Size()
  if iView, err := g.SetView("save", maxX/2-30, maxY/2, maxX/2+30, maxY/2+2); err != nil {
    if err != gocui.ErrUnknownView {
      return err
    }
    iView.Editable = true
    if _, err := g.SetCurrentView("save"); err != nil {
      return err
    }
  }
  return nil
}

func (to saveOption) Name() string {
  return "save"
}

func (to saveOption) IsModuleConfig() bool {
  return false
}
