# GUI app for managing a list of links to send to the clipboard or archive.today. LGPL 3.0 or later license
import os
import tkinter as tk
import pyperclip3 as pc
import urllib.parse
import webbrowser
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import scrolledtext

oldtitle = "newqueue"

def instruct():
    messagebox.showinfo(message='Send to: Moves the top link to the entry field and either copies it to clipboard for you to paste, or opens up a browser tab for archive.today to submit the given link.')

def about():
    messagebox.showinfo(message='By AceOfSpadesProduc100, made with Tkinter. Licensed under the GNU LGPL 3.0 or later.')

def confirmsaved():
    if linkbox.edit_modified():
        response = messagebox.askyesnocancel(message="You have unsaved changes. Do you want to save?")
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
    f = filedialog.asksaveasfile(mode='w', defaultextension=".txt", filetypes=[("Text files", ".txt")], initialfile=oldtitle)
    if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
        return
    text2save = str(linkbox.get("1.0", "end-1c")) # starts from `1.0`, not `0.0`
    f.write(text2save)
    
    oldtitle = os.path.basename(f.name)
    f.close() # `()` was missing.
    linkbox.edit_modified(False)
    return True

def openfile():
    global oldtitle
    if confirmsaved() is True:
        file = filedialog.askopenfile(mode='rt', defaultextension=".txt", filetypes=[("Text files", ".txt")])
        if file is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        linkbox.delete("1.0", "end")
        contents = file.read()
        linkbox.insert('1.0', contents)
        linkbox.edit_modified(False)
        entry_text.set("")
        window.title(os.path.abspath(file.name))
        oldtitle = os.path.basename(file.name)
        file.close()

def newfile():
    if confirmsaved() is True:
        linkbox.delete("1.0", "end")
        entry_text.set("")

def sendline():
    if sendmode.current() == 0:
        pc.copy(linkbox.get("1.0", "1.0 + 1 lines"))
    else:
        webbrowser.open("https://archive.today/?run=1&url=" + urllib.parse.quote(linkbox.get("1.0", "1.0 + 1 lines"), safe="!~*'()"))
    print(linkbox.get("1.0", "1.0 + 1 lines"))
    entry_text.set(linkbox.get("1.0", "1.0 + 1 lines"))
    linkbox.delete("1.0", "1.0 + 1 lines")
    

def savefile():
    discard = save()

window = tk.Tk()
window.geometry('')
window.title("Art queue maker")

window.resizable(True, True)
window.columnconfigure(0, weight=1)
window.rowconfigure(1, weight=1)

buttons_frame = tk.Frame(window)
buttons_frame.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N)

leftframe = ttk.Frame(window)
leftframe.rowconfigure(0, weight=1)
leftframe.columnconfigure(0, weight=1)
leftframe.grid(row=1, column=0, padx=10, pady=10, sticky=tk.E+tk.W+tk.N+tk.S)

bottomframe = ttk.Frame(window)
bottomframe.grid(row=2, column=0, sticky=tk.W+tk.E)

entry_text = tk.StringVar()
entry = ttk.Entry(leftframe, textvariable=entry_text)
linkbox = scrolledtext.ScrolledText(leftframe, undo=True)
entry.grid(column=0, row=0, sticky=tk.W+tk.E+tk.N)
linkbox.grid(column=0, row=0, pady=20, sticky=tk.E+tk.W+tk.N+tk.S)

sendbutton = ttk.Button(bottomframe, text="Send to:", command=sendline).grid(row=0, column=0, padx=(10), pady=10)

sm = tk.StringVar()
sendmode = ttk.Combobox(bottomframe, width=32, textvariable=sm, state="readonly")
sendmode['values'] = ('Clipboard (hold CTRL and press V to paste)', 'archive.today')
sendmode.current(0)
sendmode.grid(column=1, row=0, padx=10, pady=12)

newbutton = ttk.Button(buttons_frame, text="New file", command=newfile).grid(row=0, column=0, padx=(10), pady=10)
openbutton = ttk.Button(buttons_frame, text="Open", command=openfile).grid(row=0, column=1, padx=(10), pady=10)
savebutton = ttk.Button(buttons_frame, text="Save", command=savefile).grid(row=0, column=2, padx=(10), pady=10)

window.protocol("WM_DELETE_WINDOW", on_closing)

window.mainloop()
