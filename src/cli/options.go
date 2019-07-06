package main

import (
  "fmt"
  "github.com/jroimartin/gocui"
  "strings"
  "strconv"
  // "time"
)

// OPTION INTERFACE

type option interface {
  Present(g *gocui.Gui, v *gocui.View) error
  Name() string
}

// MULTIOPTION

type multiOption struct {
  options []string
  name string
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

// TEXTINPUTOPTION

type textInputOption struct {
  prompt string
  name string
  isModuleConfig bool
  validationType string
  childModule string
}

func (to textInputOption) Present(g *gocui.Gui, v *gocui.View) error {
  fmt.Fprintln(v, to.prompt)
  v.Highlight = false
  maxX, maxY := g.Size()
  if iView, err := g.SetView(VIEW_INPUT, maxX/2-30, maxY/2, maxX/2+30, maxY/2+2); err != nil {
    if err != gocui.ErrUnknownView {
      return err
    }
    iView.Editable = true
    if _, err := g.SetCurrentView(VIEW_INPUT); err != nil {
      return err
    }
  }
  return nil
}

func (to textInputOption) Name() string {
  return to.name
}

func (to textInputOption) Validate(g *gocui.Gui, input string) interface{} {
  switch to.validationType {
  case TYPE_INT:
    inInt, err := strconv.Atoi(input)
    if err != nil {
      logger(g, input + " is not an integer")
      return nil
    }
    return inInt
  case TYPE_FOLDER:
    validDir := dirIsValid("../../" + input)
    if !validDir {
      logger(g, "folder " + input + " is invalid")
      return nil
    }
    return input
  case TYPE_EXISTING_FOLDER:
    exists := dirExists("../../" + input)
    if !exists {
      logger(g, "folder " + input + " does not exist")
    }
    return input
  case TYPE_DATE:
    // TODO: consider what restrictions on date formatting (if any) are appropriate here
    // - for the moment accept any string

    // const dtFormat = "2006/01/02 15:04:05"
    // _, err := time.Parse(dtFormat, input)
    // if err != nil {
    //   logger(g, input + " is not a valid date format. Dates must be formatted YYYY/MM/DD HH:MM:SS")
    //   return nil
    // }

    return input
  case TYPE_BOOL:
    inBool, err := strconv.ParseBool(input)
    if err != nil {
      logger(g, input + " is not a bool. Please enter 'true' or 'false'")
      return nil
    }
    return inBool
  case TYPE_WHITELIST:
    whitelist := strings.Split(input, ",")
    return whitelist
  default:  // accepts anything
    return input
  }
}

// SAVEOPTION

type saveOption struct {
  isComposable bool
}

func (so saveOption) Present(g *gocui.Gui, v *gocui.View) error {

  fmt.Fprintln(v, "SAVE CONFIG")
  fmt.Fprintln(v, "-----------")
  fmt.Fprintln(v, "")
  fmt.Fprintln(v, "Please choose a file name for this workflow\nconfiguration.\n\nIt will be saved as a yaml file in your workflows\ndirectory.\n\n")
  if so.isComposable {
    fmt.Fprintln(v, "Or to add another analyser, press SPACE.")
  }
  v.Highlight = false

  maxX, maxY := g.Size()
  if iView, err := g.SetView(VIEW_SAVE, maxX/2-30, maxY/2, maxX/2+30, maxY/2+2); err != nil {
    if err != gocui.ErrUnknownView {
      return err
    }
    iView.Editable = true
    if _, err := g.SetCurrentView(VIEW_SAVE); err != nil {
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
