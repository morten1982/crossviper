import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import font
from pygments import lex
from pygments.lexers import PythonLexer
import threading
import platform
import os
import sys
import time
import re
import shutil
import subprocess
import configparser
import zipfile
from codeeditor import TextLineNumbers, TextPad
from configuration import Configuration
from dialog import (SettingsDialog, ViewDialog, 
                    InfoDialog, NewDirectoryDialog, HelpDialog,
                    GotoDialog)

###################################################################
class RunThread(threading.Thread):
    def __init__(self, command):
        super().__init__()
        self.command = command
    
    def run(self):
        try:
            os.system(self.command)
        except Exception as e:
            print(str(e))

###################################################################
class ToolTip():
    def __init__(self, widget):
        self.widget = widget
        self.tipWindow = None
        self.id = None
        self.x = self.y = 0
    
    def showtip(self, text):
        self.text = text
        if self.tipWindow or not self.text:
            return
        x, y, _cx, cy = self.widget.bbox('insert')
        x = x + self.widget.winfo_rootx() + 0
        y = y + cy + self.widget.winfo_rooty() + 40
        self.tipWindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry('+%d+%d' % (x, y))
        
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background='#ffffe0', relief=tk.SOLID, borderwidth=1)
        label.pack(ipadx=1)
     
    def hidetip(self):
        tw = self.tipWindow
        self.tipWindow = None
        if tw:
            tw.destroy()
    
        
###################################################################

class LeftPanel(tk.Frame):
    '''
        LeftPanel ... containing treeView, leftButtonFrame, Buttons 
    '''
    def __init__(self, master=None, rightPanel=None):
        super().__init__(master)
        self.master = master
        self.rightPanel = rightPanel
        self.pack()
        
        self.initUI()
        
        self.clipboard = ''
    
    def initUI(self):
        path = os.path.abspath(__file__)
        pathList = path.replace('\\', '/')
        pathList = path.split('/')[:-1]
        print(pathList)
        self.dir = ''
        for item in pathList:
       	    self.dir += item + '/'
        
        print('directory: ' + self.dir)
        leftButtonFrame = tk.Frame(self, height=25, bg='gray')
        leftButtonFrame.pack(side=tk.TOP, fill=tk.X)

        # TreeView
        from os.path import expanduser
        path = expanduser("~")
        os.chdir(path)
        #path = '.'
        self.tree = ttk.Treeview(self)

        #self.tree.heading('#0', text='<-', anchor='w')
        #self.tree.heading('#0', text='Name')
        self.tree['show'] = 'tree'
        self.tree.bind("<Double-1>", self.OnDoubleClickTreeview)
        self.tree.bind("<Button-1>", self.OnClickTreeview)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind("<ButtonRelease-3>", self.treePopUp)


        abspath = os.path.abspath(path)
        root_node = self.tree.insert('', 'end', text=abspath, open=True)
        self.process_directory(root_node, abspath)

        self.tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        # Buttons
        infoIcon = tk.PhotoImage(file=self.dir + 'images/info-file.png')
        infoButton = ttk.Button(leftButtonFrame, image=infoIcon, command=self.infoFile)
        infoButton.image = infoIcon
        infoButton.pack(side=tk.LEFT)
        self.createToolTip(infoButton, 'Show Information')

        newFolderIcon = tk.PhotoImage(file=self.dir + 'images/new-folder.png')
        newFolderButton = ttk.Button(leftButtonFrame, image=newFolderIcon, command=self.newFolder)
        newFolderButton.image = newFolderIcon
        newFolderButton.pack(side=tk.LEFT)
        self.createToolTip(newFolderButton, 'Create New Folder')

        copyFileIcon = tk.PhotoImage(file=self.dir + 'images/copy-file.png')
        copyFileButton = ttk.Button(leftButtonFrame, image=copyFileIcon, command=self.copyFile)
        copyFileButton.image = copyFileIcon
        copyFileButton.pack(side=tk.LEFT)
        self.createToolTip(copyFileButton, 'Copy Item')

        pasteFileIcon = tk.PhotoImage(file=self.dir + 'images/paste-file.png')
        pasteFileButton = ttk.Button(leftButtonFrame, image=pasteFileIcon, command=self.pasteFile)
        pasteFileButton.image = pasteFileIcon
        pasteFileButton.pack(side=tk.LEFT)
        self.createToolTip(pasteFileButton, 'Paste Item')

        deleteFileIcon = tk.PhotoImage(file=self.dir + 'images/delete-file.png')
        deleteFileButton = ttk.Button(leftButtonFrame, image=deleteFileIcon, command=self.deleteFile)
        deleteFileButton.image = deleteFileIcon
        deleteFileButton.pack(side=tk.LEFT)
        self.createToolTip(deleteFileButton, 'Delete Item')

        self.selected = []
        self.sourceItem = None
        self.destinationItem = None
        

    def createToolTip(self, widget, text):
        toolTip = ToolTip(widget)
        def enter(event):
            toolTip.showtip(text)
        def leave(event):
            toolTip.hidetip()
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)
        
    
    def process_directory(self, parent, path):
        try:
            l = []
            for p in os.listdir(path):
                abspath = os.path.join(path, p)
                isdir = os.path.isdir(abspath)

                if isdir:
                    item = '> /' + str(p)
                    l.append(item)
                    continue
                    
                else:
                    item = str(p)
                    l.append(item)
                
                # list sort ...
            l.sort()
            #l.reverse()
            
            for items in l:
                self.tree.insert(parent, 'end', text=str(items), open=False)
       
        except Exception as e:
            tk.messagebox.showerror('Error', str(e))
            return
        
    def OnClickTreeview(self, event):
        item = self.tree.identify('item',event.x,event.y)
        if '/' in self.tree.item(item,"text") or '\\' in self.tree.item(item, "text"):
            self.master.master.master.title(self.checkPath(self.tree.item(item, 'text')))
                
        else:
            dir = self.checkPath(os.getcwd())
            self.master.master.master.title(dir + '/' + self.checkPath(self.tree.item(item, 'text')))
        #print(item)
    
    def ignore(self, event):
        # workaround for dismiss OnDoubleClickTreeview to open file twice 
        # step 1
        return 'break'

    def OnDoubleClickTreeview(self, event):
        item = self.tree.identify('item',event.x,event.y)
        #print("you clicked on", self.tree.item(item,"text"))
        if self.tree.item(item, "text") == '': 

            d = os.getcwd()
            d = self.checkPath(d)
            directory = filedialog.askdirectory(initialdir=d)
            if not directory:
                return
            try:
                os.chdir(directory)
                for i in self.tree.get_children():
                    self.tree.delete(i)
                path = '.'
                abspath = os.path.abspath(path)
                root_node = self.tree.insert('', 'end', text=abspath, open=True)
                self.process_directory(root_node, abspath)
                
            except Exception as e:
                tk.messagebox.showerror('Error', str(e))
                return
        
        elif self.tree.item(item, "text").startswith('>'):
            root = os.getcwd()
            sub = self.tree.item(item, "text").split()[1]
            dir = root + sub
            dir = self.checkPath(dir)
            try:
                os.chdir(dir)
            except Exception as e:
                tk.messagebox.showerror('Error', str(e))

            self.selected = None
            self.refreshTree()
            self.master.master.master.title(dir)
    
        elif '/' in self.tree.item(item, "text") or '\\' in self.tree.item(item, "text"):
            os.chdir('..')
            self.refreshTree()
            dir = self.checkPath(os.getcwd())
            self.master.master.master.title(dir)

            return 'break'

        else:
            file = self.tree.item(item,"text")
            dir = os.getcwd()
            dir = self.checkPath(dir)
            filename = dir + '/' + file
            self.tree.config(cursor="X_cursor")
            self.tree.bind('<Double-1>', self.ignore)

            self.master.master.rightPanel.open(file=filename)
            self.tree.config(cursor='')
            self.tree.update()
            self.rightPanel.textPad.mark_set("insert", "1.0")
            self.master.master.master.title(filename)
            self.rightPanel.textPad.focus_set()
            
            # workaround 
            # step 2
            self.tree.after(1000, self.bindit)
    
    def bindit(self):
        # workaround 
        # step 3
        self.tree.bind('<Double-1>', self.OnDoubleClickTreeview)

    def checkPath(self, path):
        if '\\' in path:
            path = path.replace('\\', '/')
        return path

    def on_select(self, event):
        self.selected = event.widget.selection()
    
    def infoFile(self):
        rootDir = self.checkPath(os.getcwd())
        #print(rootDir)
        directory = None
        file = None
        size = None
        if self.selected:
            for idx in self.selected:
                try:
                    text = self.tree.item(idx)['text']
                except:
                    self.selected = []
                    return
            if '/' in text or '\\' in text:
                directory = True
            else:
                file = True
            if file == True:
                filename = rootDir + '/' + text
                size = os.path.getsize(filename)
                size = format(size, ',d')
            else:
                filename = text
            text = self.checkPath(text)
            InfoDialog(self, title='Info', text=text, directory=directory, file=file, size=size)
        
        else:
            return
        

    def refreshTree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        path = '.'
        abspath = os.path.abspath(path)
        root_node = self.tree.insert('', 'end', text=abspath, open=True)
        self.process_directory(root_node, abspath)

    def newFolder(self):
        NewDirectoryDialog(self, title='Create directory')
        self.refreshTree()
        
    def copyFile(self):
        if not self.selected:
            self.clipboard = ''
            return
        else:
            for idx in self.selected:
                text = self.tree.item(idx)['text']
        
        self.clipboard = text
        self.homedir = self.checkPath(os.getcwd())
        
        if self.clipboard.startswith('>'):
            dir = self.clipboard.split()[1]
            self.sourceItem = self.homedir + dir
        elif '/' in self.clipboard or '\\' in self.clipboard:
            self.sourceItem = self.homedir
        else:
            self.sourceItem = self.homedir + '/' + self.clipboard
            self.sourceItem = self.checkPath(self.sourceItem)
        
        self.selected = None
        self.rightPanel.setMessage('<' + self.clipboard + '>' + ' marked', 800) 

    def pasteFile(self):
        if not self.sourceItem:
            return
        
        if not self.selected:
            #self.destinationItem = self.checkPath(os.getcwd())
            self.rightPanel.setMessage('<No target selected>', 800)
            return
        
        if self.selected:
            try:
                for idx in self.selected:
                    text = self.tree.item(idx)['text']
        
            except Exception as e:
                #print('this')
                tk.messagebox.showerror('Error', str(e))
                return
        
            currentDirectory = self.checkPath(os.getcwd())
        
            if text.startswith('>'):
                dir = text.split()[1]
                self.destinationItem = currentDirectory + dir
        
            elif '/' in text or '\\' in text:
                self.destinationItem = currentDirectory

            else:
                self.destinationItem = currentDirectory + '/' + text
        
        #print('self.sourceItem:', self.sourceItem)
        #print('self.destinationItem:', self.destinationItem)
        
        if os.path.isfile(self.sourceItem):             # Source == file
            if os.path.isdir(self.destinationItem):     # Destination == directory
                destination = self.destinationItem      

                try:
                    shutil.copy2(self.sourceItem, destination)
                    self.refreshTree()

                except Exception as e:
                    tk.messagebox.showerror('Error', str(e))
                    return
            
            elif os.path.isfile(self.destinationItem):  # Destination == file
                destination = os.path.dirname(self.destinationItem)

                try:
                    shutil.copy2(self.sourceItem, destination)
                    self.refreshTree()

                except Exception as e:
                    tk.messagebox.showerror('Error', str(e))
                    return

        elif os.path.isdir(self.sourceItem):            # Source == directory
            if os.path.isdir(self.destinationItem):     # Destination == directory
                destination = self.destinationItem + '/'
                basename = self.sourceItem.split('/')[-1]
                destination = destination + basename
                destination = self.checkPath(destination)
                #print('destination:', destination)

                try:
                    shutil.copytree(self.sourceItem, destination)
                    self.refreshTree()
                
                except Exception as e:
                    tk.messagebox.showerror('Error', str(e))
                    return
            
            elif os.path.isfile(self.destinationItem):   # Destination == file
                destination = os.path.dirname(self.destinationItem) + '/'
                destination = self.checkPath(destination)
                basename = self.sourceItem.split('/')[-1]
                destination = destination + basename
                #print('destination:', destination)
                
                try:
                    shutil.copytree(self.sourceItem, destination)
                    self.refreshTree()
                    
                except Exception as e:
                    tk.messagebox.showerror('Error', str(e))
                    return
        
        self.selected = None
        self.sourceItem = None
            
        
    def deleteFile(self):
        rootDir = self.checkPath(os.getcwd())
        directory = None
        file = None
        size = None
        
        if self.selected:
            for idx in self.selected:
                try:
                    text = self.tree.item(idx)['text']
                except:
                    self.selected = []
                    return
            
            if '/' in text or '\\' in text:
                directory = True
            else:
                file = True
            
            if file == True:
                filename = rootDir + '/' + text
            else: # directory
                if text.startswith('>'):
                    dir = text.split()[-1]
                    filename = rootDir + dir
                elif '/' in text or '\\' in text:
                    filename = text
                
        else:
            return
        
        filename = self.checkPath(filename)
        
        result = tk.messagebox.askquestion('Delete', 'Delete\n\n' + filename + '  ?')
        
        if result == 'yes':
            if directory:
                try:
                    shutil.rmtree(filename)
                    self.refreshTree()
                    
                except Exception as e:
                    tk.messagebox.showerror('Error', str(e))
                    
            elif file:
                try:
                    os.remove(filename)
                    self.refreshTree()
                
                except Exception as e:
                    tk.messagebox('Error', str(e))

    
    def treePopUp(self, event):
        item = self.tree.identify('item',event.x,event.y)
        self.tree.selection_set(item)
            
        menu = tk.Menu(self, tearoff=False)
        menu.add_command(label='Info', compound=tk.LEFT, command=self.treeGenerateInfo)
        menu.add_separator()
        menu.add_command(label="Create New Folder", compound=tk.LEFT, command=self.treeGenerateFolder)
        menu.add_command(label="Copy Item", compound=tk.LEFT, command=self.treeGenerateCopy)
        menu.add_command(label="Paste Item", compound=tk.LEFT, command=self.treeGeneratePaste)
        menu.add_command(label="Delete Item", compound=tk.LEFT, command=self.treeGenerateDelete)
        menu.add_separator()
        menu.add_command(label="Select Directory", compound=tk.LEFT, command=self.treeGenerateSelectDir)
        menu.add_command(label="Zip Folder", compound=tk.LEFT, command=self.treeZipFolder)
        menu.add_separator()
        menu.add_command(label="Refresh Tree", compound=tk.LEFT, command = self.treeGenerateRefresh)
        menu.tk_popup(event.x_root, event.y_root, 0)

    def treeGenerateInfo(self):
        if not self.selected:
            self.rightPanel.setMessage('<No Selection>', 800)
            return
        
        self.infoFile()
    
    def treeGenerateFolder(self):
        self.newFolder()
    
    def treeGenerateCopy(self):
        if not self.selected:
            self.rightPanel.setMessage('<No Selection>', 800)

        self.copyFile()

    def treeGeneratePaste(self):
        if not self.selected:
            self.rightPanel.setMessage('<No Selection>', 800)

        self.pasteFile()
    
    def treeGenerateDelete(self):
        if not self.selected:
            self.rightPanel.setMessage('<No Selection>', 800)

        self.deleteFile()

    def treeGenerateSelectDir(self):
        d = os.getcwd()
        d = self.checkPath(d)
        directory = filedialog.askdirectory(initialdir=d)
        if not directory:
            return
        try:
            os.chdir(directory)
            for i in self.tree.get_children():
                self.tree.delete(i)
            path = '.'
            abspath = os.path.abspath(path)
            root_node = self.tree.insert('', 'end', text=abspath, open=True)
            self.process_directory(root_node, abspath)
                
        except Exception as e:
            return
            #print(str(e))

    
    def treeGenerateRefresh(self):
        self.refreshTree()
    
    def zipfolder(self, foldername, target_dir):            
        zipobj = zipfile.ZipFile(foldername + '.zip', 'w', zipfile.ZIP_DEFLATED)
        rootlen = len(target_dir) + 1
        for base, dirs, files in os.walk(target_dir):
            for file in files:
                fn = os.path.join(base, file)
                zipobj.write(fn, fn[rootlen:])
    
    def treeZipFolder(self):
        dialog = simpledialog.askstring('Make Zip-File from current directory', 'current directory\n' + os.getcwd() + 
                                        '\n\nEnter filename: ')
        if not dialog:
            return
            
        filename = dialog
        
        dir = os.getcwd()
        self.zipfolder(filename, dir)
        self.refreshTree()
        
        
######################################################################


######################################################################
class RightPanel(tk.Frame):
    '''
        RightPanel .... containing textPad + rightButtonFrame + Buttons
    '''
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.initUI()
    
    def initUI(self):
        pathList = __file__.replace('\\', '/')
        pathList = __file__.split('/')[:-1]
        c = Configuration()
        self.password = c.getPassword()
        
        self.dir = ''
        for item in pathList:
            self.dir += item + '/'
        #print(self.dir)
        
        rightButtonFrame = tk.Frame(self, height=25, bg='gray')
        rightButtonFrame.pack(side=tk.TOP, fill=tk.X)
        
        self.rightBottomFrame = tk.Frame(self, height=25)
        self.rightBottomFrame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # notebook
        self.notebook = ttk.Notebook(self)
        self.frame1 = ttk.Frame(self.notebook)
        self.notebook.add(self.frame1, text='noname')
        
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.bind("<ButtonRelease-1>", self.tabChanged)
        self.notebook.bind("<ButtonRelease-3>", self.closeContext)
        
        # clipboard

        # textPad
        self.textPad = TextPad(self.frame1, undo=True, maxundo=-1, autoseparators=True)
        self.textPad.filename = None
        self.textPad.bind("<FocusIn>", self.onTextPadFocus)
        self.textPad.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        textScrollY = ttk.Scrollbar(self.textPad)
        textScrollY.config(cursor="double_arrow")
        self.textPad.configure(yscrollcommand=textScrollY.set)
        textScrollY.config(command=self.textPad.yview)
        textScrollY.pack(side=tk.RIGHT, fill=tk.Y)
        
        # PopUp TextPad
        self.textPad.bind("<ButtonRelease-3>", self.textPadPopUp)
        
        # other binding for the textPad
        self.textPad.bind("<<Change>>", self.on_change)
        self.textPad.bind("<Configure>", self.on_change)
        
        self.linenumber = TextLineNumbers(self.frame1, width=35)
        self.linenumber.attach(self.textPad)
        self.linenumber.pack(side="left", fill="y")
        
        self.linenumber.bind('<ButtonRelease-1>', self.linenumberSelect)
        self.linenumber.bind('<ButtonRelease-3>', self.linenumberPopUp)
        
        # hold textPad and linenumber-widget
        self.TEXTPADS = {}
        self.LINENUMBERS = {}
        
        self.TEXTPADS[0] = self.textPad
        self.LINENUMBERS[0] = self.linenumber
        
        # Buttons
        newIcon = tk.PhotoImage(file=self.dir + 'images/new.png')
        newButton = ttk.Button(rightButtonFrame, image=newIcon, command=self.new)
        newButton.image = newIcon
        newButton.pack(side=tk.LEFT)
        self.createToolTip(newButton, 'Create New File')

        openIcon = tk.PhotoImage(file=self.dir + 'images/open.png')
        openButton = ttk.Button(rightButtonFrame, image=openIcon, command=self.open)
        openButton.image = openIcon
        openButton.pack(side=tk.LEFT)
        self.createToolTip(openButton, 'Open File')

        
        saveIcon = tk.PhotoImage(file=self.dir + 'images/save.png')
        saveButton = ttk.Button(rightButtonFrame, image=saveIcon, command=self.save)
        saveButton.image = saveIcon
        saveButton.pack(side=tk.LEFT)
        self.createToolTip(saveButton, 'Save File')

        printIcon = tk.PhotoImage(file=self.dir + 'images/print.png')
        printButton = ttk.Button(rightButtonFrame, image=printIcon, command=self.print)
        printButton.image = printIcon
        printButton.pack(side=tk.LEFT)
        self.createToolTip(printButton, 'Print File')

        
        undoIcon = tk.PhotoImage(file=self.dir + 'images/undo.png')
        self.undoButton = ttk.Button(rightButtonFrame, image=undoIcon, command=self.undo)
        self.undoButton.image = undoIcon
        self.undoButton.pack(side=tk.LEFT)
        self.createToolTip(self.undoButton, 'Undo')

        redoIcon = tk.PhotoImage(file=self.dir + 'images/redo.png')
        self.redoButton = ttk.Button(rightButtonFrame, image=redoIcon, command=self.redo)
        self.redoButton.image = redoIcon
        self.redoButton.pack(side=tk.LEFT)
        self.createToolTip(self.redoButton, 'Redo')

        zoomInIcon = tk.PhotoImage(file=self.dir + 'images/zoomIn.png')
        zoomInButton = ttk.Button(rightButtonFrame, image=zoomInIcon, command=self.zoomIn)
        zoomInButton.image = zoomInIcon
        zoomInButton.pack(side=tk.LEFT)
        self.createToolTip(zoomInButton, 'Zoom In')

        zoomOutIcon = tk.PhotoImage(file=self.dir + 'images/zoomOut.png')
        zoomOutButton = ttk.Button(rightButtonFrame, image=zoomOutIcon, command=self.zoomOut)
        zoomOutButton.image = zoomOutIcon
        zoomOutButton.pack(side=tk.LEFT)
        self.createToolTip(zoomOutButton, 'Zoom Out')


        settingsIcon = tk.PhotoImage(file=self.dir + 'images/settings.png')
        settingsButton = ttk.Button(rightButtonFrame, image=settingsIcon, command=self.settings)
        settingsButton.image = settingsIcon
        settingsButton.pack(side=tk.LEFT)
        self.createToolTip(settingsButton, 'Show Settings')

        #searcher = tk.Entry(rightButtonFrame)
        #searcher.pack(side=tk.LEFT)

        runIcon = tk.PhotoImage(file=self.dir + 'images/run.png')
        runButton = ttk.Button(rightButtonFrame, image=runIcon, command=self.run)
        runButton.image = runIcon
        runButton.pack(side=tk.RIGHT)
        self.createToolTip(runButton, 'Run File')
        
        self.runMenu = tk.Menu(self, tearoff=0)
        self.runMenu.add_command(label="Run", command=self.run)
        self.runMenu.add_command(label="Run with sudo", command=self.runSudo)
        runButton.bind('<Button-3>', self.popupRun)
                
        
        terminalIcon = tk.PhotoImage(file=self.dir + 'images/terminal.png')
        terminalButton = ttk.Button(rightButtonFrame, image=terminalIcon, command=self.terminal)
        terminalButton.image = terminalIcon
        terminalButton.pack(side=tk.RIGHT)
        self.createToolTip(terminalButton, 'Open Terminal')

        interpreterIcon = tk.PhotoImage(file=self.dir + 'images/interpreter.png')
        interpreterButton = ttk.Button(rightButtonFrame, image=interpreterIcon, command=self.interpreter)
        interpreterButton.image = interpreterIcon
        interpreterButton.pack(side=tk.RIGHT)
        self.createToolTip(interpreterButton, 'Open Python Interpreter')

        viewIcon = tk.PhotoImage(file=self.dir + 'images/view.png')
        viewButton = ttk.Button(self.rightBottomFrame, image=viewIcon, command=self.overview)
        viewButton.image = viewIcon
        viewButton.pack(side=tk.RIGHT)
        self.createToolTip(viewButton, 'Class Overview')

        searchIcon = tk.PhotoImage(file=self.dir + 'images/search.png')
        searchButton = ttk.Button(self.rightBottomFrame, image=searchIcon, command=self.search)
        searchButton.image = searchIcon
        searchButton.pack(side=tk.RIGHT)
        self.createToolTip(searchButton, 'Search')

        self.searchBox = tk.Entry(self.rightBottomFrame)
        self.searchBox.bind('<Key>', self.OnSearchBoxChange)
        self.searchBox.bind('<Return>', self.search)
        self.searchBox.pack(side=tk.RIGHT, padx=5)
        # self.searching = False

        # autocompleteEntry
        self.autocompleteEntry = tk.Label(self.rightBottomFrame, fg='green', text='---', font=('Mono', 13))
        self.autocompleteEntry.pack(side='left', fill='y', padx=5)
        self.textPad.entry = self.autocompleteEntry


        # Shortcuts
        self.textPad = self.shortcutBinding(self.textPad)

    def popupRun(self, event):
        self.runMenu.post(event.x_root, event.y_root)


    def onTextPadModified(self, event=None):
        flag = self.textPad.edit_modified()
        if flag:
            x = self.notebook.index(self.notebook.select())
            filename = self.textPad.filename
            if filename == None:
                self.textPad.edit_modified(False)
                return
            else:
                if filename.endswith('*'):
                    self.textPad.edit_modified(False)
                    return
                else:
                    filename += '*'
                    file = filename.split('/')[-1]
                    self.notebook.tab(x, text=file)
                    self.textPad.filename = filename
                    self.update()
                    self.textPad.edit_modified(False)
            
            # self.textPad.filename now with '*' ... change that on save !!
            # to do !! ....
            
    def shortcutBinding(self, textPad):
        textPad.bind('<F1>', self.help)
        textPad.bind('<Control-Key-n>', self.new)
        textPad.bind('<Control-Key-o>', self.open)
        textPad.bind('<Control-Key-s>', self.save)
        textPad.bind("<Control-Shift_L><S>", self.saveAs)
        textPad.bind("<Control-Shift_R><S>", self.saveAs)
        textPad.bind('<Control-Key-p>', self.print)
        textPad.bind('<Control-Key-z>', self.undo)
        textPad.bind('<Control-Shift_L><Z>', self.redo)
        #textPad.bind('<Alt><+>', self.nextTab)
        textPad.bind('<Control-Key-f>', self.showSearch)
        textPad.bind('<Control-Key-g>', self.overview)
        textPad.bind('<F12>', self.settings)
        textPad.bind('<Alt-Up>', self.zoomIn)
        textPad.bind('<Alt-Down>', self.zoomOut)
        textPad.bind('<Alt-F4>', self.quit)
        textPad.bind('<<Modified>>', self.onTextPadModified)


        return textPad
    
    def showSearch(self, event=None):
        self.searchBox.focus_set()
    
    def quit(self, event):
        self.master.master.destroy()
    
    def nextTab(self, event=None):
        tabs = self.notebook.tabs()
        if not tabs:
            return
        
        id = self.notebook.index(self.notebook.select())
        
        if id < len(tabs) - 1:
            id += 1
            self.notebook.select(id)
            self.tabChanged()
            self.textPad.focus_set()

        elif id == len(tabs) -1:
            id = 0
            self.notebook.select(id)
            self.tabChanged()
            self.textPad.focus_set()
        
        else:
            return
    
    def help(self, event=None):
        help = HelpDialog(self, "Help", self.textPad)
        self.textPad.focus_set()


    def createToolTip(self, widget, text):
        toolTip = ToolTip(widget)
        def enter(event):
            toolTip.showtip(text)
        def leave(event):
            toolTip.hidetip()
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def OnSearchBoxChange(self, event=None):
        # self.searching = False
        self.start = 1.0
        if self.textPad:
            self.textPad.tag_remove('sel', "1.0", tk.END)

    def onTextPadFocus(self, event):
        filename = self.textPad.filename

        if not filename:
            return
        
        self.tabChanged()
    
    def linenumberPopUp(self, event):
        menu = tk.Menu(self.notebook, tearoff=False)
        menu.add_command(label='Goto', compound=tk.LEFT, command=self.textPadGenerateGoto)
        menu.tk_popup(event.x_root, event.y_root, 0)

    
    def textPadPopUp(self, event):
        menu = tk.Menu(self.notebook, tearoff=False)
        menu.add_command(label='Cut', compound=tk.LEFT, command=self.textPadGenerateCut)
        menu.add_command(label="Copy", compound=tk.LEFT, command=self.textPadGenerateCopy)
        menu.add_command(label="Paste", compound=tk.LEFT, command=self.textPadGeneratePaste)
        menu.add_separator()
        menu.add_command(label="Select All", compound=tk.LEFT, command=self.textPadSelectAll)
        menu.add_command(label="Highlight All", compound=tk.LEFT, command=self.textPadHighlightAll)
        menu.add_separator()
        menu.add_command(label='Goto', compound=tk.LEFT, command=self.textPadGenerateGoto)
        menu.add_separator()
        menu.add_command(label="Open Terminal", compound=tk.LEFT, command = self.terminal)
        menu.tk_popup(event.x_root, event.y_root, 0)

    def textPadGenerateCut(self, event=None):
        #self.textPad.event_generate('<<Cut>>')
        self.textPad.cut()
        return 'break'
    
    def textPadGenerateCopy(self, event=None):
        #self.textPad.event_generate('<<Copy>>')
        self.textPad.copy()
        return 'break'

        
    def textPadGeneratePaste(self, event=None):
        #self.textPad.event_generate('<<Paste>>')
        self.textPad.paste()
        return 'break'

    
    def textPadHighlightAll(self):
        text = self.textPad.get("1.0", "end")
        self.textPad.delete('1.0', tk.END)
        self.textPad.insert("1.0", text)
        self.master.master.master.title('Loading ...')
        self.textPad.config(cursor="X_cursor")
        self.textPad.highlightAll()
        self.textPad.config(cursor='xterm')
        self.textPad.update()
    
    def textPadSelectAll(self):
        self.textPad.tag_add('sel', '1.0', 'end')
        self.textPad.focus_force()
    
    def textPadGenerateGoto(self, event=None):
        GotoDialog(self.textPad)
    
    def linenumberSelect(self, event):
        obj = event.widget.find_overlapping(event.x, event.y, event.x, event.y)
        line = self.linenumber.itemcget(obj, "text")
        if line:
            self.textPad.tag_add('sel', '%d.0' % int(line), '%d.end' % int(line))
            self.textPad.focus_force()
        else:
            return
            
    def on_change(self, event):
        self.linenumber.redraw()

    def tabChanged(self, event=None):
        tabs = self.notebook.tabs()
        if not tabs:
            return
        
    
        id = self.notebook.index(self.notebook.select())
        #print(id)
        textPad = self.TEXTPADS[id]
        self.textPad = textPad
        self.textPad.bind("<ButtonRelease-3>", self.textPadPopUp)
        self.textPad.bind("<<Change>>", self.on_change)
        self.textPad.bind("<Configure>", self.on_change)

        
        self.linenumber = self.LINENUMBERS[id]
        self.textPad.entry = self.autocompleteEntry
 
        self.linenumber.bind('<ButtonRelease-1>', self.linenumberSelect)

        #print(self.textPad.filename)
        filename = self.textPad.filename
        
        if filename:
            self.master.master.master.title(self.textPad.filename)
            
            # change directory
            dirlist = filename.split('/')[:-1]
            directory = ''
            for item in dirlist:
                directory += item + '/'
                os.chdir(directory)
                for i in self.master.master.leftPanel.tree.get_children():
                    self.master.master.leftPanel.tree.delete(i)
                path = '.'
                abspath = os.path.abspath(path)
                root_node = self.master.master.leftPanel.tree.insert('', 'end', text=abspath, open=True)
                self.master.master.leftPanel.process_directory(root_node, abspath)
                


        else:
            self.master.master.master.title("Cross-Viper 0.1")
        
        
    
    def closeContext(self, event):
        tabs = self.notebook.tabs()
        if not tabs:
            return

        x = len(self.TEXTPADS) - 1
        self.notebook.select(x)
        self.tabChanged()
        self.master.master.master.title(self.textPad.filename)
        
        menu = tk.Menu(self.notebook, tearoff=False)
        menu.add_command(label='Close', compound=tk.LEFT, command=self.closeTab)
        menu.tk_popup(event.x_root, event.y_root, 0)
        
    def closeTab(self, event=None):
        filename = self.textPad.filename
        if filename:
            if filename.endswith('*'):
                result = tk.messagebox.askquestion('File not saved', 'Save now ?', icon='warning')
                if result == 'yes':
                    self.save()
                    
                else:
                    i = len(self.TEXTPADS)
                    x = len(self.TEXTPADS) - 1

                    self.notebook.forget(x)
                    self.TEXTPADS.pop(x, None)
        
                    self.tabChanged()
                    self.linenumber.redraw()
                    return
                    
                    
        i = len(self.TEXTPADS)
        x = len(self.TEXTPADS) - 1

        self.notebook.forget(x)
        self.TEXTPADS.pop(x, None)
        
        self.tabChanged()
        self.linenumber.redraw()
        
    def new(self, event=None):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='noname')

        textPad = TextPad(frame, undo=True, maxundo=-1, autoseparators=True)
        textPad.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        textScrollY = ttk.Scrollbar(textPad)
        textScrollY.config(cursor="double_arrow")
        textPad.configure(yscrollcommand=textScrollY.set)
        textScrollY.config(command=textPad.yview)
        textScrollY.pack(side=tk.RIGHT, fill=tk.Y)
        
        linenumber = TextLineNumbers(frame, width=35)
        linenumber.attach(textPad)
        linenumber.pack(side="left", fill="y")
        
        textPad.bind("<<Change>>", self.on_change)
        textPad.bind("<Configure>", self.on_change)
        
        # Shortcuts
        textPad = self.shortcutBinding(textPad)

        l = len(self.notebook.tabs())
        l = l - 1

        self.TEXTPADS[l] = textPad
        self.LINENUMBERS[l] = linenumber
        x = len(self.TEXTPADS) - 1
        self.notebook.select(x)

        self.tabChanged()
        linenumber.redraw()
        
    def open(self, event=None, file=None):
        if len(self.TEXTPADS) -1 == -1:
            self.new()
            
        if not file:
            dir = os.getcwd()
            dir = self.checkPath(dir)
            filename = filedialog.askopenfilename(initialdir=dir)
        else:
            filename = file
        
        print(file)
        makeNew = True
        
        if filename:
            if self.textPad.filename == None:
                makeNew = False
            try:
                with open(filename, 'r') as f:
                    #code = f.read().splitlines()
                    #print(code)
                    text = f.read()
                    if makeNew:
                        self.new()
                    l = len(self.TEXTPADS) - 1
                    #print('l', l)
                    self.notebook.select(l)
                    self.update()
                    self.tabChanged()
                    self.textPad.delete('1.0', tk.END)
                    
                    self.textPad.insert("1.0", text)
                    
                    self.master.master.master.title('Loading ...')
                    self.textPad.config(cursor="X_cursor")
                    self.textPad.update()
                    #t1 = threading.Thread(target=self.textPad.highlightAll)
                    #t1.start()
                    #t1.join()
                    self.textPad.highlightAll()
                    
                    self.textPad.config(cursor='xterm')
                    self.textPad.update()
                    self.textPad.filename = filename
                    file = filename.split('/')[-1]
                    self.notebook.tab(l, text=file)
                    self.master.master.master.title(self.textPad.filename)
                    self.textPad.updateAutoCompleteList()
                    self.tabChanged()
                    self.textPad.mark_set("insert", "1.0")

                    
            except Exception as e:
                #print(str(e))
                tk.messagebox.showinfo("Error", str(e))
        #    return
    
    
    def save(self, event=None):
        if len(self.TEXTPADS) -1 == -1:
            return
            
        if self.textPad.filename == None:
            d = os.getcwd()
            d = self.checkPath(d)
            filename = filedialog.asksaveasfilename(initialdir=d)
        
            if filename:
                try:
                    with open(filename, 'w') as f:
                        text = self.textPad.get("1.0",'end-1c')
                        f.write(text)
                        #l = len(self.TEXTPADS) - 1  # nicht richtig
                        id = self.notebook.index(self.notebook.select())
                        
                        self.textPad.filename = filename
                        file = filename.split('/')[-1]
                        self.notebook.tab(id, text=file)
                        self.master.master.master.title(self.textPad.filename)
                        self.tabChanged()
                        
                except Exception as e:
                    tk.messagebox.showinfo("Error", str(e))
                    return
        else:
            filename = self.textPad.filename
            if filename.endswith('*'):
                filename = filename.replace('*', '')
            
            '''
            filename += '*'
            file = filename.split('/')[-1]
            self.notebook.tab(x, text=file)
            self.textPad.filename = filename
            print(self.textPad.filename)
            self.update()
            self.textPad.edit_modified(False)
            '''
            try:
                with open(filename, 'w') as f:
                    text = self.textPad.get("1.0",'end-1c')
                    f.write(text)
                    #l = len(self.TEXTPADS) - 1
                    id = self.notebook.index(self.notebook.select())
                    self.textPad.filename = filename
                    file = filename.split('/')[-1]
                    self.notebook.tab(id, text=file)
                    self.master.master.master.title(self.textPad.filename)
                    self.tabChanged()
                    file = filename.split('/')[-1]
                    x = self.notebook.index(self.notebook.select())
                    self.notebook.tab(x, text=file)
            
            except Exception as e:
                    tk.messagebox.showinfo("Error", str(e))
                    return
    
    def saveAs(self, event=None):
        d = os.getcwd()
        d = self.checkPath(d)
        filename = filedialog.asksaveasfilename(initialdir=d)
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    text = self.textPad.get("1.0",'end-1c')
                    f.write(text)
                    #l = len(self.TEXTPADS) - 1  # nicht richtig
                    id = self.notebook.index(self.notebook.select())
                        
                    self.textPad.filename = filename
                    file = filename.split('/')[-1]
                    self.notebook.tab(id, text=file)
                    self.master.master.master.title(self.textPad.filename)
                    self.tabChanged()
                    
            except Exception as e:
                tk.messagebox.showinfo("Error", str(e))
                return



    def checkPath(self, dir):
        if '\\' in dir:
            path = dir.replace('\\', '/')
        else:
            path = dir
        return path

    
    def print(self, event=None):
        if platform.system().lower() == 'windows':
            if self.textPad:
                if self.textPad.filename is not None:
                    subprocess.call(['notepad.exe', '/p', self.textPad.filename])
        else:
            if self.textPad:
                if self.textPad.filename is not None:
                    subprocess.call(['lpr', self.textPad.filename])
        
        
    def undo(self, event=None):
        index = self.textPad.index("insert linestart")
        line = index.split('.')[0]
      
        line = int(line)
        
        try:
            self.textPad.edit_undo()
            self.textPad.focus_set()
            self.textPad.highlight(lineNumber=line)
            self.textPad.highlightThisLine()
        
        except Exception as e:
            tk.messagebox.showinfo('Error', str(e))
        
        
    
    def redo(self, event=None):
        #x = self.textPad.edit_modified()
        index = self.textPad.index('insert linestart')
        line = index.split('.')[0]
        
        line = int(line)
        
        try:
            self.textPad.edit_redo()
            self.textPad.focus_set()
            self.textPad.highlight(lineNumber=line)
            self.textPad.highlightThisLine()
        
        except Exception as e:
            tk.messagebox.showinfo('Error', str(e))
        
        
    def zoomIn(self, event=None):
        if self.textPad.fontSize < 30:
            self.textPad.fontSize += 1
            self.textPad.configFont()
            
            self.linenumber.fontSize +=1
            self.linenumber.configFont()
            self.linenumber.redraw()
            
            
    def zoomOut(self, event=None):
        if self.textPad.fontSize > 5:
            self.textPad.fontSize -= 1
            self.textPad.configFont()
            
            self.linenumber.fontSize -=1
            self.linenumber.configFont()
            self.linenumber.redraw()

    
    def settings(self, event=None):
        dialog = SettingsDialog(self.textPad)
        
    
    def search(self, start=None):
        self.textPad.tag_remove('sel', "1.0", tk.END)
        
        toFind = self.searchBox.get()
        pos = self.textPad.index(tk.INSERT)
        result = self.textPad.search(toFind, str(pos), stopindex=tk.END)
        
        if result:
            length = len(toFind)
            row, col = result.split('.')
            end = int(col) + length
            end = row + '.' + str(end)
            self.textPad.tag_add('sel', result, end)
            self.textPad.mark_set('insert', end)
            self.textPad.see(tk.INSERT)
            self.textPad.focus_force()
            self.searchBox.focus()
        else:
            self.textPad.mark_set('insert', '1.0')
            self.textPad.see(tk.INSERT)
            self.textPad.focus()
            self.setEndMessage(400)
            self.searchBox.focus()
            return

    
    def setMessage(self, text, seconds):
            self.textPad.entry.config(text=text)
            self.textPad.update()
            self.after(seconds, self.textPad.entry.config(text='---'))
            self.textPad.update()
        
    def setEndMessage(self, seconds):
            pathList = __file__.replace('\\', '/')
            pathList = __file__.split('/')[:-1]
        
            self.dir = ''
            for item in pathList:
                self.dir += item + '/'
            print(self.dir)
            #self.textPad.entry.config(text=text)
            #self.textPad.update()
            canvas = tk.Canvas(self.textPad, width=64, height=64)
            x = self.textPad.winfo_width() / 2
            y = self.textPad.winfo_height() / 2
            print('x', x)
            print('y', y)
            canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            #canvas.create_line(0, 50, 200, 50, fill="#476042")
            image = tk.PhotoImage(file = self.dir + 'images/last.png')
            canvas.create_image(0, 0,  anchor=tk.NW, image=image)
            self.textPad.update()
            self.after(seconds, self.textPad.entry.config(text='---'))
            canvas.destroy()
            self.textPad.update()

    

                
    def overview(self, event=None):
        ViewDialog(self.textPad, "Class - Overview", self.textPad)
        
    
    def interpreter(self):
        c = Configuration()     # -> in configuration.py
        system = c.getSystem()
        interpreterCommand = c.getInterpreter(system).format(self.textPad.filename)

        thread = RunThread(interpreterCommand)
        thread.start()

    
    def terminal(self):
        c = Configuration()     # -> in configuration.py
        system = c.getSystem()
        terminalCommand = c.getTerminal(system).format(self.textPad.filename)

        thread = RunThread(terminalCommand)
        thread.start()

    
    def run(self):
        if not self.textPad:
            return
        
        filepath = self.textPad.filename
        
        if not filepath:
            return
        
        self.save()

        file = filepath.split('/')[-1]
    
        c = Configuration()     # -> in configuration.py
        system = c.getSystem()
        runCommand = c.getRun(system).format(file)
                
        thread = RunThread(runCommand)
        thread.start()

    def runSudo(self):
        c = Configuration()
        self.password = c.getPassword()
        
        if not self.textPad:
            return
        
        filepath = self.textPad.filename
        
        if not filepath:
            return
        
        if not self.password:
            self.password = dialog = simpledialog.askstring('Enter Root Password', 'Password: ')
            saveThis = messagebox.askyesno('Sudo password', 'Save to configuration.ini ?')
            if saveThis == True:
                c = Configuration()
                c.setPassword(self.password)
            else:
                self.passwordTmp = None
        
            
        self.save()

        file = filepath.split('/')[-1]

        c = Configuration()
        system = c.getSystem()
        runCommand = c.getRun(system).format(file)
        
        os.popen("sudo -S %s"%(runCommand), 'w').write(self.password + '\n')
        
        self.password = self.passwordTmp

class CrossViper(tk.Frame):

    def __init__(self, master):
        super().__init__(master, width=1000, height=800)
        self.pack(expand=True, fill=tk.BOTH)
        self.initUI()
        self.style = ttk.Style()
        self.style.theme_use('clam')
        #self.style.configure("Treeview", background="black", 
        #        fieldbackground="black", foreground="white")
        
    def initUI(self):
        self.panedWindow = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.panedWindow.pack(fill=tk.BOTH, expand=1)
        self.rightPanel = RightPanel(self.panedWindow)
        #self.rightPanel.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        
        self.leftPanel = LeftPanel(self.panedWindow, self.rightPanel)
        self.leftPanel.rightPanel = self.rightPanel
        #self.leftPanel.pack(side=tk.LEFT, fill=tk.Y)
        
        self.panedWindow.add(self.leftPanel)
        self.panedWindow.add(self.rightPanel)
        
        self.rightPanel.textPad.focus_set()

def center(win):
    # Center the root screen
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

if __name__ == '__main__':
    root = tk.Tk()

    app = CrossViper(master=None)
    app.master.title('Cross-Viper 0.1')
    app.master.minsize(width=1000, height=800)
    pathList = __file__.replace('\\', '/')
    pathList = __file__.split('/')[:-1]
    dir = ''
    for item in pathList:
        dir += item + '/'
    dir = str(os.path.dirname(os.path.abspath(__file__))) + '/'
    dir += 'images/crossviper.ico'
    img = tk.PhotoImage(dir)
    root.tk.call('wm', 'iconphoto', root._w, img)
    center(root)
    app.mainloop()
