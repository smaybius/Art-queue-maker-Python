# GUI app for managing a list of links to send to the clipboard or archive.today. LGPL 3.0 or later license
import os
import tkinter as tk
import urllib.parse
import webbrowser
from threading import Thread
from time import sleep
from tkinter import filedialog, messagebox, scrolledtext, ttk

import pyperclip as pc

oldtitle = "newqueue"
currenttitle = "Art queue maker"


def instruct():
    messagebox.showinfo(
        message="Send to: Moves the top link to the entry field and either copies it to clipboard for you to paste, or opens up a browser tab for archive.today to submit the given link."
    )


def about():
    messagebox.showinfo(
        message="By AceOfSpadesProduc100, made with Tkinter. Licensed under the GNU LGPL 3.0 or later."
    )


def confirmsaved():
    if linkbox.edit_modified():
        response = messagebox.askyesnocancel(
            message="You have unsaved changes. Do you want to save?"
        )
        if response:
            if save() is True:
                return True
            else:
                return False
        elif response is None:
            return False
        elif not response:
            return True
    else:
        return True


def on_closing():
    if confirmsaved() is True:
        window.destroy()
    else:
        return


def save():
    global oldtitle
    f = filedialog.asksaveasfile(
        mode="w",
        defaultextension=".txt",
        filetypes=[("Text files", ".txt")],
        initialfile=oldtitle,
    )
    if f is None:  # asksaveasfile return `None` if dialog closed with "cancel".
        return False
    text2save = str(linkbox.get("1.0", "end-1c"))  # starts from `1.0`, not `0.0`
    f.write(text2save)

    oldtitle = os.path.basename(f.name)
    currenttitle = os.path.abspath(f.name)
    window.title(currenttitle)
    f.close()  # `()` was missing.
    linkbox.edit_modified(False)
    return True


def openfile():
    global oldtitle
    if confirmsaved() is True:
        file = filedialog.askopenfile(
            mode="rt", defaultextension=".txt", filetypes=[("Text files", ".txt")]
        )
        if file is None:  # asksaveasfile return `None` if dialog closed with "cancel".
            return
        linkbox.delete("1.0", "end")
        contents = file.read()
        linkbox.insert("1.0", contents)
        linkbox.edit_modified(False)
        entry_text.set("")
        currenttitle = os.path.abspath(file.name)
        window.title(currenttitle)
        oldtitle = os.path.basename(file.name)
        file.close()


def newfile():
    if confirmsaved() is True:
        linkbox.delete("1.0", "end")
        entry_text.set("")


def sendline():
    if sendmode.current() == 0:
        pc.copy(linkbox.get("1.0", "1.0 + 1 lines"))
    elif sendmode.current() == 1:
        webbrowser.open("https://archive.is/submit/?url=" + urllib.parse.quote(linkbox.get("1.0", "1.0 + 1 lines"), safe="!~*'()"))
    elif sendmode.current() == 2:
        webbrowser.open("https://ghostarchive.org/search?term=" + urllib.parse.quote(linkbox.get(linkbox.get("1.0", "1.0 + 1 lines"), safe="!~*'()")))
    print(linkbox.get("1.0", "1.0 + 1 lines"))
    entry_text.set(linkbox.get("1.0", "1.0 + 1 lines"))
    linkbox.delete("1.0", "1.0 + 1 lines")


def savefile():
    save()


def threadedarchive():
    while tickvar.get() == 1 and len(linkbox.get("1.0", "end-1c")) != 0:
        webbrowser.open("https://archive.is/submit/?url=" + urllib.parse.quote(linkbox.get("1.0", "1.0 + 1 lines"), safe="!~*'()"))
        print(linkbox.get("1.0", "1.0 + 1 lines"))
        entry_text.set(linkbox.get("1.0", "1.0 + 1 lines"))
        linkbox.delete("1.0", "1.0 + 1 lines")
        sleep(float(delayseconds.get()))
    tickvar.set(0)

def autoarchive():
    thread = Thread(target = threadedarchive)
    thread.start()
    thread.join()

def update_title():
    """
    Updates the title of the window to end with the number of lines in linkbox.
    """
    num_lines = int(linkbox.index('end-1c').split('.')[0])  # Get the number of lines
    window.title(f"{currenttitle} ({num_lines} lines)")
    window.after(500, update_title)  # Schedule this function to run again in 500ms



window = tk.Tk()
window.geometry("")
window.title("Art queue maker")

window.resizable(True, True)
window.columnconfigure(0, weight=1)
window.rowconfigure(1, weight=1)

buttons_frame = tk.Frame(window)
buttons_frame.grid(row=0, column=0, sticky=tk.W + tk.E + tk.N)

leftframe = ttk.Frame(window)
leftframe.rowconfigure(0, weight=1)
leftframe.columnconfigure(0, weight=1)
leftframe.grid(row=1, column=0, padx=10, pady=10, sticky=tk.E + tk.W + tk.N + tk.S)

bottomframe = ttk.Frame(window)
bottomframe.grid(row=2, column=0, sticky=tk.W + tk.E)

entry_text = tk.StringVar()
entry = ttk.Entry(leftframe, textvariable=entry_text)
linkbox = scrolledtext.ScrolledText(leftframe, undo=True)
entry.grid(column=0, row=0, sticky=tk.W + tk.E + tk.N)
linkbox.grid(column=0, row=0, pady=20, sticky=tk.E + tk.W + tk.N + tk.S)

sendbutton = ttk.Button(bottomframe, text="Send to:", command=sendline).grid(
    row=0, column=0, padx=(10), pady=10
)

sm = tk.StringVar()
sendmode = ttk.Combobox(bottomframe, width=16, textvariable=sm, state="readonly")
sendmode["values"] = ("Clipboard (hold CTRL and press V to paste)", "archive.today", "ghostarchive")
sendmode.current(0)
sendmode.grid(column=1, row=0, padx=10, pady=12)

tickvar = tk.IntVar(value=0)
archivetick = ttk.Checkbutton(
    bottomframe,
    text="Auto archive.today in seconds:",
    variable=tickvar,
    onvalue=1,
    offvalue=0,
    command=lambda: Thread(target=autoarchive).start(),
)
archivetick.grid(column=2, row=0, padx=10, pady=12)

my_var = tk.StringVar(window)
my_var.set("1")
delayseconds = ttk.Spinbox(
    bottomframe, from_=1, to=60, text="Delay (in s)", textvariable=my_var, width=2
)
delayseconds.grid(column=3, row=0, padx=10, pady=12)

newbutton = ttk.Button(buttons_frame, text="New file", command=newfile).grid(
    row=0, column=0, padx=(10), pady=10
)
openbutton = ttk.Button(buttons_frame, text="Open", command=openfile).grid(
    row=0, column=1, padx=(10), pady=10
)
savebutton = ttk.Button(buttons_frame, text="Save", command=savefile).grid(
    row=0, column=2, padx=(10), pady=10
)

# Call the update_title function during initialization
update_title()

window.protocol("WM_DELETE_WINDOW", on_closing)

window.mainloop()
