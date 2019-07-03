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

const DIR_WORKFLOWS = "../../workflows"

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
    initState := state{ cfg: make(map[string]interface{}), option: getNextOption(g)}
    pushState(g, initState)
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

  // also a panel that explain the keys to use

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
  if err := g.SetKeybinding(VIEW_SAVE, gocui.KeyEnter, gocui.ModNone, saveFile); err != nil {
    return err
  }

  return nil
}

// EVENT HANDLERS

func saveFile(g *gocui.Gui, v *gocui.View) error {
  input := v.Buffer()
  if len(input) == 0 {
    return nil
  }
  input = input[:len(input)-1]  // remove trailing newline
  path := DIR_WORKFLOWS + "/" + input + ".yaml"
  data := history[len(history)-1].cfg
  writeToYamlFile(path, data)
  return gocui.ErrQuit
}

func inputEntered(g *gocui.Gui, v *gocui.View) error {

  input := v.Buffer()
  if len(input) == 0 {
    return nil
  }
  input = input[:len(input)-1]  // remove trailing newline
  optionName := history[len(history)-1].option.Name()
  isModuleConfig := history[len(history)-1].option.IsModuleConfig()
  update(g, optionName, input, isModuleConfig)

  if err := g.DeleteView(VIEW_INPUT); err != nil {
    // log.Panicln("here")
    return nil
  }
  if _, err := g.SetCurrentView(VIEW_MAIN); err != nil {
    return err
  }

  return nil
}

func undo(g *gocui.Gui, v *gocui.View) error {
  popState(g)
  return nil
}

func cursorUp(g *gocui.Gui, v *gocui.View) error {
  logger(g, "cursor up")
  // type assertion: current option is multiOption
  // history[len(history)-1].option.(multiOption)

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
  logger(g, "cursor down")
  // type assertion: current option is multiOption
  o := history[len(history)-1].option.(multiOption)

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
  o := history[len(history)-1].option.(multiOption)

  if v != nil {

    _, cy := v.Cursor()
    if cy < len(o.options) {

      selectedOption := o.options[cy]
      update(g, o.Name(), selectedOption, o.IsModuleConfig())
    }
  }
  return nil
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

func updateConfigView(g *gocui.Gui, cfg map[string]interface{}) error {

    v, err := g.View(VIEW_SIDE)
    if err != nil {
      return err
    }
    if v != nil {

      v.Clear()

      for key, val := range cfg {
        // value is either a string or not
        if s, ok := val.(string); ok {
          fmt.Fprintln(v, key + ": \"" + s + "\"")
        } else {
          // TODO: has to be a map
          // is a map
        }
      }
    }
    return nil
}

func updateOptionView(g *gocui.Gui, o option) error {
  logger(g, "update option")

  v, err := g.View(VIEW_MAIN)
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

// TODO logic will hook into mtriage
func getNextOption(g *gocui.Gui) option {
  c := len(history)
  if c == 0 {
    return multiOption{ options: []string{"select","analyse"}, isModuleConfig: false, name: "phase" }
  } else if c == 1 {
    return textInputOption{ prompt: "please enter a folder path", name: "folder", isModuleConfig: false  }
  } else {
    return saveOption{}
  }
}
