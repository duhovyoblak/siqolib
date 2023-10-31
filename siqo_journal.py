#==============================================================================
# Siqo common library
#------------------------------------------------------------------------------
from   datetime import date, datetime
import pytz
import os

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_INDENT_START =   1
_INDENT_MAX   = 100

_MAX_LINES    = 10000    # Maximalny pocet riadkov v pamati
_CUT_LINES    =   100    # Po presiahnuti _MAX_LINES zostane _CUT_LINES

_UPPER        = '\u250C'
_MID          = '\u2502'
_LOWER        = '\u2514'

_TIME_ZONE    = pytz.timezone('CET')   # Timezone in which Journal runs

#==============================================================================
# package's tools
#------------------------------------------------------------------------------


#==============================================================================
# Journal
#------------------------------------------------------------------------------
class SiqoJournal:
    
    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, name, debug=3, printLine=True, createFile=True, folder='', verbose=False):
        "Call constructor of SiqoJournal and initialise it with empty data"
        
        self.name       = name          # Nazov journalu
        self.user       = ''            # Nazov usera, ktory pouziva journal
        self.debugLevel = debug         # Pocet vnoreni, ktore sa vypisu do journalu
        self.printLine  = printLine     # Ci sa ma journal vypisovat na obrazovku
        self.createFile = createFile    # Ci sa ma journal zapisovat do suboru
        self.folder     = folder        # Folder BEZ koncoveho lomitka, do ktoreho sa bude zapisovat journal na disk
        
        self.indent     = _INDENT_START # Aktualne vnorenie
        self.showAll    = False         # Overrride debugLevel. Ak True, bude sa vypisovat VSETKO
        self.out        = []            # Zoznam vypisanych riadkov, pre zapis na disk
        
        self.reset()
        self.verbose    = verbose       # Ci ma vypisovat info instancii journalu
    
    #==========================================================================
    # API for users
    #--------------------------------------------------------------------------
    def M(self, mess='', force=False, user='', step='' ):
        "Vypise zaznam journalu do terminalu"
        
        #----------------------------------------------------------------------
        # Upravim odsadenie podla step
        #----------------------------------------------------------------------
        if (step == 'IN') and (self.indent < _INDENT_MAX): self.indent += 1
            
        #----------------------------------------------------------------------
        # Head of the line
        #----------------------------------------------------------------------
        if user != '': self.user = user
            
        if self.verbose: ids = f'<{id(self)}>'
        else           : ids = ''
        
        head = '{}{} {}>'.format( ids, datetime.now(_TIME_ZONE).strftime('%d.%m. %H:%M:%S'), self.user )
        
        #----------------------------------------------------------------------
        # Priprava vystupu - line
        #----------------------------------------------------------------------
        line = False
        if ((self.indent <= self.debugLevel) or self.showAll or force) and (self.debugLevel!=0):
            
            line = head
             
            if   step == 'IN' : line += (self.indent-2)*(_MID+' ') + _UPPER + ' ' + mess
            elif step == 'OUT': line += (self.indent-2)*(_MID+' ') + _LOWER + ' ' + mess
            else              : line += (self.indent-1)*(_MID+' ')          + ' ' + mess
        
        #----------------------------------------------------------------------
        # Vystup na obrazovku
        #----------------------------------------------------------------------
        if line and self.printLine: print(line)

        #----------------------------------------------------------------------
        # Vystup do zoznamu v pamati a kontrola pretecenia
        #----------------------------------------------------------------------
        if line: 
            
            self.out.append(line)
            
            #------------------------------------------------------------------
            # Ak zoznam sprav pretiekol
            #------------------------------------------------------------------
            if len(self.out) > _MAX_LINES:
                
                # Pokusim sa odlozit pamat na disk
                self.dumpOut()
                
                # Ponecham poslednych _CUT_LINES sprav
                self.out = self.out[-_CUT_LINES:]

        #----------------------------------------------------------------------
        # Ak islo o emergency vypis, zapis jounal do suboru
        #----------------------------------------------------------------------
        if force: self.dumpOut()
            
        #----------------------------------------------------------------------
        # Upravim odsadenie podla step
        #----------------------------------------------------------------------
        if step == 'OUT': self.indent -= 1
        if self.indent < _INDENT_START: self.indent = _INDENT_START
            
        #----------------------------------------------------------------------
        return len(self.out)-1
    
    #--------------------------------------------------------------------------
    def I(self, mess='', indent=None ):

        if indent is not None: self.indent=indent
        return self.M(mess, step='IN')
    
    #--------------------------------------------------------------------------
    def O(self, mess='' ):
    
        return self.M(mess, step='OUT')
        
    #--------------------------------------------------------------------------
    def getPos(self):
        "Vrati aktualnu dlzku <out> zoznamu"
        
        return len(self.out)
    
    #--------------------------------------------------------------------------
    def setDepth(self, debug):
        "Nastavi pocet vnoreni na zobrazenie"

        # Ak je zmena v nastaveni
        if self.debugLevel != debug:
            
            self.debugLevel = debug
#            self.M('Journal setDepth: debug level={}'.format(self.debugLevel), True)
        
    #--------------------------------------------------------------------------
    def setShow(self):
        "Zacne vypisovat VSETKY spravy"

        self.showAll = True
        return self.M('Journal setShow')
        
    #--------------------------------------------------------------------------
    def endShow(self):
        "Ukonci vypisovanie VSETKYCH sprav"

        self.showAll = False
        return self.M('Journal endShow')
        
    #--------------------------------------------------------------------------
    def showOut(self, a=None, b=None):
        "Vypise zoznam perzistentnych sprav na obrazovku"
        
        if a is None: a = 0
        if b is None: b = len(self.out)

        for mess in self.out[a:b]: print(mess)
        
    #--------------------------------------------------------------------------
    def getLog(self, maxLines=40):
        "Vrati list poslednych <maxLines> sprav v zozname"

        #----------------------------------------------------------------------
        # Ziskam riadky z logu
        #----------------------------------------------------------------------
        toRet = [['Time', 'Log']]
        
        #----------------------------------------------------------------------
        # Ak je journal odkladany do suboru
        #----------------------------------------------------------------------
        if self.createFile:
            
            self.journal.dumpOut()
            logs = self.journal.getFromFile(maxLines)
            
        #----------------------------------------------------------------------
        # Ak je journal ulozeny iba do pamati
        #----------------------------------------------------------------------
        else: 
            logs = self.out[-maxLines:]

        #----------------------------------------------------------------------
        # Sformatujem riadky logu do tabulky [(,)]
        #----------------------------------------------------------------------
        if logs is not None:
            for log in logs: toRet.append( [log[:15], log[17:]] )
                
        toRet.append(['', ''])

        return toRet
        
    #==========================================================================
    # Persistency methods
    #--------------------------------------------------------------------------
    def fileName(self):
        "Returns actual filename for this Journal"
        
        if self.folder != '': return f'{self.folder}/{self.name}.journal'
        else                : return f'{self.name}.journal'
        
    #--------------------------------------------------------------------------
    def dumpOut(self, enc='utf-8'):
        "Zapise journal na koniec suboru <fileName> a vycisti pamat <out>"
        
        if len(self.out)>0 and self.createFile:

            fileName = self.fileName()

            file = open(fileName, "a", encoding=enc)
            for mess in self.out: file.writelines([mess, '\n'])
            file.close()   
        
            self.out.clear()

        # self.M('Journal dumped to {}'.format(fileName))
        
    #--------------------------------------------------------------------------
    def getFromFile(self, maxLines=100, enc='utf-8'):
        "Nacita z disku journal a vrati ho"
        
        toRet = []
        fileName = self.fileName()
        
        #----------------------------------------------------------------------
        # Ak subor existuje, nacitam ho
        #----------------------------------------------------------------------
        if os.path.exists(fileName): 
            
            # Nacitam cely subor
            with open(fileName, "rt", encoding=enc) as file:
                for line in file:
                    toRet.append(line.strip())

        #----------------------------------------------------------------------
        # Vratim poslednych <maxLines> riadkov
        #----------------------------------------------------------------------
        return toRet[-maxLines:]
        
    #--------------------------------------------------------------------------
    def removeFile(self):
        "Zmaze subor journalu z disku"
        
        fileName = self.fileName()
        
        if os.path.exists(fileName): os.remove(fileName)
            
    #==========================================================================
    # Reset journal
    #--------------------------------------------------------------------------
    def reset(self, name=None, user=None):
        "Resetne parametre journalu na default hodnoty"

        if name is not None: self.name = name
        if user is not None: self.user = user
        
        self.indent     = 1
        self.verbose    = False
        self.showAll    = False
        
        # Vycistenie pamate a disku
        self.out.clear()
        self.removeFile()
        
        # Zapis do journalu
        self.M('<< Journal reset, name={}, debug level={} & printLine={} >> {}'.format(self.name, self.debugLevel, self.printLine, date.today().strftime("%A %d.%m.%Y")), True)
        
#------------------------------------------------------------------------------

#==============================================================================
# Journal
#------------------------------------------------------------------------------
print('Siqo journal ver 1.24')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------