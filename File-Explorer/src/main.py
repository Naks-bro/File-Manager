import os
import tkinter as tk
from datetime import datetime, timedelta

# from tkinter import ttk
from functools import partial
from sys import platform
import shutil
import threading

from PIL import Image, ImageTk

import ttkbootstrap as ttk
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.dialogs.dialogs import Messagebox
from ttkbootstrap.dialogs.dialogs import Querybox

import ext
import json

# globals
fileNames = []
file_path = ""  # path of main.py
lastDirectory = ""
selectedItem = ""  # focused item on Treeview
src = ""  # temp path for copying
theme = ""  # current theme
photo_ref = []  # keeps references of photos
currDrive = ""
date_format = "%d/%m/%Y, %H:%M:%S"
available_drives = []
font_size = "10"  # default is 10
folderIcon = 0
fileIcon = 0
items = 0  # holds treeview items
cwdLabel = 0
footer = 0

def checkPlatform():
    global currDrive, available_drives
    if platform == "win32":
        available_drives = [
            chr(x) + ":" for x in range(65, 91) if os.path.exists(chr(x) + ":")
        ]  # 65-91 -> search for drives A-Z
        currDrive = available_drives[0]  # current selected drive
    elif platform == "linux":
        available_drives = "/"
        currDrive = available_drives
 
def createWindow():
    # root = tk.Tk()
    root = ttk.Window(themename=theme)
    root.title("My File Explorer")
    root.geometry("1280x720")
    root.resizable(True, True)
    root.iconphoto(False, tk.PhotoImage(file=file_path + "icon.png"))
    return root

def refresh(queryNames):
    global fileNames, folderIcon, fileIcon, items, cwdLabel, footer
    # Refresh Header
    cwdLabel.config(text=" " + os.getcwd())
    # --Refresh Header

    # Refresh Browse
    fileSizesSum = 0
    if queryNames:  # if user gave query and pressed enter
        fileNames = queryNames
    else:
        fileNames = os.listdir(os.getcwd())
    # Ignore Window files which are not accessible
    fileNames = [file for file in fileNames if not (file.startswith('$') or file.startswith('Config.Msi') 
                                                    or file.startswith('hiberfil.sys') or file.startswith('DumpStack.log.tmp')
                                                    or file.startswith('pagefile.sys') or file.startswith('swapfile.sys') 
                                                    or file.startswith('System Volume Information')
                                                    )]
    # print(fileNames)
    fileTypes = [None] * len(fileNames)
    fileSizes = [None] * len(fileNames)
    fileDateModified = []
    fileTag = []
    for i in items.get_children():  # delete data from previous directory
        items.delete(i)
    for i in range(len(fileNames)):
        try:
            found = False
            for file in tag_files:
                if file['file_name'] == os.getcwd() + "\\" + fileNames[i]:
                    found = True
                    tag_type = file['tag_type']
            if found:
                if tag_type == 'Red':
                    fileTag.append("R")
                elif tag_type == 'Green':
                    fileTag.append("G")
                elif tag_type == 'Blue':
                    fileTag.append("B")
                elif tag_type == 'Yellow':
                    fileTag.append("Y")
                elif tag_type == 'Orange':
                    fileTag.append("O")
                elif tag_type == 'Purple':
                    fileTag.append("P")
            else:
                fileTag.append("")

            # modification time of file
            fileDateModified.append(
                datetime.fromtimestamp(os.path.getmtime(fileNames[i])).strftime(
                    "%d-%m-%Y %I:%M"
                )
            )
            # size of file
            fileSizes[i] = str(
                round(os.stat(fileNames[i]).st_size / 1024)
            )  # str->round->size of file in KB
            fileSizesSum += int(fileSizes[i])
            fileSizes[i] = str(round(os.stat(fileNames[i]).st_size / 1024)) + " KB"
            # check file type
            ext.extensions(fileTypes, fileNames, i)
            # print(fileTag[i], fileNames[i], fileDateModified[i], fileTypes[i], fileSizes[i])
            # insert
            if fileTypes[i] == "Directory":
                items.insert(
                    parent="",
                    index=i,
                    values=(fileTag[i], fileNames[i], fileDateModified[i], fileTypes[i], ""),
                    image=folderIcon,
                    tags=fileTag[i],
                )
            else:
                items.insert(
                    parent="",
                    index=i,
                    values=(fileTag[i], fileNames[i], fileDateModified[i], fileTypes[i], fileSizes[i]),
                    image=fileIcon,
                    tags=fileTag[i],
                )
        except:
            pass
    # --Refresh Browse

    # Draw browse
    items.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    # --Draw browse

    # Refresh Footer
    footer.config(
        text=" "
        + str(len(fileNames))
        + " items | "
        + str(round(fileSizesSum / 1024, 1))
        + " MB Total"
    )
    footer.pack(fill=tk.BOTH)
    # --Refresh Footer

def wrap_refresh(event):  # wrapper for F5 bind
    refresh([])


def previous():
    global lastDirectory
    lastDirectory = os.getcwd()
    os.chdir("../")
    refresh([])


def next():
    try:
        os.chdir(lastDirectory)
        refresh([])
    except:
        return

# open file
def onDoubleClick(event=None):
    global items
    iid = items.focus()
    # iid = items.identify_row(event.y) # old
    if iid == "":  # if double click on blank, don't do anything
        return
    for item in items.selection():
        tempDictionary = items.item(item)
        tempName = tempDictionary["values"][1]  # get first value of dictionary
    try:
        newPath = os.getcwd() + "/" + tempName
        if os.path.isdir(
            newPath
        ):  # if file is directory, open directory else open file
            os.chdir(newPath)
        else:
            os.startfile(newPath)
        refresh([])
    except:
        newPath = newPath.replace(tempName, "")
        os.chdir("../")


def onRightClick(m, event):
    selectItem(event)
    m.tk_popup(event.x_root, event.y_root)


def search(searchEntry, event):
    fileNames = os.listdir()
    query = searchEntry.get()  # get query from text box
    query = query.lower()
    queryNames = []

    for name in fileNames:
        if name.lower().find(query) != -1:  # if query in name
            queryNames.append(name)
    refresh(queryNames)


def create_widgets(window):
    global folderIcon, fileIcon, items, cwdLabel, footer
    s = ttk.Style()
    # Browse Frame
    browseFrame = ttk.Frame(window)
    scroll = ttk.Scrollbar(browseFrame, orient="vertical")
    items = ttk.Treeview(
        browseFrame,
        columns=("Tag", "Name", "Date modified", "Type", "Size"),
        yscrollcommand=scroll.set,
        height=15,
        style="Custom.Treeview",
    )
    items.tag_configure('B', background='#0000FF')
    items.tag_configure('R', background='#FF0000')
    items.tag_configure('G', background='#00FF00')
    items.tag_configure('B', background='#0000FF')
    items.tag_configure('Y', background='#FFFF00')
    items.tag_configure('O', background='#FF7F00')
    items.tag_configure('P', background='#7F007F')
    scroll.config(command=items.yview)  # scroll with mouse drag
    # --Browse Frame

    # Footer Frame
    footerFrame = ttk.Frame(window)
    footer = ttk.Label(footerFrame)
    grip = ttk.Sizegrip(footerFrame, bootstyle="default")
    # --Footer Frame

    folderIcon = tk.PhotoImage(file=file_path + "folder.png", width=20, height=16)
    fileIcon = tk.PhotoImage(file=file_path + "file.png", width=20, height=16)

    # Header Frame
    refreshIcon = tk.PhotoImage(file=file_path + "reload.png")
    backArrowIcon = tk.PhotoImage(file=file_path + "back.png")
    frontArrowIcon = tk.PhotoImage(file=file_path + "next.png")
    headerFrame = ttk.Frame()
    cwdLabel = ttk.Label(
        headerFrame,
        text=" " + os.getcwd(),
        relief="flat",
        # width=110,
    )
    searchEntry = ttk.Entry(headerFrame, width=30, font=("TkDefaultFont", font_size))
    searchEntry.insert(0, "Search files..")
    searchEntry.bind("<Button-1>", partial(click, searchEntry))
    searchEntry.bind("<FocusOut>", partial(FocusOut, searchEntry, window))
    backButton = ttk.Button(
        headerFrame,
        image=backArrowIcon,
        command=previous,
        bootstyle="light",
    )
    forwardButton = ttk.Button(
        headerFrame,
        image=frontArrowIcon,
        command=next,
        bootstyle="light",
    )
    refreshButton = ttk.Button(
        headerFrame,
        command=partial(refresh, []),
        image=refreshIcon,
        bootstyle="light",
    )

    # tooltips for buttons
    ToolTip(backButton, text="Back", bootstyle=("default", "inverse"))
    ToolTip(forwardButton, text="Forward", bootstyle=("default", "inverse"))
    ToolTip(refreshButton, text="Refresh", bootstyle=("default", "inverse"))
    # --Header Frame

    # imgs
    open_img = Image.open(file_path + "icon.png")
    open_photo = ImageTk.PhotoImage(open_img)

    refresh_img = Image.open(file_path + "reload.png")
    refresh_photo = ImageTk.PhotoImage(refresh_img)

    tag_img = Image.open(file_path + "next.png")
    tag_photo = ImageTk.PhotoImage(tag_img)

    untag_img = Image.open(file_path + "back.png")
    untag_photo = ImageTk.PhotoImage(untag_img)

    rename_img = Image.open(file_path + "rename.png")
    rename_photo = ImageTk.PhotoImage(rename_img)

    drive_img = Image.open(file_path + "drive.png")
    drive_photo = ImageTk.PhotoImage(drive_img)

    info_img = Image.open(file_path + "info.png")
    info_photo = ImageTk.PhotoImage(info_img)

    file_img = Image.open(file_path + "file.png")
    file_photo = ImageTk.PhotoImage(file_img)

    dir_img = Image.open(file_path + "folder.png")
    dir_photo = ImageTk.PhotoImage(dir_img)

    copy_img = Image.open(file_path + "copy.png")
    copy_photo = ImageTk.PhotoImage(copy_img)

    paste_img = Image.open(file_path + "paste.png")
    paste_photo = ImageTk.PhotoImage(paste_img)

    delete_img = Image.open(file_path + "delete.png")
    delete_photo = ImageTk.PhotoImage(delete_img)

    # Right click menu
    m = ttk.Menu(window, tearoff=False, font=("TkDefaultFont", font_size))
    m.add_command(
        label="Open",
        image=open_photo,
        compound="left",
        command=onDoubleClick,
    )
    m.add_separator()
    m.add_command(
        label="New file", image=file_photo, compound="left", command=new_file_popup
    )
    m.add_command(
        label="New directory", image=dir_photo, compound="left", command=new_dir_popup
    )
    m.add_separator()
    m.add_command(
        label="Copy Selected",
        image=copy_photo,
        compound="left",
        command=copy,
    )
    m.add_command(
        label="Paste Selected", image=paste_photo, compound="left", command=paste
    )
    m.add_command(
        label="Delete selected",
        image=delete_photo,
        compound="left",
        command=del_file_popup,
    )
    m.add_command(
        label="Rename selected",
        image=rename_photo,
        compound="left",
        command=rename_popup,
    )
    m.add_separator()
    sub_tag = ttk.Menu(window, tearoff=False, font=("TkDefaultFont", font_size))
    sub_tag.add_command(label="1 minitue (Red)", command=partial(tag_popup, "Red"))
    sub_tag.add_command(label="1 hour (Orange)", command=partial(tag_popup, "Orange"))
    sub_tag.add_command(label="1 day (Purple)", command=partial(tag_popup, "Purple"))
    sub_tag.add_command(label="7 day (Yellow)", command=partial(tag_popup, "Yellow"))
    sub_tag.add_command(label="30 day (Green)", command=partial(tag_popup, "Green"))
    m.add_cascade(
        label="Tag selected",
        image=tag_photo,
        compound="left",
        menu=sub_tag,
    )
    m.add_command(
        label="UnTag selected",
        image=untag_photo,
        compound="left",
        command=untag_popup,
    )
    m.add_command(
        label="Delete duplicate",
        image=delete_photo,
        compound="left",
        command=del_dup_popup,
    )
    sub_del_tag = ttk.Menu(window, tearoff=False, font=("TkDefaultFont", font_size))
    sub_del_tag.add_command(label="1 minitue (Red)", command=partial(del_tag_popup, "Minitue"))
    sub_del_tag.add_command(label="1 hour (Orange)", command=partial(del_tag_popup, "Hour"))
    sub_del_tag.add_command(label="1 day (Purple)", command=partial(del_tag_popup, "Day"))
    sub_del_tag.add_command(label="7 day (Yellow)", command=partial(del_tag_popup, "Week"))
    sub_del_tag.add_command(label="30 day (Green)", command=partial(del_tag_popup, "Month"))
    m.add_cascade(
        label="Delete tagged",
        image=delete_photo,
        compound="left",
        menu=sub_del_tag,
    )
    m.add_command(
        label="Show Tagged",
        compound="left",
        command=show_tag_popup,
    )
    m.add_separator()
    m.add_command(
        label="Refresh",
        image=refresh_photo,
        compound="left",
        command=partial(refresh, []),
    )
    # --Right click menu

    s.configure(".", font=("TkDefaultFont", font_size))  # set font size
    s.configure("Treeview", rowheight=28)  # customize treeview
    s.configure(
        "Treeview.Heading", font=("TkDefaultFont", str(int(font_size) + 1), "bold")
    )
    s.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])  # remove borders

    items.column("#0", width=40, stretch=tk.NO)
    items.column("Tag", width=40, stretch=tk.NO)
    items.column("Name", anchor=tk.W, width=150, minwidth=120)
    items.column("Date modified", anchor=tk.CENTER, width=200, minwidth=120)
    items.column("Size", anchor=tk.CENTER, width=80, minwidth=60)
    items.column("Type", anchor=tk.CENTER, width=120, minwidth=60)
    items.heading(
        "Tag",
        text=" ",
        anchor=tk.CENTER,
        command=partial(sort_col, "Tag", False),
    )
    items.heading(
        "Name",
        text="Name",
        anchor=tk.CENTER,
        command=partial(sort_col, "Name", False),
    )
    items.heading(
        "Date modified",
        text="Date modified",
        anchor=tk.CENTER,
        command=partial(sort_col, "Date modified", False),
    )
    items.heading(
        "Type",
        text="Type",
        anchor=tk.CENTER,
        command=partial(sort_col, "Type", False),
    )
    items.heading(
        "Size",
        text="Size",
        anchor=tk.CENTER,
        command=partial(sort_col, "Size", False),
    )
    items.bind(
        "<Double-1>",
        onDoubleClick,
    )  # command on double click
    items.bind("<ButtonRelease-1>", selectItem)
    items.bind("<Button-3>", partial(onRightClick, m))  # command on right click
    items.bind("<Up>", up_key)  # bind up arrow key
    items.bind("<Down>", down_key)  # bind down arrow key
    # --Browse Frame

    # Menu bar
    bar = ttk.Menu(window, font=("TkDefaultFont", font_size))
    window.config(menu=bar)

    file_menu = ttk.Menu(bar, tearoff=False, font=("TkDefaultFont", font_size))
    file_menu.add_command(
        label="Open",
        image=open_photo,
        compound="left",
        command=onDoubleClick,
    )
    file_menu.add_command(
        label="New file",
        image=file_photo,
        compound="left",
        command=new_file_popup,
    )
    file_menu.add_command(
        label="New directory", image=dir_photo, compound="left", command=new_dir_popup
    )
    file_menu.add_separator()
    file_menu.add_command(
        label="Copy Selected",
        image=copy_photo,
        compound="left",
        command=copy,
    )
    file_menu.add_command(
        label="Paste Selected", image=paste_photo, compound="left", command=paste
    )
    file_menu.add_command(
        label="Delete selected",
        image=delete_photo,
        compound="left",
        command=del_file_popup,
    )
    file_menu.add_command(
        label="Rename selected",
        image=rename_photo,
        compound="left",
        command=rename_popup,
    )
    file_menu.add_separator()
    sub_tag = ttk.Menu(window, tearoff=False, font=("TkDefaultFont", font_size))
    sub_tag.add_command(label="1 minitue (Red)", command=partial(tag_popup, "Red"))
    sub_tag.add_command(label="1 hour (Orange)", command=partial(tag_popup, "Orange"))
    sub_tag.add_command(label="1 day (Purple)", command=partial(tag_popup, "Purple"))
    sub_tag.add_command(label="7 day (Yellow)", command=partial(tag_popup, "Yellow"))
    sub_tag.add_command(label="30 day (Green)", command=partial(tag_popup, "Green"))
    file_menu.add_cascade(
        label="Tag selected",
        image=tag_photo,
        compound="left",
        menu=sub_tag,
    )
    file_menu.add_command(
        label="UnTag selected",
        image=untag_photo,
        compound="left",
        command=untag_popup,
    )
    file_menu.add_command(
        label="Delete duplicate",
        image=delete_photo,
        compound="left",
        command=del_dup_popup,
    )
    sub_del_tag = ttk.Menu(window, tearoff=False, font=("TkDefaultFont", font_size))
    sub_del_tag.add_command(label="1 minitue (Red)", command=partial(del_tag_popup, "Minitue"))
    sub_del_tag.add_command(label="1 hour (Orange)", command=partial(del_tag_popup, "Hour"))
    sub_del_tag.add_command(label="1 day (Purple)", command=partial(del_tag_popup, "Day"))
    sub_del_tag.add_command(label="7 day (Yellow)", command=partial(del_tag_popup, "Week"))
    sub_del_tag.add_command(label="30 day (Green)", command=partial(del_tag_popup, "Month"))
    file_menu.add_cascade(
        label="Delete tagged",
        image=delete_photo,
        compound="left",
        menu=sub_del_tag,
    )
    file_menu.add_command(
        label="Show Tagged",
        compound="left",
        command=show_tag_popup,
    )
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=window.destroy)

    drives_menu = ttk.Menu(bar, tearoff=False, font=("TkDefaultFont", font_size))
    for drive in available_drives:
        drives_menu.add_command(
            label=drive,
            image=drive_photo,
            compound="left",
            command=partial(cd_drive, drive, []),
        )

    help_menu = ttk.Menu(bar, tearoff=False, font=("TkDefaultFont", font_size))
    help_menu.add_command(
        label="Keybinds", image=info_photo, compound="left", command=keybinds
    )
    about_menu = ttk.Menu(bar, tearoff=False, font=("TkDefaultFont", font_size))
    about_menu.add_command(
        label="About the app", command=about_popup, image=info_photo, compound="left"
    )

    bar.add_cascade(label="File", menu=file_menu, underline=0)
    bar.add_cascade(label="Drives", menu=drives_menu, underline=0)
    bar.add_cascade(label="Help", menu=help_menu, underline=0)
    bar.add_cascade(label="About", menu=about_menu, underline=0)
    # --Menu bar

    # packs
    scroll.pack(side=tk.RIGHT, fill=tk.BOTH)
    backButton.pack(side=tk.LEFT, padx=5, pady=10, fill=tk.BOTH)
    forwardButton.pack(side=tk.LEFT, padx=5, pady=10, fill=tk.BOTH)
    cwdLabel.pack(side=tk.LEFT, padx=5, pady=10, fill=tk.BOTH, expand=True)
    refreshButton.pack(side=tk.LEFT, padx=1, pady=10, fill=tk.BOTH)
    searchEntry.pack(side=tk.LEFT, padx=5, pady=10, fill=tk.BOTH)
    grip.pack(side=tk.RIGHT, fill=tk.BOTH, padx=2, pady=2)

    headerFrame.pack(fill=tk.X)
    browseFrame.pack(fill=tk.BOTH, expand=True)
    footerFrame.pack(side=tk.BOTTOM, fill=tk.BOTH)

    searchEntry.bind(
        "<Return>",
        partial(search, searchEntry),
    )  # on enter press, run search1

    # img references
    photo_ref.append(backArrowIcon)
    photo_ref.append(frontArrowIcon)
    photo_ref.append(refreshIcon)
    photo_ref.append(open_photo)
    photo_ref.append(refresh_photo)
    photo_ref.append(tag_photo)
    photo_ref.append(untag_photo)
    photo_ref.append(rename_photo)
    photo_ref.append(drive_photo)
    photo_ref.append(info_photo)
    photo_ref.append(file_photo)
    photo_ref.append(dir_photo)
    photo_ref.append(copy_photo)
    photo_ref.append(paste_photo)
    photo_ref.append(delete_photo)

    # wrappers for keybinds
    window.bind("<F5>", wrap_refresh)
    window.bind("<Delete>", wrap_del)
    window.bind("<Control-c>", wrap_copy)
    window.bind("<Control-v>", wrap_paste)
    window.bind("<Control-Shift-N>", wrap_new_dir)


def sort_col(col, reverse):
    global items
    l = [(items.set(k, col), k) for k in items.get_children("")]
    if col == "Name" or col == "Type":
        l.sort(reverse=reverse)
    elif col == "Date modified":
        l = sorted(l, key=sort_key_dates, reverse=reverse)
    elif col == "Size":
        l = sorted(l, key=sort_key_size, reverse=reverse)

    # rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        items.move(k, "", index)

    # reverse sort next time
    items.heading(col, command=partial(sort_col, col, not reverse))


def sort_key_dates(item):
    return datetime.strptime(item[0], "%d-%m-%Y %I:%M")


def sort_key_size(item):
    num_size = item[0].split(" ")[0]
    if num_size != "":
        return int(num_size)
    else:
        return -1  # if it's a directory, give it negative size value, for sorting


def update_tag():
    with open(file_path + "../res/tag_files.json", 'w') as outfile:
        # Writing to file
        data={}
        data['items']  = tag_files
        json.dump(data, outfile)

def cd_drive(drive, queryNames):
    global fileNames, currDrive, cwdLabel
    cwdLabel.config(text=" " + drive)
    currDrive = drive
    fileNames = os.listdir(currDrive)
    os.chdir(currDrive + "/")
    refresh(queryNames)

def up_key(event):
    global selectedItem, items
    iid = items.focus()
    iid = items.prev(iid)
    if iid:
        items.selection_set(iid)
        selectedItem = items.item(iid)["values"][1]
        # print(selectedItem)
    else:
        pass


def down_key(event):
    global selectedItem, items
    iid = items.focus()
    iid = items.next(iid)
    if iid:
        items.selection_set(iid)
        selectedItem = items.item(iid)["values"][1]
        # print(selectedItem)
    else:
        pass


def click(searchEntry, event):
    if searchEntry.get() == "Search files..":
        searchEntry.delete(0, "end")


def FocusOut(searchEntry, window, event):
    searchEntry.delete(0, "end")
    searchEntry.insert(0, "Search files..")
    window.focus()


def rename_popup():
    global items
    if items.focus() != "":
        try:
            name = Querybox.get_string(prompt="Name: ", title="Rename")
            old = os.getcwd() + "/" + selectedItem
            os.rename(old, name)
            refresh([])
        except:
            pass
    else:
        Messagebox.show_info(
            message="There is no selected file or directory.", title="Info"
        )

def tag_popup(tag_type):
    global items
    if items.focus() != "":
        try:
            selected = os.getcwd() + "\\" + selectedItem
            found=False
            for file in tag_files:
                if file['file_name'] == selected:
                    found = True
            if not found:
                new_item = {}
                new_item['file_name'] = selected
                new_item['tag_date'] = datetime.now().strftime(date_format)
                new_item['tag_type'] = tag_type
                tag_files.append(new_item)
                update_tag()
                refresh([])
        except:
            pass
    else:
        Messagebox.show_info(
            message="There is no selected file or directory.", title="Info"
        )

def untag_popup():
    global items
    if items.focus() != "":
        try:
            selected = os.getcwd() + "\\" + selectedItem
            found=False
            for file in tag_files:
                if file['file_name'] == selected:
                    found = True
                    founditem = file
            if found:
                tag_files.remove(founditem)
                update_tag()
                refresh([])
        except:
            pass
    else:
        Messagebox.show_info(
            message="There is no selected file or directory.", title="Info"
        )

def selectItem(event):
    global selectedItem, items
    # selectedItemID = items.focus()
    iid = items.identify_row(event.y)
    if iid:
        items.selection_set(iid)
        selectedItem = items.item(iid)["values"][1]
        # print(selectedItem)
        items.focus(iid)  # Give focus to iid
    else:
        pass


def keybinds():
    Messagebox.ok(
        message="Copy - <Control + C>\nPaste - <Control + V>\nDelete - <Del>\n"
        + "New Directory - <Control + Shift + N>\nRefresh - <F5>\n"
        + "Select up - <Arrow key up>\nSelect down - <Arrow key down>",
        title="Info",
    )

def show_tag_popup():  # popup window
    str_files_Red = ''
    str_files_Green = ''
    str_files_Yellow = ''
    str_files_Orange = ''
    str_files_Purple = ''
    for file in tag_files:
        if file['tag_type'] == 'Red':
            str_files_Red += file['file_name'] + '\n'
        elif file['tag_type'] == 'Green':
            str_files_Green += file['file_name'] + '\n'
        elif file['tag_type'] == 'Yellow':
            str_files_Yellow += file['file_name'] + '\n'
        elif file['tag_type'] == 'Orange':
            str_files_Orange += file['file_name'] + '\n'
        elif file['tag_type'] == 'Purple':
            str_files_Purple += file['file_name'] + '\n'
    Messagebox.ok(
        message=f'Red:\n {str_files_Red}Orange:\n {str_files_Orange}Purple:\n {str_files_Purple}Yellow:\n {str_files_Yellow}Green:\n {str_files_Green}',
        title="Show Tagged files",
    )

def about_popup():  # popup window
    Messagebox.ok(
        message="My File Explorer\nVersion 1.0.0",
        title="About",
    )


def new_file_popup():
    name = Querybox.get_string(prompt="Name: ", title="New file")
    if name != "":
        try:
            f = open(os.getcwd() + "/" + name, "x")
            f.close()
            refresh([])
        except:
            pass


def new_dir_popup():
    name = Querybox.get_string(prompt="Name: ", title="New directory")
    if name != "":
        try:
            os.mkdir(os.getcwd() + "/" + name)
            refresh([])
        except:
            pass


def wrap_new_dir(event):
    new_dir_popup()


def copy():
    global src, items
    if items.focus() != "":  # if there is a focused item
        src = os.getcwd() + "/" + selectedItem


def wrap_copy(event):  # wrapper for ctrl+c keybinds
    copy()


def wrap_paste(event):  # wrapper for ctrl+v keybinds
    paste()


def paste():
    global src
    dest = os.getcwd() + "/"
    if not os.path.isdir(src) and src != "":
        try:
            t1 = threading.Thread(
                target=shutil.copy2, args=(src, dest)
            )  # use threads so gui does not hang on large file copy
            t2 = threading.Thread(target=paste_popup, args=([t1]))
            t1.start()
            t2.start()
        except:
            pass
    elif os.path.isdir(src) and src != "":
        try:
            new_dest_dir = os.path.join(dest, os.path.basename(src))
            os.makedirs(new_dest_dir)
            t1 = threading.Thread(  # use threads so gui does not hang on large directory copy
                target=shutil.copytree,
                args=(src, new_dest_dir, False, None, shutil.copy2, False, True),
            )
            t2 = threading.Thread(target=paste_popup, args=([t1]))
            t1.start()
            t2.start()
        except:
            pass


def paste_popup(t1):
    top = ttk.Toplevel(title="Progress")
    top.geometry("250x50")
    top.resizable(False, False)

    gauge = ttk.Floodgauge(
        top, bootstyle="success", mode="indeterminate", text="Copying files.."
    )
    gauge.pack(fill=tk.BOTH, expand=tk.YES)
    gauge.start()
    t1.join()
    refresh([])
    top.destroy()


def del_file_popup():
    global items
    if items.focus() != "":  # if there is a focused item
        answer = Messagebox.yesno(
            message="Are you sure?\nThis file/directory will be deleted permanently.",
            alert=True,
        )
        if answer == "Yes":
            del_file(None)
            refresh([])
        else:
            return
    else:
        Messagebox.show_info(
            message="There is no selected file or directory.", title="Info"
        )

def del_dup_popup():
    dup_items = []
    fileNames = os.listdir(os.getcwd())
    for name1 in fileNames:
        for name2 in fileNames:
            for postfix in [' - Copy', ' - Copy (2)', ' - Copy (3)', ' - Copy (4)', ' - Copy (5)', ' - Copy (6)', ' - Copy (7)', ' - Copy (8)', ' - Copy (9)', ' - Copy (10)'
                            , ' (1)', ' (2)', ' (3)', ' (4)', ' (5)', ' (6)', ' (7)', ' (8)', ' (9)', ' (10)']:
                if name1.split('.', maxsplit=1)[0] == name2.split('.', maxsplit=1)[0] + postfix:
                    if name1 not in dup_items:
                        dup_items.append(name1)
    if dup_items:
        for dup_item in dup_items:
            answer = Messagebox.yesno(
                message=f"Are you sure?\n{dup_item} will be deleted permanently.",
                alert=True,
            )
            if answer == "Yes":
                del_file(os.getcwd() + "/" + dup_item)
            refresh([])
    else:
        Messagebox.show_info(
            message="There is no duplicate file or directory.", title="Info"
        )

def del_tag_popup(del_upto):
    if tag_files:
        delta = 0
        if del_upto == "Minitue":
            delta = timedelta(minutes=1)    
        elif del_upto == "Hour":
            delta = timedelta(hours=1)    
        elif del_upto == "Day":
            delta = timedelta(days=1)    
        elif del_upto == "Week":
            delta = timedelta(days=7)    
        elif del_upto == "Month":
            delta = timedelta(days=30)    
        for tag_item in tag_files:
            del_upto_date = datetime.strptime(tag_item['tag_date'],date_format)
            if datetime.now() >= del_upto_date + delta:
                f_n = tag_item["file_name"]
                answer = Messagebox.yesno(
                    message=f"Are you sure?\n{f_n} will be deleted permanently.",
                    alert=True,
                )
                if answer == "Yes":
                    del_file(f_n)
                    tag_files.remove(tag_item)
        update_tag()
        refresh([])
    else:
        Messagebox.show_info(
            message="There is no tagged file or directory.", title="Info"
        )

def wrap_del(event):  # wrapper for delete keybind
    del_file_popup(None)


def del_file(file_name:str):
    if not file_name:
        file_name = os.getcwd() + "/" + selectedItem
    if os.path.isfile(file_name):
        os.remove(file_name)
    elif os.path.isdir(file_name):
        # os.rmdir(os.getcwd() + "/" + selectedItem)
        shutil.rmtree(file_name)


def read_tag():
    global tag_files
    if not os.path.isdir(file_path + "../res"):
        os.mkdir(file_path + "../res") 
    if not os.path.isfile(file_path + "../res/tag_files.json"):
        with open(file_path + "../res/tag_files.json", 'w') as outfile:
            # Writing to file
            data={}
            data['items']  = []
            json.dump(data, outfile)
    
    with open(file_path + "../res/tag_files.json", 'r') as openfile:
     # Reading from json file
        data  = json.load(openfile)
        tag_files = data['items']

def main():
    global theme
    global file_path
    file_path = os.path.join(os.path.dirname(__file__), "../icons/")
    checkPlatform()
    theme = "superhero"
    root = createWindow()

    create_widgets(root)
    read_tag()
    refresh([])
    root.mainloop()


if __name__ == "__main__":
    main()
