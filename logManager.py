import tkinter as tk
import tkinter.font
import tkinter.simpledialog

from gameClasses import Option, Entry, Spell, Enemy, Weapon, Potion, TextBox
from tkManager import clear, Button, Canvas, onFrameConfigure, Label, ImageButton


def createLogbookPage(logbookPage, plr):
    clear(logbookPage)
    topMenu = tk.Frame(logbookPage, pady=5, padx=5, bg="gray85", highlightthickness=2)
    topMenu.grid(column=0, row=0, columnspan=4, sticky="nsew")
    Button("Add Entry", lambda: addEntry(Entry(), plr, logbookPage), topMenu).grid(column=0, row=0)
    Button("Add Folder", lambda: addEntry(Option([], "New Folder"), plr, logbookPage), topMenu).grid(column=1, row=0)

    tabCanvas = Canvas(logbookPage, borderwidth=0, background="gray85", width=200)
    tabFrame = tk.Frame(tabCanvas, bg="gray85", highlightbackground="gray70", highlightthickness=2, pady=5, padx=5)
    tabScrollbar = tk.Scrollbar(logbookPage, orient="vertical", command=tabCanvas.yview)
    tabCanvas.configure(yscrollcommand=tabScrollbar.set)
    tabFrame.columnconfigure(0)

    infoCanvas = Canvas(logbookPage, borderwidth=0, background="gray85", width=450)
    infoFrame = tk.Frame(infoCanvas, background="gray85")
    infoScrollbar = tk.Scrollbar(logbookPage, orient="vertical", command=infoCanvas.yview)
    infoCanvas.configure(yscrollcommand=infoScrollbar.set)

    tabScrollbar.grid(sticky="esn", column=1, row=1)
    tabCanvas.grid(sticky="nsw", column=0, row=1)
    tabCanvas.create_window((4, 4), window=tabFrame, anchor="ne")
    infoScrollbar.grid(sticky="esn", column=3, row=1)
    infoCanvas.grid(sticky="nsw", column=2, row=1)
    infoCanvas.create_window((4, 4), window=infoFrame, anchor="nw")

    tabFrame.bind("<Configure>", lambda event, canvas=tabCanvas: onFrameConfigure(canvas))
    infoFrame.bind("<Configure>", lambda event, canvas=infoCanvas: onFrameConfigure(canvas))

    updateLogbookTabs(tabFrame, infoFrame, logbookPage, plr)
    updateLogbookInfo(tabFrame, infoFrame, logbookPage, plr)


def updateLogbookTabs(frame, infoFrame, logbookPage, plr):
    clear(frame)
    openOption(frame, infoFrame, logbookPage, plr)


def updateLogbookInfo(tabFrame, frame, logbookPage, plr, chosen=None):
    clear(frame)
    if chosen is None:
        testLabel = Label(frame, "Logbook Frontpage", anchor=tk.CENTER, width=30)
        testLabel.columnconfigure(0, weight=1)
        testLabel.grid()
    else:
        Label(frame, chosen.name, width=30, anchor=tk.CENTER).grid()
        if type(chosen) == Enemy:
            Label(frame, f"Strength: {chosen.strength}").grid()
            Label(frame, f"Health: {chosen.health}").grid()
            Label(frame, f"Range: {chosen.reach}").grid()
            Label(frame, f"Article: {chosen.article}").grid()
        elif type(chosen) == Weapon:
            Label(frame, chosen.desc).grid()
            Label(frame, f"Attack: {chosen.strBonus}").grid()
            Label(frame, f"Range: {chosen.reach}").grid()
            Label(frame, f"Article: {chosen.article}").grid()
        elif type(chosen) == Potion:
            Label(frame, chosen.desc + "\n").grid()
            Label(frame, chosen.effectDesc).grid()


        elif type(chosen) == Spell:
            if chosen.hasExperimented:
                Label(frame, "Experimentation effect:\n" + chosen.desc).grid()
            for part in chosen.history:
                partFrame = tk.Frame(borderwidth=1, highlightcolor="red")
                Label(partFrame, part.desc)

        # Generate added content
        for part in chosen.content:
            partFrame = tk.Frame(frame, background="gray85")
            partFrame.grid()
            if type(part) == TextBox:
                textBox = tk.Text(partFrame, background="gray85", width=40, height=10)
                textBox.insert(tk.END, part.content)
                textBox.configure(state="disabled")
                textBox.grid(column=0, row=0)
                textBox.bind("<FocusIn>", lambda event: plr.bindFuncs[1]())
                textBox.bind("<FocusOut>", lambda event: plr.bindFuncs[0])  # See player init for explanation ish

                editButton = ImageButton(partFrame, None, "editIcon.png")
                editButton.configure(command=lambda box=textBox, frm=partFrame, btn=editButton, txtObj=part: editText(box, frm, btn,
                                                                                                                      part, plr))
                editButton.grid(row=0, column=1, sticky="n")

        #  Buttons at the end
        Button("Add Text", lambda: [chosen.content.append(TextBox()), updateLogbookInfo(tabFrame, frame, logbookPage, plr, chosen)],
               frame).grid()
        Button("Change Name", lambda: changeName(chosen, tabFrame, frame, logbookPage, plr), frame).grid()
        if type(chosen) != Spell and type(chosen) != Entry:
            Button("Change Article", lambda: changeArticle(chosen, tabFrame, frame, logbookPage, plr), frame).grid()
        Button("Change Path", lambda: changePath(chosen, tabFrame, frame, logbookPage, plr), frame).grid()
        Button("Delete", lambda: removeEntry(chosen, plr, tabFrame, frame, logbookPage, chosen.path), frame).grid()


def openOption(frame, infoFrame, logbookPage, plr, parentOption=None, layer=0):  # Loops through options to generate the tabs in tab frame
    if parentOption is None:
        parentOption = Option(plr.gatheredEntries, opened=True)
    for option in parentOption.thing:
        if type(option) == Option:
            optionButton = ImageButton(parent=frame, text=option.name + "  ", command=lambda op=option: openEntry(op, frame, infoFrame,
                                                                                                                  logbookPage, plr),
                                       bg="gray80", font=tkinter.font.Font(family="Arial", size=14, weight="bold"), width=200 - layer * 10,
                                       image="arrow-next-right-icon.png", compound=tk.RIGHT, dimensions=(10, 16))
            optionButton.grid(sticky="w")
            if option.opened:  # Generate contents of a tab if it is opened
                openOption(frame, infoFrame, logbookPage, plr, option, layer + 1)
                optionButton.setImage("arrow-down-icon.png", (16, 10))
        else:
            tk.Button(text=option.name, command=lambda op=option: openEntry(op, frame, infoFrame, logbookPage, plr), master=frame,
                      bg="gray85", font=tkinter.font.Font(
                    family="Arial", size=13), width=22 - layer * 1).grid(sticky="w")


def openEntry(option, tabFrame, infoFrame, logbookPage, plr):
    if type(option) == Option:
        option.opened = not bool(option.opened)
        updateLogbookTabs(tabFrame, infoFrame, logbookPage, plr)
    updateLogbookInfo(tabFrame, infoFrame, logbookPage, plr, option)


def removeEntry(entry, plr, tabFrame, infoFrame, logbookPage, target="/"):
    targetList = target.split("/")
    parentThing = plr.gatheredEntries
    for name in targetList:
        for option in parentThing:
            if option.name == name:
                parentThing = option.thing
                break
    parentThing.remove(entry)
    updateLogbookTabs(tabFrame, infoFrame, logbookPage, plr)


def changeName(target, tabFrame, infoFrame, logbookPage, plr):
    newName = (tkinter.simpledialog.askstring("Change Name", "Please enter the new name"))
    if newName:
        target.name = newName
    updateLogbookInfo(tabFrame, infoFrame, logbookPage, plr, target)
    updateLogbookTabs(tabFrame, infoFrame, logbookPage, plr)


def changeArticle(target, tabFrame, infoFrame, logbookPage, plr):
    newArticle = (
        tkinter.simpledialog.askstring("Change Article", "Please enter the new article that will be used with your item. (Ex: 'An' "
                                                         "-> 'An object')"))
    if newArticle:
        target.article = newArticle
    updateLogbookInfo(tabFrame, infoFrame, logbookPage, plr, target)


def changePath(entry, tabFrame, infoFrame, logbookPage, plr):
    newPath = tkinter.simpledialog.askstring("New Path", "Please enter the new name. (Use '/' to separate folders.)")
    if newPath:
        removeEntry(entry, plr, tabFrame, infoFrame, logbookPage, entry.path)
        addEntry(entry, plr, logbookPage, newPath)


def editText(textBox, frame, button, textObj, plr):
    textBox.configure(state="normal")
    button.setImage("saveIcon.png")
    button.configure(command=lambda: saveText(textBox, frame, button, textObj, plr))


def saveText(textBox, frame, button, textObj, plr):
    textObj.content = textBox.get("1.0", "end-1c")
    textBox.configure(state="disabled")
    plr.bindFuncs[0]()  # Check player init for explanation (ish)
    button.configure(command=lambda: editText(textBox, frame, button, textObj, plr))
    button.setImage("editIcon.png")


def entryExists(entry, plr, parent=None):
    if parent is None:
        parent = plr.gatheredEntries
    for i in parent:
        if type(i) == Option:
            if entryExists(entry, plr, i.thing):
                return True
        elif type(i) != Entry and entry.id == i.id and type(entry) == type(i):
            return True
    return False


def addEntry(entry, plr, logbookPage, target="/"):
    entry.path = target
    targetList = target.split("/")
    parentThing = plr.gatheredEntries
    for name in targetList:
        for option in parentThing:
            if option.name == name and type(option) == Option:
                parentThing = option.thing
                break
    parentThing.append(entry)
    createLogbookPage(logbookPage, plr)
