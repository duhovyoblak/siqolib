#==============================================================================
# Class SiqoConnect as an abstract class 
#------------------------------------------------------------------------------
import sys
import os
import re
import pytz

from   datetime      import datetime, timedelta
from   siqo_hosts    import hosts

env = 'localPython'
hst = 'PC'


#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_TIME_ZONE    = pytz.timezone('CET')   # Timezone in which Journal runs
_TIME_WATCH   = 5                      # Logovanie prikazov trvajucich viac sekund
_PING_LAG     = 10                     # Pocet hodin do najblizsieho ping-u
_QRY_SAMPLE   = 60                     # Dlzka QRY na zobrazenie
 
#==============================================================================
# package's variables
#------------------------------------------------------------------------------

#==============================================================================
# SiqoConnect
#------------------------------------------------------------------------------
class SiqoConnect:
    
    #==========================================================================
    # Static variables & methods
    #--------------------------------------------------------------------------
    conf          = {}     # connects configuration
    cons          = {}     # Zoznam konekcii     {conId: {<conObj>}}

    _PING_LAG     = 1      # Time between ping in hours
    _KINIT_LAG    = 3      # Time between kinit in hours

    #--------------------------------------------------------------------------
    @staticmethod
    def infoAll(who):
        "Returns info about all connections"

        dat = {}
        msg = []

        msg.append('<<CONNECTIONS>>')

        for conId, conObj in SiqoConnect.cons.items():

            sub = conObj.info(who)

            dat[conId] = sub['dat']
            msg.append(f"{50*'-'} {conId}")
            msg.extend(sub['msg'])

        return {'res':'OK', 'dat':dat, 'msg':msg}

    #--------------------------------------------------------------------------
    @staticmethod
    def getConnect(srvId, con):
        "Returns connection object for given con"

        conId = f'{srvId}.{con}'

        if conId in SiqoConnect.cons.keys(): return SiqoConnect.cons[conId]
        else                               : return None

    #--------------------------------------------------------------------------
    @staticmethod
    def initConnect(journal, srvId, con, who, pasw=None):
        "Creates and initialises <con> connection. Returns conObj"

        #----------------------------------------------------------------------
        # Nacitam konfiguraciu konekcie
        #----------------------------------------------------------------------
        SiqoConnect.loadConf(journal)

        if con not in SiqoConnect.conf.keys():
            journal.M(f'{con}.initConnect: Connection {con} does not exists in configuration file', True)
            return None

        #----------------------------------------------------------------------
        # Skontrolujem, ci je sluzba funkcna
        #----------------------------------------------------------------------
        conf = SiqoConnect.conf[con]

        if conf['func']!='Y':
            journal.M(f'{con}.initConnect: Connection {con} is not active', True)
            return None

        #----------------------------------------------------------------------
        # Zistim credentials
        #----------------------------------------------------------------------
        user = conf['user']
        
        if pasw is None: pasw = gen.getPasw(journal, con, user)
        if pasw is None: pasw = _NOPAS
        
        #----------------------------------------------------------------------
        # Skorigujem nazov konekcie pre API konekcie
        #----------------------------------------------------------------------
        if con == _AUTH: con = f'{_AUTH}{who}'
        
        #----------------------------------------------------------------------
        # Vytvorim instanciu konekcie
        #----------------------------------------------------------------------
        journal.I(f"{con}.initConnect: For user '{user}'/'{who}'")

        if   conf['type'] == 'oracle':

            if env == 'docker': from   .SiqoConnect_oracle  import SiqoConnect_oracle
            else              : from   SiqoConnect_oracle   import SiqoConnect_oracle

            try: conObj = SiqoConnect_oracle(journal, srvId, con, conf, who, pasw)
            except Exception as err:
                journal.M(f'{con}.oracle.initConnect: ERROR {err}', True)
                journal.O('')
                return None

        elif conf['type'] == 'python':

            if env == 'docker': from   .SiqoConnect_python  import SiqoConnect_python
            else              : from   SiqoConnect_python   import SiqoConnect_python

            try: conObj = SiqoConnect_python(journal, srvId, con, conf, who, pasw)
            except Exception as err:
                journal.M(f'{con}.python.initConnect: ERROR {err}', True)
                journal.O('')
                return None

        elif conf['type'] == 'impala':

            if env == 'docker': from   .SiqoConnect_impala  import SiqoConnect_impala
            else              : from   SiqoConnect_impala   import SiqoConnect_impala

            try: conObj = SiqoConnect_impala(journal, srvId, con, conf, who, pasw)
            except Exception as err:
                journal.M(f'{con}.impala.initConnect: ERROR {err}', True)
                journal.O('')
                return None

        else:
            journal.M('{}.initConnect: ERROR - {} is unknown connection type of {}'.format('SiqoConnect.initconnects', con, conf['type']), True)
            journal.O('')
            return None

        #----------------------------------------------------------------------
        journal.O('')
        return conObj

    #--------------------------------------------------------------------------
    @staticmethod
    def delConnect(journal, srvId, con):
        "Removes conObj for respective con from cons and deletes conObj"

        journal.I(f'SiqoConnect.delConnect: {srvId}.{con}')

        #----------------------------------------------------------------------
        # Kontrola pred zmazanim konekcie
        #----------------------------------------------------------------------
        if SiqoConnect.getConnect(srvId, con) is None:
            journal.M(f'SiqoConnect.delConnect: Service {srvId}.{con} does not exist, command is denied', True)
            journal.O('')
            return {'res':'ER', 'msg':[f'Service {srvId}.{con} does not exist. Command denied'], 'dat':{}, 'obj':None}

        else:
            #------------------------------------------------------------------
            # Ziskam konekciu zo zoznamu a deaktivujem ju
            #------------------------------------------------------------------
            conToDel = SiqoConnect.cons.pop(f'{srvId}.{con}')
            if conToDel is not None: del conToDel

            journal.O(f'SiqoConnect.delConnect: Service {srvId}.{con} was deleted')
            return {'res':'OK', 'msg':[f'Connection {srvId}.{con} was deleted'], 'dat':{}, 'obj':None}

    #--------------------------------------------------------------------------
    @staticmethod
    def saveConf(journal):
        "Saves current connects configuration"

        journal.I('{}.saveConf'.format('SiqoConnect'))
        gen.dumpJson(journal, CONNECTS_CONF, SiqoConnect.conf)
        journal.O('')

    #--------------------------------------------------------------------------
    @staticmethod
    def loadConf(journal):
        "Loads current connects configuration"

        journal.I('{}.loadConf'.format('SiqoConnect'))
        SiqoConnect.conf = gen.loadJson(journal, CONNECTS_CONF)
        journal.O('')

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, journal, name, notes='')
        "Call constructor of SiqoConnect and initialise it"
        
        journal.I(f'SiqoConnect.init:{name}')
        
        self.journal     = journal      # Odkaz na globalny journal
        self.name        = name         # Nazov konekcie
        self.notes       = notes        # Poznamky ku konekcii

        self.user        = ''           # User        
        self.host        = ''           # Nazov hostu
        self.port        = ''           # Cislo portu ako string
        self.service     = ''           # Nazov service 
        self.keytab      = ''           # Nazov keytab file 
        self.enc         = 'UTF-8'      # encoding
        self.prop        = {}           # User defined properties
        self.initialised = False        # Status of the connection

        self.eng         = None         # Objekt driver engine
        self.cur         = None         # Objekt kurzor
        
        self.lastPing    = None         # Time of last ping
        self.lastKinit   = None         # Time of last kinit

        self.journal.O(f'{self.name}.init: done')
        
    #==========================================================================
    # API for users
    #--------------------------------------------------------------------------
    def info(self, who):
        "Returns info about the connect"
 
        dat = {}
        msg = []

        dat['name'       ] = self.name
        dat['notes'      ] = self.notes

        dat['type'       ] = self.type
        dat['user'       ] = self.user
        dat['host'       ] = self.host
        dat['port'       ] = self.port
        dat['service'    ] = self.service
        dat['keytab'     ] = self.keytab
        dat['enc'        ] = self.enc
        dat['initialised'] = self.initialised

        dat['lastPing'   ] = self.lastPing. strftime('%d.%m. %H:%M:%S')
        dat['lastKinit'  ] = self.lastKinit.strftime('%d.%m. %H:%M:%S')
        
        for key, val in self.prop.items():
            dat[key] = val

        # Transformacia do message
        for key, val in dat.items(): msg.append('{:<15}: {}'.format(key, val))

        return {'who':who, 'res':'OK', 'dat':dat, 'msg':msg, 'obj':self}

    #--------------------------------------------------------------------------
    def isInitialised(self):
        "Returns True if connect is initialised"

        return self.initialised

    #--------------------------------------------------------------------------
    def prop(self, key, default=None):
        "Returns user defined property"

        if key in self.prop.keys(): return self.prop[key]
        else                      : return default

    #==========================================================================
    # Open&close connection
    #--------------------------------------------------------------------------
    def openConn(self, pasw):
        "Opens connection"

        self.journal.M('{}.openConn: This is abstract method only. You should use inherited object'.format(self.con), True)
        return { 'dbServ':self.host, 'dbServId':-1, 'eng':None, 'cur':None}

    #--------------------------------------------------------------------------
    def commitConn(self):
        "Commits open transaction"

        self.journal.M('{}.commitConn: This is abstract method only. You should use inherited object'.format(self.con), True)

    #--------------------------------------------------------------------------
    def closeConn(self):
        "Close opened session/connection"

        self.journal.M('{}.closeConn: This is abstract method only. You should use inherited object'.format(self.con), True)

    #--------------------------------------------------------------------------
    def ping(self, who, force=False):
        "Ping this connection. Returns true if succeed"

        self.journal.M('{}.ping: This is abstract method only. You should use inherited object. Force = {}'.format(self.con, force))
        return self.initialised

    #--------------------------------------------------------------------------
    def kinit(self, who, force=False):
        "Kinit/refresh ticket this connection."

        self.journal.M('{}.kinit: This is abstract method only. You should use inherited object. Force = {}'.format(self.con, force))


#==============================================================================
#   Inicializacia kniznice
#------------------------------------------------------------------------------
print('SiqoConnect ver 1.00')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------