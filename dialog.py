import tkinter as tk
from tkinter import ttk
import tkinter.scrolledtext as tkst
from configuration import Configuration
import configparser
import os
import sys 
import zipfile


class Dialog(tk.Toplevel):

    def __init__(self, parent, title=None):

        super().__init__(parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent

        self.result = None

        body = ttk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()


        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()
        
        # make background black 
        self.configure(bg='black')
        
        # no borders ?
        #self.overrideredirect(1)
        
        self.wait_window(self)


    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden

        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = ttk.Frame(self)
        #box.configure(bg='black')
        
        w = ttk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
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

    def CheckPath(self, path):
        if '\\' in path:
            path = path.replace('\\', '/')
        return path

#########################################################
class NewDirectoryDialog(Dialog):
    
    def body(self, master):
        # get configuration 
        
        # make body
        ttk.Label(master, text="Name of directory:").grid(row=0)
        
        self.e1 = tk.Entry(master)
        self.e1 = tk.Entry(master, bg='black', fg='white')
        self.e1.configure(cursor="xterm green")
        self.e1.configure(insertbackground = "red")
        self.e1.configure(highlightcolor='#448dc4')
        self.e1.grid(row=0, column=1, sticky='nsew')
        
        return self.e1 # initial focus

    def apply(self):
        name = self.e1.get()
        dir = self.CheckPath(os.getcwd())
        dir += '/' + name
        os.mkdir(dir)




############################################################

class RenameDialog(Dialog):
    
    def __init__(self, parent, title=None, item=None):
        self.item = item
        super().__init__(parent, title)
    
    def body(self, master):

        # make body
        ttk.Label(master, text='Current name: ').grid(row=1, column=0)
        ttk.Label(master, text=self.item).grid(row=1, column=1)
        ttk.Label(master, text="New name: ").grid(row=2)
        
        self.e1 = tk.Entry(master)
        self.e1 = tk.Entry(master, bg='black', fg='white')
        self.e1.configure(cursor="xterm green")
        self.e1.configure(insertbackground = "red")
        self.e1.configure(highlightcolor='#448dc4')
        self.e1.grid(row=2, column=1, sticky='nsew')
        
        return self.e1 # initial focus

    def apply(self):
        lastName = self.getLastName(self.item)
        cwd = self.CheckPath(os.getcwd()) + '/'
        
        oldFullPath = cwd + lastName 
        
        new = self.e1.get()
        
        newFullPath = cwd + new
        
        try:
            os.rename(oldFullPath, newFullPath)
        except Exception as e:
            print(str(e))
        
    def getLastName(self, item):
        # get LastName
        if item.startswith('>'):
            item = item.replace('> ', '')
            if ('/') in item:
                item = item.split('/')[-1]
            return item
        elif item.startswith('/'):
            item = item.split('/')[-1]
            return item
        else:
            return item


#############################################################

class ZipFolderDialog(Dialog):
    
    def body(self, master):

        # make body
        ttk.Label(master, text='Current Folder: ').grid(row=1, column=0)
        ttk.Label(master, text=os.getcwd()).grid(row=1, column=1)
        ttk.Label(master, text="Zip Filename: ").grid(row=2, column=0)
        ttk.Label(master, text='.zip').grid(row=2, column=2)
        
        self.e1 = tk.Entry(master)
        self.e1 = tk.Entry(master, bg='black', fg='white')
        self.e1.configure(cursor="xterm green")
        self.e1.configure(insertbackground = "red")
        self.e1.configure(highlightcolor='#448dc4')
        self.e1.grid(row=2, column=1, sticky='nsew')
        
        return self.e1 # initial focus

    def apply(self):
        dir = self.CheckPath(os.getcwd()) 
        filename = self.e1.get() + '.zip'
        
        self.zipfolder(filename, dir)

    def zipfolder(self, filename, target_dir):            
        zipobj = zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED)
        rootlen = len(target_dir) + 1
        for base, dirs, files in os.walk(target_dir):
            for file in files:
                fn = os.path.join(base, file)
                zipobj.write(fn, fn[rootlen:])



#############################################################

class MessageDialog(Dialog):
    def __init__(self, parent, title, text=None):
        self.text = text
        super().__init__(parent, title)
    
    def body(self, master):
        label1 = ttk.Label(master, text=self.text)
        label1.configure(style="White.TLabel")
        label1.pack()
        
        return label1
    
        
    def buttonbox(self):
        box = ttk.Frame(self)
        
        b1 = ttk.Button(box, text="Ok", width=10, command=self.cancel, default=tk.ACTIVE)
        b1.pack(side=tk.LEFT, padx=5, pady=5)

        box.pack()
        

    def cancel(self, event=None):
        # put focus back to the parent window
        self.result = 0
        self.parent.focus_set()
        self.destroy()


#############################################################


class MessageYesNoDialog(Dialog):
    def __init__(self, parent, title, text=None):
        self.text = text
        super().__init__(parent, title)
    
    def body(self, master):
        label1 = ttk.Label(master, text=self.text)
        label1.configure(style="White.TLabel")
        label1.pack()
        
        return label1
    
        
    def buttonbox(self):
        box = ttk.Frame(self)
        
        b1 = ttk.Button(box, text="Yes", width=10, command=self.apply, default=tk.ACTIVE)
        b1.pack(side=tk.LEFT, padx=5, pady=5)
        b2 = ttk.Button(box, text="No", width=10, command=self.cancel, default=tk.ACTIVE)
        b2.pack(side=tk.LEFT, padx=5, pady=5)

        box.pack()

    def apply(self, event=None):
        self.result = 1
        self.parent.focus_set()
        self.destroy()
        

    def cancel(self, event=None):
        # put focus back to the parent window
        self.result = 0
        self.parent.focus_set()
        self.destroy()


#############################################################
class MessageSudoYesNoDialog(Dialog):

    def __init__(self, parent, title, text):
        self.text = text
        super().__init__(parent, title)
        
    def body(self, master):
        label1 = ttk.Label(master, text=self.text)
        label1.configure(style="White.TLabel")
        label1.pack()
        self.pw = tk.Entry(master, bg='black', fg='white')
        self.pw.configure(cursor="xterm green")
        self.pw.configure(insertbackground = "red")
        self.pw.configure(highlightcolor='#448dc4')
        self.pw.config(show="*")
        self.pw.pack()
    
        
    def buttonbox(self):
        box = ttk.Frame(self)
        
        b1 = ttk.Button(box, text="Ok", width=10, command=self.apply, default=tk.ACTIVE)
        b1.pack(side=tk.LEFT, padx=5, pady=5)
        b2 = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        b2.pack(side=tk.LEFT, padx=5, pady=5)

        box.pack()

    def apply(self, event=None):
        self.result = 1
        self.password = self.pw.get()
        self.parent.focus_set()
        self.destroy()
        

    def cancel(self, event=None):
        # put focus back to the parent window
        self.result = 0
        self.parent.focus_set()
        self.destroy()

#############################################################

class InfoDialog(Dialog):

    def __init__(self, parent, title, text, directory, file, size):
        self.text = text
        self.directory = directory
        self.file = file
        self.size = size
        super().__init__(parent, title)

    def body(self, master):
        label1 = ttk.Label(master, text=' ' + self.text + ' ')
        label1.configure(style="Red.TLabel")
        label1.pack()
        label1b = ttk.Label(master, text=' ')
        label1b.configure(style="White.TLabel")
        label1b.pack()
        

    
        if self.directory:
            label2a = ttk.Label(master, text='Type: directory\n', anchor=tk.W)
            label2a.configure(style="White.TLabel")
            label2a.pack()
        else:
            label2a = ttk.Label(master, text='Type: file\n', anchor=tk.W)
            label2a.configure(style="White.TLabel")
            label2a.pack()
        if self.file:
            label3a = ttk.Label(master, text='Size: ' + str(self.size) + ' bytes\n', anchor=tk.W)
            label3a.configure(style="White.TLabel")
            label3a.pack()
            
        return label1
    
        
    def buttonbox(self):
        box = ttk.Frame(self)
        
        w = ttk.Button(box, text="OK", width=10, command=self.cancel, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        box.pack()


    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

#############################################################
class HelpDialog(Dialog):
    def __init__(self, parent, title):
        super().__init__(parent, title)
    
    def body(self, master):
        tabControl = ttk.Notebook(master)
        
        ##
        # Tab What is
        ##
        tab1 = ttk.Frame(tabControl)
        tabControl.add(tab1, text='What is CrossViper ?')
        tabControl.pack(expand=1, fill='both')
        
        readonlyWhatIs = tkst.ScrolledText(tab1, bg='black', fg='white', wrap='none')
        readonlyWhatIs.pack()
        
        textWhatIs = '''
        CrossViper - The cross platform Python IDE
        
        CrossViper is an Editor and Integrated Development Environment (IDE)
        for the "Python Programming Language".
        
        It shows the "python source code" colored (syntax highlighting) and 
        helps you to code with its own auto-complete function.
        
        It can run the codefile (requirement is, that you have installed 
        Python on your OS)
        It can also run the "Python Interpreter" and a terminal window 
        (specific for your current OS) -> this can be modified in the 
        settings (-> which where saved in crossviper.ini => it's a text file)
        
        On the bottom-right, you find two buttons => one for searching the 
        current file and the other to analyse the code 
        (-> shows you the classes and functions)
        
        On the left side it has its own file-explorer to 
        copy, delete, rename ... files and folders. Use the pop-up menu
        (right mousebutton).
        '''
        
        readonlyWhatIs.insert(1.0, textWhatIs)
        readonlyWhatIs.configure(state='disabled')


        ##
        # Tab Shortcut
        ##
        
        tab2 = ttk.Frame(tabControl)
        tabControl.add(tab2, text='Shortcuts')
        tabControl.pack(expand=1, fill='both')
        
        readonlyShortcuts = tkst.ScrolledText(tab2, bg='black', fg='white', wrap='none')
        readonlyShortcuts.pack()

        
        textShortcut = '''
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
        Change Tab      -       Alt + Right
        Autocomplete    -       Tab
        Search          -       Ctrl + F
        Class Overview  -       Ctrl + G
        Show Settings   -       F12
        Zoom In         -       Alt + Up
        Zoom Out        -       Alt + Down
        Set Cursor      -       Ctrl + Left / Ctrl + Right
        Show Help       -       F1
        
        '''
        
        readonlyShortcuts.insert(1.0, textShortcut)
        readonlyShortcuts.configure(state='disabled')

        ##
        # Tab About
        ##
        tab3 = ttk.Frame(tabControl)
        tabControl.add(tab3, text='About')
        tabControl.pack(expand=1, fill='both')
        
        readonlyAbout = tkst.ScrolledText(tab3, bg='black', fg='white', wrap='none')
        readonlyAbout.pack()

        textAbout = '''
        CrossViper 1.0
        
        
        Programmed 2017 by morbidMo
        
        
        I's open source software. You can modify and use the sourcecode -
        make it better or fork it on github.com:
        
        
        https://github.com/morten1982/crossviper
        
        
        no guarantee of using it - it's your own risk :)
        
        
        CrossViper was completely coded in Python just using tkinter
        
        Requirements are : pygments (-> for syntax highlighting)
        To install pygments : pip3 install pygments
        
        '''
        readonlyAbout.insert(1.0, textAbout)
        readonlyAbout.configure(state='disabled')

        
        
    def buttonbox(self):
        box = ttk.Frame(self)
        
        w = ttk.Button(box, text="OK", width=10, command=self.cancel, default=tk.ACTIVE)
        w.pack(side=tk.BOTTOM, padx=5, pady=5)
        box.pack()
        buttonbox = tk.Frame(self)

    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

#############################################################
class GotoDialog(Dialog):
    def __init__(self, parent, title=None):
        self.Pad = parent
        super().__init__(parent, title)

    def body(self, master):
        # make body
        ttk.Label(master, text="Goto Linenumber:").grid(row=0)
        
        #self.e1 = tk.Entry(master)
        
        index = int(self.Pad.index("end-1c linestart").split('.')[0])
        
        var = tk.StringVar()
        var.set("1")
        self.spinbox = tk.Spinbox(master, from_= 1, to=index, textvariable=var, bg='black', fg='white', width=5)
        self.spinbox.grid(row=0, column=1, sticky='nsew')
        self.spinbox.configure(cursor="xterm green")
        self.spinbox.configure(insertbackground = "red")
        self.spinbox.configure(highlightcolor='#448dc4')
        self.spinbox.configure(buttonbackground='green')
        self.spinbox.selection('range', tk.INSERT, tk.END)
        
        return self.spinbox # initial focus

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = ttk.Frame(self)

        w = ttk.Button(box, text="OK", width=10, command=self.apply, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)


        box.pack()
        

    def apply(self, event=None):
        number = self.spinbox.get()
        if number.isnumeric():
            number = int(number)
        else:
            return
        
        #print('number', number)
        
        try:
            self.Pad.mark_set("insert", "%d.0" % (number))
        except Exception as e:
            print(str(e))
            
        self.Pad.see(tk.INSERT)
        self.Pad.focus_set()
        
        self.cancel()
        
    
    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()


#############################################################

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
            
        self.title('Settings')
        
        # make body
        ttk.Label(master, text="Run:").grid(row=0)
        ttk.Label(master, text="Terminal:").grid(row=1)
        ttk.Label(master, text="Interpreter:").grid(row=2)
        
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

        
        self.e1 = tk.Entry(master, bg='black', fg='white', width=40)
        self.e1.configure(cursor='left_ptr')
        self.e1.configure(insertbackground = "red")
        self.e1.configure(highlightcolor='#448dc4')
        self.e1Label = ttk.Label(master, text = '{} = Filename')
        #self.e1Label.configure(style='White.TLabel')

        self.e2 = tk.Entry(master, bg='black', fg='white', width=40)
        self.e2.configure(cursor='left_ptr')
        self.e2.configure(insertbackground = "red")
        self.e2.configure(highlightcolor='#448dc4')

        self.e3 = tk.Entry(master, bg='black', fg='white', width=40)
        self.e3.configure(cursor='left_ptr')
        self.e3.configure(insertbackground = "red")
        self.e3.configure(highlightcolor='#448dc4')

        
        

        self.mate_radio = ttk.Radiobutton(master, text='Mate', variable=self.v,
                                        command=self.setMate, value=1)
        self.gnome_radio = ttk.Radiobutton(master, text='Gnome', variable=self.v,
                                        command=self.setGnome, value=2)
        self.kde_radio = ttk.Radiobutton(master, text='KDE', variable=self.v,
                                        command=self.setKDE, value=3)
        self.xterm_radio = ttk.Radiobutton(master, text='xterm', variable=self.v,
                                        command=self.setXterm, value=4)
        self.win_radio = ttk.Radiobutton(master, text='Windows', variable=self.v,
                                        command=self.setWindows, value=5)
        self.mac_radio = ttk.Radiobutton(master, text='MacOS', variable=self.v,
                                        command=self.setMac, value=6)



        self.e1.grid(row=0, column=1, sticky='ew')
        self.e1.insert(0, self.runCommand)
        self.e1Label.grid(row=0, column=2, sticky='ew')
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
        config['System']['system'] = ''
        
        config['Password'] = {}
        config['Password']['password'] = ''
        
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
        print(base)
        iniPath = base + "/crossviper.ini"
        with open(iniPath, 'w') as f:
            config.write(f)
        


#########################################################

class ViewDialog(tk.Toplevel):
    def __init__(self, parent, title=None, textPad=None):

        super().__init__(parent)
        self.transient(parent)
        self.textPad = textPad
        self.configure(bg='black')

        if title:
            self.title(title)

        self.parent = parent

        self.result = None

        body = ttk.Frame(self)
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

        self.treeview.tag_configure('class', background='black', foreground='yellow')
        self.treeview.tag_configure('function', background='black', foreground='#448dc4')
        self.treeview.tag_configure('something', background='black', foreground='gray')

        
    def buttonbox(self):
        box = ttk.Frame(self)
        
        w = ttk.Button(box, text="OK", width=10, command=self.cancel, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        box.pack()


    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    def work(self):
        if not self.textPad:
            self.cancel()
        if self.textPad.filename == None or self.textPad.filename == 'noname':
            filename = 'noname'

        if self.textPad.filename:
            filename = self.textPad.filename.split('/')[-1]
        
        if not filename:
            self.cancel()
        
        self.treeview.heading('#0', text=filename)
        self.treeview.column('#0', stretch=tk.YES, minwidth=350, width=350)
        self.i = 0
        
        #filename = self.textPad.filename
        
        textLines = self.textPad.get('1.0', 'end-1c')
        lines = textLines.split('\n')
                    
        self.AddTreeNodes(lines)
        
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
                    node = self.treeview.insert('', 'end', text=line, tags='class')
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
                                            self.treeview.insert(node, 'end', text=secondLine, tags='function')
                                            key += secondLine
                                            self.findLine[key] = x+y
                                            key = '_class_' + line
                                        else:
                                            break
            elif 'def' in line:
                whitespaces = len(line) - len(line.lstrip())
                if whitespaces == 0:
                    l = line.lstrip()
                    if l.startswith('def'):
                        if l.startswith('#'):
                            continue
                        else:
                            node = self.treeview.insert('', 'end', text=line, tags='function')
                            key = '_root_' + line
                            self.findLine[key] = x

                    else:
                        continue
            
            elif 'if __name__ ==' in line:
                l = line.lstrip()
                if l.startswith('if __name__'):
                    node = self.treeview.insert('', 'end', line, tags='something')
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
class ChangeDirectoryDialog(tk.Toplevel):
    def __init__(self, parent, title=None, text=''):

        super().__init__(parent)
        self.transient(parent)
        
        self.text = text
        
        if title:
            self.title(title)
        else:
            title='Change Directory'

        self.parent = parent
        self.text = text
        
        # value for get : Yes or No
        self.result = None

        body = ttk.Frame(self)
        label1 = ttk.Label(body, text=self.text)
        label1.configure(style="White.TLabel")
        label1.pack()
        self.treeview = ttk.Treeview(body)
        self.treeview.tag_configure('row', background='black', foreground='white')
        self.treeview.tag_configure('folder', background='black', foreground='yellow')
        self.treeview.tag_configure('subfolder', background='black', foreground='#448dc4')
        self.treeview.tag_configure('hidden', background='black', foreground='gray')
        
        self.treeview['show'] = 'tree'
        self.treeview.bind("<Double-1>", self.OnDoubleClickTreeview)
        self.treeview.bind("<Button-1>", self.OnClickTreeview)
        #self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        
        path = self.checkPath(os.getcwd())
        abspath = os.path.abspath(path)
        
        root_node = self.treeview.insert('', 'end', text=abspath, open=True, tags='folder')
        self.process_directory(root_node, abspath)


        self.treeview.pack(expand=True)

        body.pack(padx=5, pady=5)


        self.buttonbox()

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.configure(bg='black')
        
        # variable fpr selected item
        self.selected = None
        
        self.wait_window(self)

    def refreshTree(self):
        for i in self.treeview.get_children():
            self.treeview.delete(i)
        path = '.'
        abspath = os.path.abspath(path)
        root_node = self.treeview.insert('', 'end', text=abspath, open=True, tags='folder')
        self.process_directory(root_node, abspath)

        
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
                    continue
                
                # list sort ...
            l.sort()
            #l.reverse()
            
            for items in l:
                if items.startswith('>'):
                    self.treeview.insert(parent, 'end', text=str(items), open=False, tags='subfolder')
                elif items.startswith('.'):
                    self.treeview.insert(parent, 'end', text=str(items), open=False, tags='hidden')                    
                else:
                    self.treeview.insert(parent, 'end', text=str(items), open=False, tags='row')
       
        except Exception as e:
            MessageDialog(self, 'Error', '\n' + str(e) + '\n')
            return
        
    def OnClickTreeview(self, event=None):
        item = self.treeview.identify('item',event.x,event.y)
        dir = self.treeview.item(item, 'text')
        self.checkPath(dir)
        
        if '>' in dir:
            dir = dir.replace('> ', '')
            
        self.selected = dir
        
        
    def OnDoubleClickTreeview(self, event):
        item = self.treeview.identify('item',event.x,event.y)

        
        if self.treeview.item(item, "text").startswith('>'):
            root = os.getcwd()

            sub = self.treeview.item(item, "text").split()[1]

            dir = root + sub
            dir = self.checkPath(dir)
            try:
                os.chdir(dir)
            except Exception as e:
                MessageDialog(self, 'Error', '\n' + str(e) + '\n')

            self.selected = None
            self.refreshTree()
    
        elif '/' in self.treeview.item(item, "text") or '\\' in self.treeview.item(item, "text"):
            os.chdir('..')
            dir = self.checkPath(os.getcwd())
            self.refreshTree()
            self.selected = None
            return 'break'

        else:
            item = self.treeview.identify('item',event.x,event.y)
            dir = self.treeview.item(item, 'text')
            self.checkPath(dir)
        
            if '>' in dir:
                dir = dir.replace('> ', '')
                os.chdir(dir)

            else:
                return
            

        self.refreshTree()

    def checkPath(self, path):
        if '\\' in path:
            path = path.replace('\\', '/')
        return path

    def on_select(self, event):
        self.selected = event.widget.selection()

        
    def buttonbox(self):
        box = ttk.Frame(self)
        
        b1 = ttk.Button(box, text="Ok", width=10, command=self.apply, default=tk.ACTIVE)
        b1.pack(side=tk.LEFT, padx=5, pady=5)
        b2 = ttk.Button(box, text="Cancel", width=10, command=self.cancel, default=tk.ACTIVE)
        b2.pack(side=tk.LEFT, padx=5, pady=5)

        box.pack()

    def apply(self, event=None):
        self.result = 1
        self.parent.focus_set()
        self.destroy()
        

    def cancel(self, event=None):
        # put focus back to the parent window
        self.result = 0
        self.parent.focus_set()
        self.destroy()
        
#########################################################

#########################################################
class OpenFileDialog(tk.Toplevel):
    def __init__(self, parent, title=None, text=''):

        super().__init__(parent)
        self.transient(parent)
        
        self.text = text
        
        if title:
            self.title(title)
        else:
            title='Open'

        self.parent = parent
        self.text = text
        
        # value for get : Yes or No
        self.result = None

        body = ttk.Frame(self)
        label1 = ttk.Label(body, text=self.text)
        label1.configure(style="White.TLabel")
        label1.pack()
        self.treeview = ttk.Treeview(body)
        self.treeview.tag_configure('row', background='black', foreground='white')
        self.treeview.tag_configure('folder', background='black', foreground='yellow')
        self.treeview.tag_configure('subfolder', background='black', foreground='#448dc4')
        self.treeview.tag_configure('hidden', background='black', foreground='gray')
        
        self.treeview['show'] = 'tree'
        self.treeview.bind("<Double-1>", self.OnDoubleClickTreeview)
        self.treeview.bind("<Button-1>", self.OnClickTreeview)
        #self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        
        path = self.checkPath(os.getcwd())
        abspath = os.path.abspath(path)
        
        root_node = self.treeview.insert('', 'end', text=abspath, open=True, tags='folder')
        self.process_directory(root_node, abspath)


        self.treeview.pack(expand=True)

        body.pack(padx=5, pady=5)


        self.buttonbox()

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.configure(bg='black')
        
        # variable fpr selected item
        self.selected = None
        
        self.wait_window(self)

    def refreshTree(self):
        for i in self.treeview.get_children():
            self.treeview.delete(i)
        path = '.'
        abspath = os.path.abspath(path)
        root_node = self.treeview.insert('', 'end', text=abspath, open=True, tags='folder')
        self.process_directory(root_node, abspath)

        
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
                if items.startswith('>'):
                    self.treeview.insert(parent, 'end', text=str(items), open=False, tags='subfolder')
                elif items.startswith('.'):
                    self.treeview.insert(parent, 'end', text=str(items), open=False, tags='hidden')                    
                else:
                    self.treeview.insert(parent, 'end', text=str(items), open=False, tags='row')
       
        except Exception as e:
            MessageDialog(self, 'Error', '\n' + str(e) + '\n')
            return
        
    def OnClickTreeview(self, event=None):
        item = self.treeview.identify('item',event.x,event.y)
        dir = self.treeview.item(item, 'text')
        self.checkPath(dir)
        
        if '>' in dir:
            dir = dir.replace('> ', '')
            
        self.selected = dir
        
        
    def OnDoubleClickTreeview(self, event):
        item = self.treeview.identify('item',event.x,event.y)
        root = os.getcwd()

        
        if self.treeview.item(item, "text").startswith('>'):
            sub = self.treeview.item(item, "text").split()[1]

            dir = root + sub
            dir = self.checkPath(dir)
            try:
                os.chdir(dir)
            except Exception as e:
                MessageDialog(self, 'Error', '\n' + str(e) + '\n')

            self.selected = None
            self.refreshTree()
    
        elif '/' in self.treeview.item(item, "text") or '\\' in self.treeview.item(item, "text"):
            os.chdir('..')
            dir = self.checkPath(os.getcwd())
            self.refreshTree()
            return 'break'

        else:
            item = self.treeview.identify('item',event.x,event.y)
            obj = self.treeview.item(item, 'text')
            self.checkPath(obj)
            
            self.selected = obj
            
            if '>' in obj:
                obj = obj.replace('> ', '')
                os.chdir(obj)

            elif obj == root:
                return
            


        self.refreshTree()

    def checkPath(self, path):
        if '\\' in path:
            path = path.replace('\\', '/')
        return path

    def on_select(self, event):
        self.selected = event.widget.selection()


        
    def buttonbox(self):
        box = ttk.Frame(self)
        
        b1 = ttk.Button(box, text="Ok", width=10, command=self.apply, default=tk.ACTIVE)
        b1.pack(side=tk.LEFT, padx=5, pady=5)
        b2 = ttk.Button(box, text="Cancel", width=10, command=self.cancel, default=tk.ACTIVE)
        b2.pack(side=tk.LEFT, padx=5, pady=5)

        box.pack()

    def apply(self, event=None):
        self.result = 1
        absdir = os.getcwd()
        if not absdir == self.selected:

            if self.selected == None:
                self.parent.focus_set()
                self.destroy()
            
            try:
                os.chdir(absdir + self.selected)
            except Exception as e:
                self.parent.focus_set()
                self.destroy()
                
        self.parent.focus_set()
        self.destroy()
        

    def cancel(self, event=None):
        # put focus back to the parent window
        self.result = 0
        self.parent.focus_set()
        self.destroy()


#########################################################
class SaveFileDialog(tk.Toplevel):
    def __init__(self, parent, title=None, text=''):

        super().__init__(parent)
        self.transient(parent)
        
        self.text = text
        
        if title:
            self.title(title)
        else:
            title='Save'

        self.parent = parent
        self.text = text
        
        # value for get : Yes or No
        self.result = None

        body = ttk.Frame(self)
        label1 = ttk.Label(body, text=self.text)
        label1.configure(style="White.TLabel")

        self.treeview = ttk.Treeview(body)
        self.treeview.tag_configure('row', background='black', foreground='white')
        self.treeview.tag_configure('folder', background='black', foreground='yellow')
        self.treeview.tag_configure('subfolder', background='black', foreground='#448dc4')
        self.treeview.tag_configure('hidden', background='black', foreground='gray')
        
        self.treeview['show'] = 'tree'
        self.treeview.bind("<Double-1>", self.OnDoubleClickTreeview)
        self.treeview.bind("<Button-1>", self.OnClickTreeview)
        self.treeview.bind('<<TreeviewSelect>>', self.on_select)

        
        self.filenameBox = tk.Entry(self, bg='black', fg='white')
        self.filenameBox.configure(cursor="xterm green")
        self.filenameBox.configure(insertbackground = "red")
        self.filenameBox.configure(highlightcolor='#448dc4')

        
        
        path = self.checkPath(os.getcwd())
        abspath = os.path.abspath(path)
        
        root_node = self.treeview.insert('', 'end', text=abspath, open=True, tags='folder')
        self.process_directory(root_node, abspath)


        body.pack(padx=5, pady=5)
        label1.pack()
        self.treeview.pack(expand=True)
        self.filenameBox.pack()




        self.buttonbox()

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.configure(bg='black')
        
        # variable fpr selected item
        self.selected = None
        
        self.wait_window(self)

    def refreshTree(self):
        for i in self.treeview.get_children():
            self.treeview.delete(i)
        path = '.'
        abspath = os.path.abspath(path)
        root_node = self.treeview.insert('', 'end', text=abspath, open=True, tags='folder')
        self.process_directory(root_node, abspath)

        
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
                if items.startswith('>'):
                    self.treeview.insert(parent, 'end', text=str(items), open=False, tags='subfolder')
                elif items.startswith('.'):
                    self.treeview.insert(parent, 'end', text=str(items), open=False, tags='hidden')                    
                else:
                    self.treeview.insert(parent, 'end', text=str(items), open=False, tags='row')
       
        except Exception as e:
            MessageDialog(self, 'Error', '\n' + str(e) + '\n')
            return
        
    def OnClickTreeview(self, event=None):
        item = self.treeview.identify('item',event.x,event.y)
        dir = self.treeview.item(item, 'text')
        self.checkPath(dir)
        
        if dir:
            if '>' in dir:
                dir = dir.replace('> ', '')
            
        self.selected = dir
        
        
    def OnDoubleClickTreeview(self, event):
        item = self.treeview.identify('item',event.x,event.y)
        root = os.getcwd()

        
        if self.treeview.item(item, "text").startswith('>'):
            sub = self.treeview.item(item, "text").split()[1]

            dir = root + sub
            dir = self.checkPath(dir)
            try:
                os.chdir(dir)
            except Exception as e:
                MessageDialog(self, 'Error', '\n' + str(e) + '\n')

            self.selected = None
            self.refreshTree()
    
        elif '/' in self.treeview.item(item, "text") or '\\' in self.treeview.item(item, "text"):
            os.chdir('..')
            dir = self.checkPath(os.getcwd())
            self.refreshTree()
            return 'break'

        else:
            item = self.treeview.identify('item',event.x,event.y)
            obj = self.treeview.item(item, 'text')
            self.checkPath(obj)
            
            self.selected = obj
            
            if '>' in obj:
                obj = obj.replace('> ', '')
                os.chdir(obj)

            elif obj == root:
                return
            


        self.refreshTree()

    def checkPath(self, path):
        if path:
            if '\\' in path:
                path = path.replace('\\', '/')
        return path

    def on_select(self, event):
        item = self.treeview.focus()
        
        text = self.treeview.item(item, 'text')


        if text.startswith('>'):
            text = ''
        elif ('/') in text:
            text = ''
        else:
            text = self.treeview.item(item, 'text')
        
        self.filenameBox.delete(0, 'end')
        self.filenameBox.insert(0, text)

        
    def buttonbox(self):
        box = ttk.Frame(self)
        
        b1 = ttk.Button(box, text="Ok", width=10, command=self.apply, default=tk.ACTIVE)
        b1.pack(side=tk.LEFT, padx=5, pady=5)
        b2 = ttk.Button(box, text="Cancel", width=10, command=self.cancel, default=tk.ACTIVE)
        b2.pack(side=tk.LEFT, padx=5, pady=5)

        box.pack()

    def apply(self, event=None):
        self.result = 1
        filename = self.filenameBox.get()
        
        if filename == None or '/' in filename:
            self.result = 0

        dir = os.getcwd()
        self.filename = dir + '/' + filename
        
        self.parent.focus_set()
        self.destroy()
            
        
    def cancel(self, event=None):
        # put focus back to the parent window
        self.result = 0
        self.filename = None
        self.parent.focus_set()
        self.destroy()
        
#########################################################