#==============================================================================
# Class SiqoConnect as an abstract class
#------------------------------------------------------------------------------
import sys
import os
import re
import pytz

from   datetime      import datetime, timedelta
from   . import general as gen
from   .hosts    import hosts
from   .logger       import SiqoLogger

logger = SiqoLogger('connect')

env = 'localPython'
hst = 'PC'


#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_VER          = '1.0.1'
#------------------------------------------------------------------------------
_AUTH         = 'AUTH'                 # Authentication connection name
_NOPAS        = '***'                  # Placeholder for no password
CONNECTS_CONF = 'connects.conf'        # Configuration file name
#------------------------------------------------------------------------------
_TIME_ZONE    = pytz.timezone('CET')   # Timezone for connections
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
    def initConnect(srvId, con, who, pasw=None):
        "Creates and initialises <con> connection. Returns conObj"

        #----------------------------------------------------------------------
        # Nacitam konfiguraciu konekcie
        #----------------------------------------------------------------------
        SiqoConnect.loadConf()

        if con not in SiqoConnect.conf.keys():
            logger.error(f'connect.initConnect: Connection {con} does not exists in configuration file')
            return None

        #----------------------------------------------------------------------
        # Skontrolujem, ci je sluzba funkcna
        #----------------------------------------------------------------------
        conf = SiqoConnect.conf[con]

        if conf['func']!='Y':
            logger.error(f'connect.initConnect: Connection {con} is not active')
            return None

        #----------------------------------------------------------------------
        # Zistim credentials
        #----------------------------------------------------------------------
        user = conf['user']

        if pasw is None: pasw = gen.getPasw(con, user)
        if pasw is None: pasw = _NOPAS

        #----------------------------------------------------------------------
        # Skorigujem nazov konekcie pre API konekcie
        #----------------------------------------------------------------------
        if con == _AUTH: con = f'{_AUTH}{who}'

        #----------------------------------------------------------------------
        # Vytvorim instanciu konekcie
        #----------------------------------------------------------------------
        logger.info(f"connect.initConnect: For user '{user}'/'{who}'")

        if   conf['type'] == 'oracle':

            if env == 'docker': from   .SiqoConnect_oracle  import SiqoConnect_oracle
            else              : from   .SiqoConnect_oracle  import SiqoConnect_oracle

            try: conObj = SiqoConnect_oracle(srvId, con, conf, who, pasw)
            except Exception as err:
                logger.error(f'connect.oracle.initConnect: ERROR {err}')
                return None

        elif conf['type'] == 'python':

            if env == 'docker': from   .SiqoConnect_python  import SiqoConnect_python
            else              : from   .SiqoConnect_python  import SiqoConnect_python

            try: conObj = SiqoConnect_python(srvId, con, conf, who, pasw)
            except Exception as err:
                logger.error(f'connect.python.initConnect: ERROR {err}')
                return None

        elif conf['type'] == 'impala':

            if env == 'docker': from   .SiqoConnect_impala  import SiqoConnect_impala
            else              : from   .SiqoConnect_impala  import SiqoConnect_impala

            try: conObj = SiqoConnect_impala(srvId, con, conf, who, pasw)
            except Exception as err:
                logger.error(f'connect.impala.initConnect: ERROR {err}')
                return None

        else:
            logger.error(f'connect.initConnect: ERROR - {con} is unknown connection type of {conf["type"]}')
            return None

        #----------------------------------------------------------------------
        logger.info('connect.initConnect: done')
        return conObj

    #--------------------------------------------------------------------------
    @staticmethod
    def delConnect(srvId, con):
        "Removes conObj for respective con from cons and deletes conObj"

        logger.info(f'connect.delConnect: {srvId}.{con}')

        #----------------------------------------------------------------------
        # Kontrola pred zmazanim konekcie
        #----------------------------------------------------------------------
        if SiqoConnect.getConnect(srvId, con) is None:
            logger.error(f'connect.delConnect: Service {srvId}.{con} does not exist, command is denied')
            return {'res':'ER', 'msg':[f'Service {srvId}.{con} does not exist. Command denied'], 'dat':{}, 'obj':None}

        else:
            #------------------------------------------------------------------
            # Ziskam konekciu zo zoznamu a deaktivujem ju
            #------------------------------------------------------------------
            conToDel = SiqoConnect.cons.pop(f'{srvId}.{con}')
            if conToDel is not None: del conToDel

            logger.info(f'connect.delConnect: Service {srvId}.{con} was deleted')
            return {'res':'OK', 'msg':[f'Connection {srvId}.{con} was deleted'], 'dat':{}, 'obj':None}

    #--------------------------------------------------------------------------
    @staticmethod
    def saveConf():
        "Saves current connects configuration"

        logger.info('connect.saveConf: saving connections configuration')
        gen.dumpJson(CONNECTS_CONF, SiqoConnect.conf)
        logger.info('connect.saveConf: done')

    #--------------------------------------------------------------------------
    @staticmethod
    def loadConf():
        "Loads current connects configuration"

        logger.info('connect.loadConf: loading connections configuration')
        SiqoConnect.conf = gen.loadJson(CONNECTS_CONF)
        logger.info('connect.loadConf: done')

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, name, notes=''):
        """Call constructor of SiqoConnect and initialise it"""

        logger.info(f'connect.init: {name}')

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

        logger.info(f'connect.init: {self.name} done')

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

        logger.error('connect.openConn: This is abstract method only. You should use inherited object')
        return { 'dbServ':self.host, 'dbServId':-1, 'eng':None, 'cur':None}

    #--------------------------------------------------------------------------
    def commitConn(self):
        "Commits open transaction"

        logger.error('connect.commitConn: This is abstract method only. You should use inherited object')

    #--------------------------------------------------------------------------
    def closeConn(self):
        "Close opened session/connection"

        logger.error('connect.closeConn: This is abstract method only. You should use inherited object')

    #--------------------------------------------------------------------------
    def ping(self, who, force=False):
        "Ping this connection. Returns true if succeed"

        logger.warning(f'connect.ping: This is abstract method only. Force = {force}')
        return self.initialised

    #--------------------------------------------------------------------------
    def kinit(self, who, force=False):
        "Kinit/refresh ticket this connection."

        logger.warning(f'connect.kinit: This is abstract method only. Force = {force}')


#==============================================================================
#   Inicializacia kniznice
#------------------------------------------------------------------------------
logger.info(f'connect: SiqoConnect library initialized, ver {_VER}')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------