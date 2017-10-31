# configuration.py

import configparser
import os
import sys

class Configuration():
    
    def __init__(self):
        
        self.config = configparser.ConfigParser()
        file = self.getDir()
        #print(file)
        self.config.read(file)
        
        #print('Test ...')
        #print(self.config.sections())        # liest alle Sections ..... [Run] [Terminal] [Interpreter]
        #print(self.config['Run']['mate'])    # liest ['Run']['mate'] ....  mate-terminal -x sh ...
        #print('---\n')
        
    def getDir(self):
        #print('__file__' + __file__)
        if getattr(sys, 'frozen', False):
            dir = os.path.realpath(sys._MEIPASS)
        else:
            dir = os.path.realpath(__file__)      # Pfad ermitteln
        
        basename = os.path.dirname(dir)
        if '\\' in basename:
            basename = basename.replace('\\', '/')

        dir = basename + '/crossviper.ini'
        #print('dir: ' + dir)
        return dir
        
    def getRun(self, system):
        return self.config['Run'][system]
    
    def getTerminal(self, system):
        return self.config['Terminal'][system]
    
    def getInterpreter(self, system):
        return self.config['Interpreter'][system]
    
    def getSystem(self):
        return self.config['System']['system']
    
    def getPassword(self):
        return self.config['Password']['password']
    
    def setSystem(self, system):
        self.config['System']['system'] = system
        if getattr(sys, 'frozen', False):
            thisFile = os.path.realpath(sys._MEIPASS)
        else:
            thisFile = os.path.realpath(__file__)      # Pfad ermitteln

        base = os.path.dirname(thisFile)
        # print('base' + base)
        if '\\' in base:
            base = base.replace('\\', '/')

        iniPath = base + "/crossviper/crossviper.ini"
        with open(iniPath, 'w') as f:
            self.config.write(f)
    
    def setPassword(self, password):
        self.config['Password']['password'] = password
        if getattr(sys, 'frozen', False):
            thisFile = os.path.realpath(sys._MEIPASS)
        else:
            thisFile = os.path.realpath(__file__)      # Pfad ermitteln

        base = os.path.dirname(thisFile)
        if '\\' in base:
            base = base.replace('\\', '/')
        
        iniPath = base + "/crossviper.ini"
        with open(iniPath, 'w') as f:
            self.config.write(f)

    
if __name__ == '__main__':
    c = Configuration()

    system = c.getSystem()
    runCommand = c.getRun(system)
    terminalCommand = c.getTerminal(system)
    interpreterCommand = c.getInterpreter(system)
    
    # c.setSystem('mate')     # funktioniert
 
    print(system + ':\n' + runCommand + '\n' + terminalCommand + '\n' + interpreterCommand) 
    
    '''
    runMate = c.getRun('mate')
    print(runMate)

    system = c.getSystem('mate')
    print(system)
    '''