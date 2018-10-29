import tkinter as tk
from tkinter import ttk
from tkinter import font
import keyword
import platform
from pygments import lex
from pygments.lexers import PythonLexer
import re
 
class TextLineNumbers(tk.Canvas):
    '''
        Canvas for Linenumbers
    '''
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None
        self.fontSize = 12
        self.configFont()


    def configFont(self):
        system = platform.system().lower()
        if system == "windows":
            self.font = font.Font(family='monospace', size=self.fontSize)
        elif system == "linux":
            self.font = font.Font(family='monospace', size=self.fontSize)


    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(1,y,anchor="nw", font=self.font, text=linenum, fill='white')
            i = self.textwidget.index("%s+1line" % i)
        
        

class TextPad(tk.Text):
    '''
        modified text Widget ... thanks to stackoverflow.com :)
    '''
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)
        
        self.tk.eval('''
            proc widget_proxy {widget widget_command args} {

                # call the real tk widget command with the real args
                set result [uplevel [linsert $args 0 $widget_command]]

                # generate the event for certain types of commands
                if {([lindex $args 0] in {insert replace delete}) ||
                    ([lrange $args 0 2] == {mark set insert}) || 
                    ([lrange $args 0 1] == {xview moveto}) ||
                    ([lrange $args 0 1] == {xview scroll}) ||
                    ([lrange $args 0 1] == {yview moveto}) ||
                    ([lrange $args 0 1] == {yview scroll})} {

                    event generate  $widget <<Change>> -when tail
                }

                # return the result from the real widget command
                return $result
            }
            ''')
        self.tk.eval('''
            rename {widget} _{widget}
            interp alias {{}} ::{widget} {{}} widget_proxy {widget} _{widget}
        '''.format(widget=str(self)))
        
        self.filename = None
        self.tabWidth = 4
        self.clipboard = None
        self.entry = None
        
        self.fontSize = 13
        self.configFont()

        self.config(insertbackground='#00FF00')
        self.config(background='#000000')
        self.config(foreground='#FFFFFF')
        
        self.bind('<Return>', self.indent, add='+')
        self.bind('<Tab>', self.tab)
        self.bind('<BackSpace>', self.backtab)
        self.bind('<KeyRelease>', self.highlight, add='+')
        self.bind('<KeyRelease>', self.correctThisLine, add='+')
        #self.bind('<KeyPress-Return>', self.getDoublePoint)
        self.bind('<KeyRelease-Down>', self.correctLine)
        self.bind('<KeyRelease-Up>', self.correctLineUp)
        self.bind('<Key>', self.updateAutocompleteEntry, add='+')
        self.bind('<Control-x>', self.cut)
        self.bind('<Control-c>', self.copy)
        self.bind('<Control-v>', self.paste)
        #self.bind('<space>', self.highlight)
        
        self.autocompleteList = []
        self.SetAutoCompleteList()
        #print(self.autocompleteList)
        self.charstring = ''
        self.list = []
        
        # change selection color
        self.tag_config("sel", background="#47494c", foreground="white")
        

    
    def updateAutoCompleteList(self, event=None):
        '''
            a simple algorithm for parsing the given text and filter important words
        '''
        self.SetAutoCompleteList()
            
        autocompleteList = []
        liste = []
        text = self.get(1.0, tk.END)
        text = text.replace('"', " ").replace("'", " ").replace("(", " ").replace\
                        (")", " ").replace("[", " ").replace("]", " ").replace\
                        (':', " ").replace(',', " ").replace("<", " ").replace\
                        (">", " ").replace("/", " ").replace("=", " ").replace\
                        (";", " ").replace("self.", "").replace('.', ' ')
        
        liste = text.split('\n')
        
        for zeile in liste:
            if zeile.strip().startswith('#'):
                continue
            else:
                wortListe = zeile.split()
                for wort in wortListe:
                    if re.match("(^[0-9])", wort):
                        continue
                    elif '#' in wort or '//' in wort:
                        continue
                    elif wort in self.kwList:
                        continue
                    elif wort in self.autocompleteList:
                        continue
                    elif not len(wort) < 3:
                        w = re.sub("{}<>;,:]", '', wort)
                        #print(w)
                        autocompleteList.append(w)
        
        x = set(autocompleteList)
        autocompleteList = list(x)
        #print(autocompleteList)
        #self.autocompleteList = autocompleteList
        for word in autocompleteList:
            if len(word) > 30:
                continue
            self.autocompleteList.append(word)
        #print(self.autocompleteList)
        return
    
    
    def updateAutocompleteEntry(self, event=None):
        '''
            make new list for the input from the user
        '''
        char = event.char
        key = event.keycode
        sym = event.keysym
        
        # debugging ... :)
        #print(char)
        #print(key)
        
        self.list = []
        if (sym=='Space') or (sym=='Up') or (sym=='Down') or (sym=='Left') or (sym=='Right') \
            or (sym=='Shift_L') or (sym=='Shift_R') or (sym=='Control_R') or (sym=='Control_R') \
            or (sym=='Alt_L'):
                # set label and variables to none
                self.entry.config(text='---')
                self.list = []
                self.charstring = ''
        
        elif(char == '.') or (char == '(') or (char == ')') or (char=='"') or (char=="'") or \
            (char==',') or (char=='='):
                self.entry.config(text='---')
                self.list = []
                self.charstring = ''
        
        else:
            self.charstring += char
            
            for item in self.autocompleteList:
                if item.startswith(self.charstring):
                    self.list.append(item)
            
            if self.list:
                self.entry.config(text=self.list[0])                            
            else:
                self.entry.config(text='---')

            if len(self.list) == 3:
                self.entry.config(text=self.list[0])
                            
        
    def paste(self, event=None):
        '''
            paste method
        '''
        if self.clipboard == None:
            root = tk.Tk()                          # make tk instance
            root.withdraw()                         # don't display
            self.clipboard = root.clipboard_get()   # get clipboard
            root.clipboard_clear()                  # clear clipboard
            
        index = str(self.index(tk.INSERT))
        code = self.clipboard
        print(code)
        try:
            codelines = code.splitlines()
            for item in codelines:
                self.insert(tk.INSERT, item)
                self.insert(tk.INSERT, '\n')
                index = self.index('insert linestart')
                line = index.split('.')[0]
                line = int(line) - 1
                self.highlight(lineNumber=line)
                self.see(tk.INSERT)
        except:
            self.clipboard = None
            
        self.clipboard = None
        
        return 'break'
            
    
    def copy(self, event=None):
        '''
            copy method
        '''
        if self.tag_ranges("sel"):
            self.clipboard = self.get(tk.SEL_FIRST, tk.SEL_LAST)
            return 'break'

    
    def cut(self, event=None):
        '''
            cut method
        '''
        if self.tag_ranges("sel"):
            self.clipboard = self.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.delete(tk.SEL_FIRST, tk.SEL_LAST)
            return 'break'


    def selectAll(self, event=None):
        self.tag_add('sel', '1.0', 'end')
    
    def indent(self, event=None):
        '''
            make indent
        '''
        self.entry.config(text='---')
        self.list = []
        self.charstring = ''

        self.highlight()
        index = self.index(tk.INSERT).split(".")
        line_no = int(index[0])
        pos = int(index[1])
        self.updateAutoCompleteList()
        if pos == 0:
            return
        line_text = self.get("%d.%d" % (line_no, 0),  "%d.end" % (line_no))
        text_only = line_text.lstrip(" ")
        no_of_spaces = len(line_text) - len(text_only)
        spaces = '\n' + " " * no_of_spaces
        if(no_of_spaces % 2 == 0):
            self.insert(tk.INSERT, spaces)

        else:
            while(no_of_spaces % 2 is not 0):
                no_of_spaces -= 1
                #print('spaces', no_of_spaces)
            spaces = '\n' + " " * no_of_spaces
            self.insert(tk.INSERT, spaces)

        #x, y = self.index(tk.INSERT).split('.')
        #x2, y2 = self.index('end-1c').split('.')
        #if x == x2:
        self.see(self.index(tk.INSERT)) 
        
        # on Return ends:
        self.correctLine()
        
        return 'break'
    
    def highlightThisLine(self, event=None):

        index = self.index('insert linestart')
        line = index.split('.')[0]
        
        line = int(line)
        
        
        if line > 0:
            self.highlight(lineNumber=line)

    
    def correctLine(self, event=None):
        index = self.index(tk.INSERT).split(".")
        line = int(index[0])
        line -= 1
        line_text = self.get("%d.%d" % (line, 0), "%d.end" % (line))
        self.delete("%d.0" % (line), "%d.end" %(line))
        self.insert("%d.0" % (line), line_text)
        
        if line > 0:
            self.highlight(lineNumber=line)

    def correctLineUp(self, event=None):
        index = self.index(tk.INSERT).split(".")
        line = int(index[0])
        line += 1
        line_text = self.get("%d.%d" % (line, 0), "%d.end" % (line))
        self.delete("%d.0" % (line), "%d.end" %(line))
        self.insert("%d.0" % (line), line_text)        
        
        if line > 0:
            self.highlight(lineNumber=line)
    
    def correctThisLine(self, event=None):
        ' to do   !!    -> event for <Key-Release>'
        key = event.keycode
        sym = event.keysym
        #print(key)
        #print(sym)
        # parenleft parenright () bracketleft bracketright [] braceleft braceright {}
        
        line = int(self.index(tk.INSERT).split('.')[0])
        line_text = self.get("%d.%d" % (line, 0), "%d.end" % (line))
        
        #for token, content in lex(line, PythonLexer()):


        if key == 51:   # -> #
            if line > 0:
                self.highlight(lineNumber=line)
        
        self.tag_configure("braceHighlight", foreground="red")
        self.tag_configure('parenHighlight', foreground='red')
        self.tag_configure('bracketHighlight', foreground='red')
                
        # paren ()
        if sym == 'parenleft':
            x = self.isBalancedParen(line_text)
            if x == False:
                z = line_text.rfind('(')
            else:
                z = False
            
            if z:
                self.tag_add("parenHighlight", "%d.%d"%(line, z), "%d.%d"%(line, z+1)) 
            else:
                self.tag_remove('parenHighlight', "%d.0"%(line), '%d.end'%(line))
        
        elif sym == 'parenright':
            x = self.isBalancedParen(line_text)
            if x == False:
                z = line_text.rfind(')')
            else:
                z = False
            
            if z:
                self.tag_add("parenHighlight", "%d.%d"%(line, z), "%d.%d"%(line, z+1)) 
            else:
                self.tag_remove('parenHighlight', "%d.0"%(line), '%d.end'%(line))
        
        # bracket []
        elif sym == 'bracketleft':
            x = self.isBalancedBracket(line_text)
            if x == False:
                z = line_text.rfind('[')
            else:
                z = False
            
            if z:
                self.tag_add("bracketHighlight", "%d.%d"%(line, z), "%d.%d"%(line, z+1)) 
            else:
                self.tag_remove('bracketHighlight', "%d.0"%(line), '%d.end'%(line))
        
        elif sym == 'bracketright':
            x = self.isBalancedBracket(line_text)
            if x == False:
                z = line_text.rfind(']')
            else:
                z = False
            
            if z:
                self.tag_add("bracketHighlight", "%d.%d"%(line, z), "%d.%d"%(line, z+1)) 
            else:
                self.tag_remove('bracketHighlight', "%d.0"%(line), '%d.end'%(line))
        
        # brace {}
        elif sym == 'braceleft':
            x = self.isBalancedBrace(line_text)
            if x == False:
                z = line_text.rfind('{')
            else:
                z = False
            
            if z:
                self.tag_add("braceHighlight", "%d.%d"%(line, z), "%d.%d"%(line, z+1)) 
            else:
                self.tag_remove('braceHighlight', "%d.0"%(line), '%d.end'%(line))
        
        elif sym == 'braceright':
            x = self.isBalancedBrace(line_text)
            if x == False:
                z = line_text.rfind('}')
            else:
                z = False
            
            if z:
                self.tag_add("braceHighlight", "%d.%d"%(line, z), "%d.%d"%(line, z+1)) 
            else:
                self.tag_remove('braceHighlight', "%d.0"%(line), '%d.end'%(line))


        else:
            return
        
    def isBalanced(self, txt):
        braced = 0
        for ch in txt:
            if (ch == '(') or (ch == '[') or (ch == '{'): 
                braced += 1
            if (ch == ')') or (ch == ']') or (ch == '}'):
                braced -= 1
                if braced < 0: return False
        return braced == 0


    def isBalancedParen(self, txt):
        braced = 0
        for ch in txt:
            if ch == '(': braced += 1
            if ch == ')':
                braced -= 1
                if braced < 0: return False
        return braced == 0

    def isBalancedBracket(self, txt):
        braced = 0
        for ch in txt:
            if ch == '[': braced += 1
            if ch == ']':
                braced -= 1
                if braced < 0: return False
        return braced == 0

    def isBalancedBrace(self, txt):
        braced = 0
        for ch in txt:
            if ch == '{': braced += 1
            if ch == '}':
                braced -= 1
                if braced < 0: return False
        return braced == 0

    
    def tab(self, event):
        '''
            make tab(4 * whitespaces) or insert autocomplete when using tab
        '''
        if not self.list:
            self.insert(tk.INSERT, " " * self.tabWidth)
        else:
            l = len(self.charstring)
            x, y = self.index(tk.INSERT).split(".")
            y2 = int(y) - l
            y2 = str(y2)
            pos = x + '.' + y2
            self.mark_set('insert', pos)
            self.tag_add("sel", pos, '%d.%d' % (int(x), int(y)))
            self.insert(tk.INSERT, self.list[0])
            if self.tag_ranges("sel"):      # test if selection...
                self.delete('sel.first', 'sel.last')
            self.charstring == ''
            self.entry.config(text='---')
            self.list = []
            self.highlight()

        return 'break'
    
    def backtab(self, event):
        '''
            make backtab when using backspace
        '''
        self.entry.config(text='---')
        self.list = []
        self.charstring = ''

        chars = self.get("insert linestart", 'insert')
        if not self.tag_ranges("sel"):
            if chars.isspace():     # only if there are whitespaces !
                if len(chars) >= 4:
                    self.delete("insert-4c", "insert")
                    return 'break'
        
        self.correctThisLine(event)
    
    def highlightOpen(self, text):
        index = self.index(tk.INSERT).split(".")
        line_no = int(index[0])
        
        lines = text.split('\n')
        i = 1
        
        for line in lines:
            self.insert('%d.0' % i, line)

            self.mark_set("range_start", '%d.0' %i)

            
            for token, content in lex(line, PythonLexer()):
                # Debug
                #print(token)

                self.tag_configure("Token.Name", foreground="#FFFFFF")
                self.tag_configure("Token.Text", foreground="#FFFFFF")

                self.tag_configure("Token.Keyword", foreground="#CC7A00")
                self.tag_configure("Token.Keyword.Constant", foreground="#CC7A00")
                self.tag_configure("Token.Keyword.Declaration", foreground="#CC7A00")
                self.tag_configure("Token.Keyword.Namespace", foreground="#CC7A00")
                self.tag_configure("Token.Keyword.Pseudo", foreground="#CC7A00")
                self.tag_configure("Token.Keyword.Reserved", foreground="#CC7A00")
                self.tag_configure("Token.Keyword.Type", foreground="#CC7A00")

                self.tag_configure("Token.Punctuation", foreground="#2d991d")

                self.tag_configure("Token.Name.Class", foreground="#ddd313")
                self.tag_configure("Token.Name.Exception", foreground="#ddd313")
                self.tag_configure("Token.Name.Function", foreground="#298fb5")
                self.tag_configure("Token.Name.Function.Magic", foreground="#298fb5")
                self.tag_configure("Token.Name.Decorator", foreground="#298fb5")

                        
                self.tag_configure("Token.Name.Builtin", foreground="#CC7A00")
                self.tag_configure("Token.Name.Builtin.Pseudo", foreground="#CC7A00")
                        

                self.tag_configure("Token.Operator.Word", foreground="#CC7A00")
                self.tag_configure("Token.Operator", foreground="#FF0000")

                self.tag_configure("Token.Comment", foreground="#767d87")
                self.tag_configure("Token.Comment.Single", foreground="#767d87")
                self.tag_configure("Token.Comment.Double", foreground="#767d87")

                self.tag_configure("Token.Literal.Number.Integer", foreground="#88daea")
                self.tag_configure("Token.Literal.Number.Float", foreground="#88daea")
            # 
                self.tag_configure("Token.Literal.String.Single", foreground="#35c666")
                self.tag_configure("Token.Literal.String.Double", foreground="#35c666")

            

                self.mark_set("range_end", "range_start + %dc" % len(content))
                self.tag_add(str(token), "range_start", "range_end")
                self.mark_set("range_start", "range_end")
                
            self.insert(tk.INSERT, '\n')
            i += 1
            self.update()

    
    def highlight(self, event=None, lineNumber=None):
        '''
            highlight the line where the cursor is ...
        '''
        
        index = self.index(tk.INSERT).split(".")
        line_no = int(index[0])
        if lineNumber == None:
            line_text = self.get("%d.%d" % (line_no, 0),  "%d.end" % (line_no))
            self.mark_set("range_start", str(line_no) + '.0')
        
        elif lineNumber is not None:
            line_text = self.get("%d.%d" % (lineNumber, 0), "%d.end" % (lineNumber))
            self.mark_set("range_start", str(lineNumber) + '.0')

        for token, content in lex(line_text, PythonLexer()):
            # Debug
            #print(token)
            self.tag_configure("Token.Name", foreground="#FFFFFF")
            self.tag_configure("Token.Text", foreground="#FFFFFF")

            self.tag_configure("Token.Keyword", foreground="#CC7A00")
            self.tag_configure("Token.Keyword.Constant", foreground="#CC7A00")
            self.tag_configure("Token.Keyword.Declaration", foreground="#CC7A00")
            self.tag_configure("Token.Keyword.Namespace", foreground="#CC7A00")
            self.tag_configure("Token.Keyword.Pseudo", foreground="#CC7A00")
            self.tag_configure("Token.Keyword.Reserved", foreground="#CC7A00")
            self.tag_configure("Token.Keyword.Type", foreground="#CC7A00")

            self.tag_configure("Token.Punctuation", foreground="#2d991d")

            self.tag_configure("Token.Name.Class", foreground="#ddd313")
            self.tag_configure("Token.Name.Exception", foreground="#ddd313")
            self.tag_configure("Token.Name.Function", foreground="#298fb5")
            self.tag_configure("Token.Name.Function.Magic", foreground="#298fb5")
            self.tag_configure("Token.Name.Decorator", foreground="#298fb5")

                        
            self.tag_configure("Token.Name.Builtin", foreground="#CC7A00")
            self.tag_configure("Token.Name.Builtin.Pseudo", foreground="#CC7A00")
                        

            self.tag_configure("Token.Operator.Word", foreground="#CC7A00")
            self.tag_configure("Token.Operator", foreground="#FF0000")

            self.tag_configure("Token.Comment", foreground="#767d87")
            self.tag_configure("Token.Comment.Single", foreground="#767d87")
            self.tag_configure("Token.Comment.Double", foreground="#767d87")

            self.tag_configure("Token.Literal.Number.Integer", foreground="#88daea")
            self.tag_configure("Token.Literal.Number.Float", foreground="#88daea")
            # 
            self.tag_configure("Token.Literal.String.Single", foreground="#35c666")
            self.tag_configure("Token.Literal.String.Double", foreground="#35c666")



            self.mark_set("range_end", "range_start + %dc" % len(content))
            self.tag_add(str(token), "range_start", "range_end")
            self.mark_set("range_start", "range_end")
    
    def highlightAll(self, event=None):
        '''
            highlight whole document (when loading a file) ... this can taking a few seconds
            if the file is big ..... no better solution found
        '''
        
        code = self.get("1.0", "end-1c")
        #print(code)
        i = 1
        for line in code.splitlines():
            self.index("%d.0" %i)
            self.highlight(lineNumber=i)
            self.update()
            i += 1

    def highlightAll2(self, linesInFile, overlord, event=None):
        '''
            highlight whole document (when loading a file) ... this can taking a few seconds
            if the file is big ..... no better solution found
        '''
        
        code = self.get("1.0", "end-1c")
        #print(code)
        i = 1
        for line in code.splitlines():
            self.index("%d.0" %i)
            self.highlight(lineNumber=i)
            percent = i/linesInFile*100
            percent = round(percent,2)
            overlord.title('Loading ... ' + str(percent) + ' %')
            i += 1


    
    def highlightAllOpen(self, code):
        pass

    def configFont(self):
        '''
            set the font .... tested only in windows .. if you want to make it cross platform
        '''
        system = platform.system().lower()
        if system == "windows":
            self.font = font.Font(family='Consolas', size=self.fontSize)
            self.configure(font=self.font)
        elif system == "linux":
            self.font = font.Font(family='Mono', size=self.fontSize)
            self.configure(font=self.font)

    def SetAutoCompleteList(self):
        '''
            basic autocompleteList with keywords and some important things (for me)
        '''
        self.autocompleteList = ['__init__', '__main__','__name__', '__repr__', '__str__',
                '__dict__', 'args', 'kwargs', "self", "__file__", 'super()'] # autocomplete

        self.kwList = keyword.kwlist
        for item in self.kwList:
            self.autocompleteList.append(item)


class Example(ttk.Frame):
    '''
        The Example App 
    '''

    def __init__(self, master=None):
        super().__init__(master)
        self.pack(expand=True, fill=tk.BOTH)
        self.initUI()
        self.style = ttk.Style()
        self.style.theme_use('clam')

    def initUI(self):
        
        #frame1
        frame1 = ttk.Frame(self)
        frame1.pack(fill=tk.BOTH, expand=True)
        
        # textPad
        self.textPad = TextPad(frame1, undo=True, maxundo=-1, autoseparators=True)
        self.textPad.filename = None
        self.textPad.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        textScrollY = ttk.Scrollbar(self.textPad)
        textScrollY.config(cursor="double_arrow")
        self.textPad.configure(yscrollcommand=textScrollY.set)
        textScrollY.config(command=self.textPad.yview)
        textScrollY.pack(side=tk.RIGHT, fill=tk.Y)

        # autocompleteEntry
        self.autocompleteEntry = tk.Label(self, bg='black', fg='green', text='---', font=('Mono', 13))
        self.autocompleteEntry.pack(side='bottom', fill='y')
        self.textPad.entry = self.autocompleteEntry
        
        self.linenumber = TextLineNumbers(frame1, width=30)
        self.linenumber.attach(self.textPad)
        self.linenumber.pack(side="left", fill="y")
        
        
        self.textPad.bind("<<Change>>", self.on_change)
        self.textPad.bind("<Configure>", self.on_change)

    def on_change(self, event):
        self.linenumber.redraw()
        
        
        
if __name__ == '__main__':
    app = Example()
    app.master.title('Text-Widget with Autocomplete-Label + BackTab + Indent + Syntax Highlighting with pygments')
    app.master.minsize(width=800, height=600)    
    app.mainloop()




