package main

import (
  "fmt"
  "log"
  "github.com/jroimartin/gocui"
)

// CONSTANTS

const VIEW_MAIN = "main"
const VIEW_SIDE = "side"
const VIEW_INPUT = "input"
const VIEW_SAVE = "save"
const VIEW_CONSOLE = "console"

const OPT_PHASE = "phase"
const OPT_FOLDER = "folder"
const OPT_MODULE = "module"

const PHASE_SELECT = "select"
const PHASE_ANALYSE = "analyse"

const LIB_SELECTORS = "selectors"
const LIB_ANALYSERS = "analysers"

const EXEC_MTRIAGE = "../../mtriage"
const DIR_WORKFLOWS = "../../workflows"
const DIR_LIB = "../lib"
const DIR_SELECTORS = DIR_LIB + "/" + LIB_SELECTORS
const DIR_ANALYSERS = DIR_LIB + "/" + LIB_ANALYSERS

const TYPE_STRING = "string"
const TYPE_FOLDER = "folder"
const TYPE_DATE = "date"
const TYPE_INT = "int"
const TYPE_WHITELIST = "whitelist"
const TYPE_BOOL = "bool"

const MODULE_META = "meta"

// GOCUI LIFECYCLE

func main() {

  g, err := gocui.NewGui(gocui.OutputNormal)
  if err != nil {
    log.Panicln(err)
  }
  defer g.Close()

  g.Cursor = true

  g.SetManagerFunc(layout)

  if err := keybindings(g); err != nil {
    log.Panicln(err)
  }

  if err := g.MainLoop(); err != nil && err != gocui.ErrQuit {
    log.Panicln(err)
  }
}

func layout(g *gocui.Gui) error {

  maxX, maxY := g.Size()
  sideWidth := 60
  helpHeight := 4
  logHeight := 30

  if v, err := g.SetView(VIEW_MAIN, 0, 0, sideWidth-2, maxY-helpHeight-1); err != nil {
    if err != gocui.ErrUnknownView {
      return err
    }
    v.SelBgColor = gocui.ColorGreen
    v.SelFgColor = gocui.ColorBlack
    if _, err := g.SetCurrentView(VIEW_MAIN); err != nil {
      return err
    }
    v.Wrap = true
    updateUI(g, currentState(g))
  }

  if v, err := g.SetView("help", 0, maxY - helpHeight, sideWidth-2, maxY-1); err != nil {
    if err != gocui.ErrUnknownView {
      return err
    }
    fmt.Fprintln(v, " Undo: ctrl+z")
    fmt.Fprintln(v, " Quit: ctrl+c")
  }

  if _, err := g.SetView(VIEW_SIDE, sideWidth, 0, maxX-1, maxY-logHeight-1); err != nil {
    if err != gocui.ErrUnknownView {
      return err
    }
  }

  if v, err := g.SetView(VIEW_CONSOLE, sideWidth, maxY - logHeight, maxX-1, maxY-1); err != nil {
    if err != gocui.ErrUnknownView {
      return err
    }
    v.Autoscroll = true
  }
  g.SetViewOnTop(VIEW_INPUT)
  return nil
}

func quit(g *gocui.Gui, v *gocui.View) error {
  return gocui.ErrQuit
}

func keybindings(g *gocui.Gui) error {
  if err := g.SetKeybinding("", gocui.KeyCtrlC, gocui.ModNone, quit); err != nil {
    log.Panicln(err)
  }
  if err := g.SetKeybinding("", gocui.KeyCtrlZ, gocui.ModNone, undo); err != nil {
    log.Panicln(err)
  }
  if err := g.SetKeybinding(VIEW_MAIN, gocui.KeyArrowUp, gocui.ModNone, cursorUp); err != nil {
    return err
  }
  if err := g.SetKeybinding(VIEW_MAIN, gocui.KeyArrowDown, gocui.ModNone, cursorDown); err != nil {
    return err
  }
  if err := g.SetKeybinding(VIEW_MAIN, gocui.KeyEnter, gocui.ModNone, selectOption); err != nil {
    return err
  }
  if err := g.SetKeybinding(VIEW_INPUT, gocui.KeyEnter, gocui.ModNone, inputEntered); err != nil {
    return err
  }
  if err := g.SetKeybinding(VIEW_SAVE, gocui.KeyEnter, gocui.ModNone, saveRequested); err != nil {
    return err
  }
  if err := g.SetKeybinding(VIEW_SAVE, gocui.KeySpace, gocui.ModNone, addAnalyser); err != nil {
    return err
  }

  return nil
}

// EVENT HANDLERS

func addAnalyser(g *gocui.Gui, v *gocui.View) error {
  so := currentState(g).option.(saveOption)
  if !so.isComposable {
    return nil
  }
  update(g, so, nil)
  updateUI(g, currentState(g))
  return nil
}

func saveRequested(g *gocui.Gui, v *gocui.View) error {
  input := v.Buffer()
  if len(input) == 0 {
    return nil
  }
  input = input[:len(input)-1]  // remove trailing newline
  save(g, input)
  return quit(g, v)
}

func undo(g *gocui.Gui, v *gocui.View) error {
  popState(g)
  updateUI(g, currentState(g))
  return nil
}

func cursorUp(g *gocui.Gui, v *gocui.View) error {
  if v != nil {
    ox, oy := v.Origin()
    cx, cy := v.Cursor()
    if err := v.SetCursor(cx, cy-1); err != nil && oy > 0 {
      if err := v.SetOrigin(ox, oy-1); err != nil {
        return err
      }
    }
  }
  return nil
}

func cursorDown(g *gocui.Gui, v *gocui.View) error {
  // type assertion: current option is multiOption
  o := currentState(g).option.(multiOption)
  if v != nil {
    cx, cy := v.Cursor()
    if cy < len(o.options)-1 {
      if err := v.SetCursor(cx, cy+1); err != nil {
        ox, oy := v.Origin()
        if err := v.SetOrigin(ox, oy+1); err != nil {
          return err
        }
      }
    }
  }
  return nil
}

func selectOption(g *gocui.Gui, v *gocui.View) error {
  // type assertion: current option is multiOption
  o := currentState(g).option.(multiOption)
  if v != nil {
    _, cy := v.Cursor()
    if cy < len(o.options) {
      selectedOption := o.options[cy]
      update(g, o, selectedOption)
      newState := currentState(g)
      updateUI(g, newState)
    }
  }
  return nil
}

func inputEntered(g *gocui.Gui, v *gocui.View) error {

  o := history[len(history)-1].option.(textInputOption)

  input := v.Buffer()
  if len(input) == 0 {
    return nil
  }
  input = input[:len(input)-1]  // remove trailing newline
  vInput := o.Validate(g, input)
  if vInput == nil {
    return nil
  }

  if err := g.DeleteView(VIEW_INPUT); err != nil {
    return err
  }
  if _, err := g.SetCurrentView(VIEW_MAIN); err != nil {
    return err
  }

  update(g, o, vInput)
  newState := currentState(g)
  updateUI(g, newState)

  return nil
}

func updateUI(g *gocui.Gui, newState state) {
  updateConfigView(g, newState)
  updateOptionView(g, newState)
}

// HELPERS

func printToView(g *gocui.Gui, view string, text string) error {
  v, err := g.View(view)
  if err != nil {
    return err
  }
  if v != nil {
    fmt.Fprintln(v, text)
  }
  return nil
}

func updateConfigView(g *gocui.Gui, newState state) error {
    stateMap := newState.AsMap()
    yamlString := mapToYamlString(stateMap)
    v, err := g.View(VIEW_SIDE)
    if err != nil {
      return err
    }
    if v != nil {
      v.Clear()
      printToView(g, VIEW_SIDE, yamlString)
    }
    return nil
}

func updateOptionView(g *gocui.Gui, newState state) error {

  o := newState.option
  v, err := g.View(VIEW_MAIN)
  v.SetCursor(0, 0)
  if err != nil {
    return err
  }
  if v != nil {
    v.Clear()
    if err := g.DeleteView(VIEW_INPUT); err != nil {}
    if err := g.DeleteView(VIEW_SAVE); err != nil {}
    o.Present(g, v)
  }
  return nil
}

func logger(g *gocui.Gui, text string) {
  v, _ := g.View(VIEW_CONSOLE)
  if v != nil {
    fmt.Fprintln(v, text)
  }
}
