import tkinter as tk
from tkinter import ttk
import tkinter.scrolledtext as tkst
from configuration import Configuration
import configparser
import os
import sys 


class Dialog(tk.Toplevel):

    def __init__(self, parent, title=None):

        super().__init__(parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent

        self.result = None

        body = tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    #
    # construction hooks

    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden

        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = tk.Frame(self)

        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        #self.bind("<Return>", self.ok)
        #self.bind("<Escape>", self.cancel)

        box.pack()

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    def validate(self):

        return 1 # override

    def apply(self):

        pass # override


######################################################################

class SettingsDialog(Dialog):

    def body(self, master):
        # get configuration 
        self.master = master
        self.c = Configuration()        # in configuration.py
        self.system = self.c.getSystem()
        self.runCommand = self.c.getRun(self.system)
        self.terminalCommand = self.c.getTerminal(self.system)
        self.interpreterCommand = self.c.getInterpreter(self.system)
        self.master.grid_columnconfigure(1, weight=1)

        # make body
        tk.Label(master, text="Run:").grid(row=0)
        tk.Label(master, text="Terminal:").grid(row=1)
        tk.Label(master, text="Interpreter:").grid(row=2)
        
        self.v = tk.IntVar()
        if self.c.getSystem() == 'mate':
            self.v.set(1)
        elif self.c.getSystem() == 'gnome':
            self.v.set(2)
        elif self.c.getSystem() == 'kde':
            self.v.set(3)
        elif self.c.getSystem() == 'xterm':
            self.v.set(4)
        elif self.c.getSystem() == 'windows':
            self.v.set(5)
        elif self.c.getSystem() == 'mac':
            self.v.set(6)

        
        self.e1 = tk.Entry(master)
        self.e2 = tk.Entry(master)
        self.e3 = tk.Entry(master)
        self.mate_radio = tk.Radiobutton(master, text='Mate', variable=self.v,
                                        command=self.setMate, value=1)
        self.gnome_radio = tk.Radiobutton(master, text='Gnome', variable=self.v,
                                        command=self.setGnome, value=2)
        self.kde_radio = tk.Radiobutton(master, text='KDE', variable=self.v,
                                        command=self.setKDE, value=3)
        self.xterm_radio = tk.Radiobutton(master, text='xterm', variable=self.v,
                                        command=self.setXterm, value=4)
        self.win_radio = tk.Radiobutton(master, text='Windows', variable=self.v,
                                        command=self.setWindows, value=5)
        self.mac_radio = tk.Radiobutton(master, text='MacOS', variable=self.v,
                                        command=self.setMac, value=6)




        self.e1.grid(row=0, column=1, sticky='ew')
        self.e1.insert(0, self.runCommand)
        self.e2.grid(row=1, column=1, sticky='ew')
        self.e2.insert(0, self.terminalCommand)
        self.e3.grid(row=2, column=1, sticky='ew')
        self.e3.insert(0, self.interpreterCommand)
        self.mate_radio.grid(row=3, column=0)
        self.gnome_radio.grid(row=3, column=1)
        self.kde_radio.grid(row=3, column=2)
        self.xterm_radio.grid(row=4, column=0)
        self.win_radio.grid(row=4, column=1)
        self.mac_radio.grid(row=4, column=2)
        
        return self.e1 # initial focus
    
    def setStandard(self):
        config = configparser.ConfigParser()
        
        config['Run'] = {}
        config['Run']['mate'] = 'mate-terminal -x sh -c "python3 {}; exec bash"'
        config['Run']['gnome'] = 'gnome-terminal -x sh -c "python3 {}; exec bash"'
        config['Run']['kde'] = 'konsole --hold -e "python3 {}"'
        config['Run']['xterm'] = 'xterm -hold -e "python3 {}"'
        config['Run']['windows'] = 'start cmd /K python {}'
        config['Run']['mac'] = 'open -a Terminal ./python3 {}'
        
        config['Terminal'] = {}
        config['Terminal']['mate'] = 'mate-terminal'
        config['Terminal']['gnome'] = 'gnome-terminal'
        config['Terminal']['kde'] = 'konsole'
        config['Terminal']['xterm'] = 'xterm'
        config['Terminal']['windows'] = 'start cmd'
        config['Terminal']['mac'] = 'open -a Terminal ./' 
        
        config['Interpreter'] = {}
        config['Interpreter']['mate'] = 'mate-terminal -x "python3"'
        config['Interpreter']['gnome'] = 'gnome-terminal -x "python3"'
        config['Interpreter']['kde'] = 'konsole -e python3'
        config['Interpreter']['xterm'] = 'xterm python3'
        config['Interpreter']['windows'] = 'start cmd /K python'
        config['Interpreter']['mac'] = 'open -a Terminal ./python3'
        
        config['System'] = {}
        config['System']['system'] = 'None'
        
        return config

    def setSystem(self, system):
        system = system
        self.runCommand = self.c.getRun(system)
        self.e1.delete(0, tk.END)
        self.e1.insert(0, self.runCommand)

        self.terminalCommand = self.c.getTerminal(system)
        self.e2.delete(0, tk.END)
        self.e2.insert(0, self.terminalCommand)

        self.interpreterCommand = self.c.getInterpreter(system)
        self.e3.delete(0, tk.END)
        self.e3.insert(0, self.interpreterCommand)


    def setMate(self, event=None):
        self.setSystem('mate')
        
    def setGnome(self, event=None):
        self.setSystem('gnome')

    def setKDE(self, event=None):
        self.setSystem('kde')

    def setXterm(self, event=None):
        self.setSystem('xterm')

    def setWindows(self, event=None):
        self.setSystem('windows')

    def setMac(self, event=None):
        self.setSystem('mac')

    def apply(self):
        value = self.v.get()
        config = self.setStandard()
        
        if value == 1:
            config['System']['system'] = 'mate'
            config['Run']['mate'] = self.e1.get()
            config['Terminal']['mate'] = self.e2.get()
            config['Interpreter']['mate'] = self.e3.get()
        elif value == 2:
            config['System']['system'] = 'gnome'
            config['Run']['gnome'] = self.e1.get()
            config['Terminal']['gnome'] = self.e2.get()
            config['Interpreter']['gnome'] =self.e3.get()

        elif value == 3:
            config['System']['system'] = 'kde'
            config['Run']['kde'] = self.e1.get()
            config['Terminal']['kde'] = self.e2.get()
            config['Interpreter']['kde'] = self.e3.get()
        elif value == 4:
            config['System']['system'] = 'xterm'
            config['Run']['xterm'] = self.e1.get()
            config['Terminal']['xterm'] = self.e2.get()
            config['Interpreter']['xterm'] = self.e3.get()
        elif value == 5:
            config['System']['system'] = 'windows'
            config['Run']['windows'] = self.e1.get()
            config['Terminal']['windows'] = self.e2.get()
            config['Interpreter']['windows'] = self.e3.get()
        elif value == 6:
            config['System']['system'] = 'mac'
            config['Run']['mac'] = self.e1.get()
            config['Terminal']['mac'] = self.e2.get()
            config['Interpreter']['mac'] = self.e3.get()
        else:
            return
        
        if getattr(sys, 'frozen', False):
            thisFile = os.path.realpath(sys._MEIPASS)
        else:
            thisFile = os.path.realpath(__file__)      # Pfad ermitteln

        base = os.path.dirname(thisFile)
        base = self.CheckPath(base)
        iniPath = base + "/crossviper.ini"
        with open(iniPath, 'w') as f:
            config.write(f)
        

    def CheckPath(self, path):
        if '\\' in path:
            path = path.replace('\\', '/')
        return path

#########################################################

class ViewDialog(tk.Toplevel):
    def __init__(self, parent, title=None, textPad=None):

        super().__init__(parent)
        self.transient(parent)
        self.textPad = textPad

        if title:
            self.title(title)

        self.parent = parent

        self.result = None

        body = tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        
        self.work()


        self.initial_focus.focus_set()
        self.wait_window(self)
        
        

    def body(self, master):
        self.treeview = ttk.Treeview(self)
        self.treeview.pack()
        self.treeview.bind('<Double-1>', self.OnActivated)

        
    def buttonbox(self):
        box = tk.Frame(self)
        
        w = tk.Button(box, text="OK", width=10, command=self.cancel, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        box.pack()


    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    def work(self):
        if not self.textPad:
            return
        if self.textPad.filename == None:
            return

        filename = ''
        if self.textPad.filename:
            filename = self.textPad.filename.split('/')[-1]
        
        
        self.treeview.heading('#0', text=filename)
        self.treeview.column('#0', stretch=tk.YES, minwidth=350, width=350)
        self.i = 0
        
        filename = self.textPad.filename
        if filename.endswith('*'):
            filename = filename.replace('*', '')
            
        with open(filename, 'r') as f:
            textLines = f.readlines()
        
        self.AddTreeNodes(textLines)
        
        #self.treeview.Bind(xxxxx)


    def AddTreeNodes(self, text):
        self.findLine = {}
        x = 0
        for line in text:
            x += 1
            y = 0
            whitespaces = len(line) - len(line.lstrip())
            if 'class' in line:
                l = line.lstrip()
                #print(l)
                if l.startswith('class'):
                    node = self.treeview.insert('', 'end', text=line)
                    key = '_class_' + line
                    self.findLine[key] = x
                
                    for secondLine in text[x:]:
                        whitespacesSecond = len(secondLine) - len(secondLine.lstrip())
                        y += 1
                        newClass = False
                        if newClass == False:
                            if 'class' in secondLine:
                                l = secondLine.lstrip()
                                if l.startswith('#'):
                                    continue
                                newClass = True
                                key = ''
                                break
                            elif 'def' in secondLine:
                                l = secondLine.lstrip()
                                if l.startswith('def'):
                                    if l.startswith('#'):
                                        continue
                                    else:
                                        if whitespaces < whitespacesSecond:
                                            self.treeview.insert(node, 'end', text=secondLine)
                                            key += secondLine
                                            self.findLine[key] = x+y
                                            key = '_class_' + line
                                        else:
                                            break
            if 'def' in line:
                whitespaces = len(line) - len(line.lstrip())
                if whitespaces == 0:
                    l = line.lstrip()
                    if l.startswith('def'):
                        if l.startswith('#'):
                            continue
                        else:
                            node = self.treeview.insert('', 'end', text=line)
                            key = '_root_' + line
                            self.findLine[key] = x

                    else:
                        continue
            
            if 'if __name__ ==' in line:
                l = line.lstrip()
                if l.startswith('if __name__'):
                    node = self.treeview.insert('', 'end', line)
                    key = '_root_' + line
                    self.findLine[key] = x
        
        #print(self.findLine)

    def OnActivated(self, event):
        item = self.treeview.identify('item', event.x, event.y)
        label =  self.treeview.item(item, "text")

        if label == '':
            self.textPad.mark_set('insert', '1.0')
            self.textPad.see(tk.INSERT)
            self.textPad.focus_force()
            return
        
        key = ''
        searchKey = ''
    
        if 'class' in label and 'def' not in label:
            key = '_class_' + label
            z = self.findLine[key]
            self.textPad.mark_set('insert', "%d.0" %(z))
            self.textPad.see(tk.INSERT)
            self.textPad.focus_force()

        elif 'def' in label:
            childLabel = label
            
            info = self.treeview.get_children()
            self.nodeList = []
            for i in info:
                #print(i)
                if i.startswith('I'):
                    self.nodeList.append(i)
            #print(':', self.nodeList)
            parentLabel = None
            for i in self.nodeList:
                if i < item:
                    parentLabel = self.treeview.item(i, 'text')
            
            if parentLabel == None:
                searchKey = '_root_' + childLabel
                #print('searchKey:' , searchKey)
                z = self.findLine[searchKey]
                self.textPad.mark_set('insert', "%d.0" %(z))
                self.textPad.see(tk.INSERT)
                self.textPad.focus_force()

            elif parentLabel:
                if 'class' in parentLabel:
                    try:
                        searchKey = '_class_' + parentLabel
                        searchKey += childLabel
                        z = self.findLine[searchKey]
                        self.textPad.mark_set('insert', "%d.0" %(z))
                        self.textPad.see(tk.INSERT)
                        self.textPad.focus_force()
                    except:
                        #exception class ends -> change to def in _root_ 
                        searchKey = '_root_' + childLabel
                        z = self.findLine[searchKey]
                        self.textPad.mark_set('insert', "%d.0" %(z))
                        self.textPad.see(tk.INSERT)
                        self.textPad.focus_force()
  

                else:
                    searchKey = '_root_' + childLabel
                    z = self.findLine[searchKey]
                    self.textPad.mark_set('insert', "%d.0" %(z))
                    self.textPad.see(tk.INSERT)
                    self.textPad.focus_force()
                    
        
        elif 'if __name__' in label:
            key = '_root_' + label
            z = self.findLine[key]
            self.textPad.mark_set('insert', "%d.0" %(z))
            self.textPad.see(tk.INSERT)
            self.textPad.focus_force()

#########################################################

class InfoDialog(tk.Toplevel):
    def __init__(self, parent, title=None, text=None, directory=None, file=None, size=None):

        super().__init__(parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent
        self.text = text
        self.directory = directory
        self.file = file
        self.size = size
        
        self.result = None

        body = tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))


        self.initial_focus.focus_set()
        self.wait_window(self)
        
        

    def body(self, master):
        self.master = master
        label1 = tk.Label(self, text=self.text)
        label1.pack()
    
        if self.directory:
            label2 = tk.Label(master, text='type: directory')
            label2.pack()
        else:
            label2 = tk.Label(master, text='type: file')
            label2.pack()
        if self.file:
            label3 = tk.Label(master, text='size: ' + str(self.size) + " bytes")
            label3.pack()
        
    def buttonbox(self):
        box = tk.Frame(self)
        
        w = tk.Button(box, text="OK", width=10, command=self.cancel, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        box.pack()


    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

#########################################################
class NewDirectoryDialog(Dialog):
    
    
    def body(self, master):
        # get configuration 
        self.master = master

        # make body
        tk.Label(master, text="Name of directory:").grid(row=0)
        
        self.e1 = tk.Entry(master)
        self.e1.grid(row=0, column=1, sticky='nsew')
        
        return self.e1 # initial focus

    def apply(self):
        name = self.e1.get()
        dir = self.CheckPath(os.getcwd())
        dir += '/' + name
        os.mkdir(dir)

    def CheckPath(self, path):
        if '\\' in path:
            path = path.replace('\\', '/')
        return path


##########################################################
class HelpDialog(tk.Toplevel):
    def __init__(self, parent, title="Help", textPad=None):
        super().__init__(parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent

        body = tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))


        self.initial_focus.focus_set()
        self.wait_window(self)
        
        

    def body(self, master):
        self.master = master
        readonlyHelp = tkst.ScrolledText(self)
        readonlyHelp.pack()

        
        text = '''
        CrossViper - The Cross-Platform Python IDE
        
        
        Shortcuts:
        
        
        New File        -       Ctrl + N
        Open File       -       Ctrl + O
        Save File       -       Ctrl + S
        SaveAs          -       Ctrl + Shift + S
        Print           -       Ctrl + P
        Quit CrossViper -       Alt + F4
        Undo            -       Ctrl + Z
        Redo            -       Ctrl + Shift + Z
        Copy            -       Ctrl + C
        Cut             -       Ctrl + X
        Paste           -       Ctrl + V
        Select All      -       Ctrl + A
        Change Tab      -       Alt + +
        Search          -       Ctrl + F
        Class Overview  -       Ctrl + G
        Show Settings   -       F12
        Zoom In         -       Alt + Up
        Zoom Out        -       Alt + Down
        Set Cursor      -       Ctrl + Left / Ctrl + Right
        Show Help       -       F1
        

        programmed 2017 by morbidMo

        '''
        
        readonlyHelp.insert(1.0, text)
        readonlyHelp.configure(state='disabled')

    def buttonbox(self):
        box = tk.Frame(self)
        
        w = tk.Button(box, text="OK", width=10, command=self.cancel, default=tk.ACTIVE)
        w.pack(side=tk.BOTTOM, padx=5, pady=5)
        box.pack()
        buttonbox = tk.Frame(self)

    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()
