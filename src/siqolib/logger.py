#==============================================================================
# Siqo common library
#------------------------------------------------------------------------------
import os
import functools
import logging
import inspect
from   datetime                      import datetime

deployment = os.getenv("monDeploy", "local")

if deployment.startswith("edg-") or deployment.startswith("aws-"):

    from  .siqo_singleton              import SingletonMeta
    from  .siqo_general                import TIME_ZONE

else:
    from  siqo_singleton              import SingletonMeta
    from  siqo_general                import TIME_ZONE

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_VER = '1.1'

_LOGGER_NAME             = 'siqoLogger'
_LOGGER_LEVEL            = 'WARNING'
_LOGGER_FILE             = False
_LOGGER_CONSOLE          = True
_LOGGER_FILENAME         = 'siqoLogger'
_LOGGER_FILENAME_POSTFIX = '.log'
_LOGGER_FILE_MODE        = 'w'
_LOGGER_FORMAT           = '%(asctime)s | %(levelname)-8s | %(process)6d | %(filename)22s:%(lineno)-5s | %(message)s'
_LOGGER_AUDIT            = 90       # Custom log level for audit messages

_MAX_LINES               = 10000    # Maximalny pocet riadkov v pamati
_CUT_LINES               =  9000    # Po presiahnuti _MAX_LINES zostane _CUT_LINES

_TIME_WARNING            = 20

#==============================================================================
# package's variables
#------------------------------------------------------------------------------
_timeStats = {}   # Dict to store time duration for functions {functon_name: [start_time, duration]}

#----------------------------------------------------------------------
# Add AUDTIT level to the logging module
#----------------------------------------------------------------------
logging.addLevelName(_LOGGER_AUDIT, 'AUDIT')
logging.AUDIT = _LOGGER_AUDIT

#==============================================================================
# Alarm stopwatch decorator
#------------------------------------------------------------------------------
def stopWatch(function):
    "Measures and print time elapsed by calling the function"

    #--------------------------------------------------------------------------
    # Interna wrapper funkcia
    #--------------------------------------------------------------------------
    @functools.wraps(function)
    def wrapper(*args, **kwargs):

        #----------------------------------------------------------------------
        # Before decorated function
        #----------------------------------------------------------------------
        start = datetime.now()

        #----------------------------------------------------------------------
        # Actual call function
        #----------------------------------------------------------------------
        resp = function(*args, **kwargs)

        #----------------------------------------------------------------------
        # After decorated function
        #----------------------------------------------------------------------
        stop = datetime.now()
        dur  = stop - start

        #----------------------------------------------------------------------
        # Store time duration for the function
        #----------------------------------------------------------------------
        if function.__name__ not in _timeStats: _timeStats[function.__name__] = []
        _timeStats[function.__name__].append([start, dur.total_seconds()])

        if dur.total_seconds() > _TIME_WARNING:
            logger = SiqoLogger()
            logger.warning(f"{function.__name__}() took {dur.seconds} seconds to complete TIME WARNING")

        #----------------------------------------------------------------------
        return resp

    #--------------------------------------------------------------------------
    # Koniec internej wrapper fcie
    #--------------------------------------------------------------------------
    return wrapper

#------------------------------------------------------------------------------
def asyncStopWatch(function):
    "Measures and print time elapsed by calling the function"

    #--------------------------------------------------------------------------
    # Interna wrapper funkcia
    #--------------------------------------------------------------------------
    @functools.wraps(function)
    async def wrapper(*args, **kwargs):

        #----------------------------------------------------------------------
        # Before decorated function
        #----------------------------------------------------------------------
        start = datetime.now()

        #----------------------------------------------------------------------
        # Actual call function
        #----------------------------------------------------------------------
        resp = await function(*args, **kwargs)

        #----------------------------------------------------------------------
        # After decorated function
        #----------------------------------------------------------------------
        stop = datetime.now()
        dur  = stop - start

        #----------------------------------------------------------------------
        # Store time duration for the function
        #----------------------------------------------------------------------
        if function.__name__ not in _timeStats: _timeStats[function.__name__] = []
        _timeStats[function.__name__].append([start, dur.total_seconds()])

        if dur.total_seconds() > _TIME_WARNING:
            logger = SiqoLogger()
            logger.warning(f"{function.__name__}() took {dur.seconds} seconds to complete TIME WARNING")

        #----------------------------------------------------------------------
        return resp

    #--------------------------------------------------------------------------
    # Koniec internej wrapper fcie
    #--------------------------------------------------------------------------
    return wrapper

#==============================================================================
# SiqoLogger
#------------------------------------------------------------------------------
class SiqoLogger(metaclass=SingletonMeta):

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self,
                 name:      str  = _LOGGER_NAME,
                 logFile:   bool = _LOGGER_FILE,
                 fileName:  str  = _LOGGER_FILENAME,
                 fileMode:  str  = _LOGGER_FILE_MODE,
                 logConsole:bool = _LOGGER_CONSOLE,
                 level:     str  = _LOGGER_LEVEL):
        """
        Constructor for SiqoLogger class.
        Initializes the logger with the specified parameters.
        """

        #----------------------------------------------------------------------
        # Vytvorim logger
        #----------------------------------------------------------------------
        self.name       = name                     # Názov loggera
        self.logFile    = logFile                  # Logovanie do súboru?
        self.fileName   = fileName                 # Názov súboru pre logovanie
        self.fileMode   = fileMode                 # Režim zápisu do súboru (napr. 'w' pre zápis, 'a' pre pripojenie)
        self.logConsole = logConsole               # Logovanie do konzoly?
        self._logger    = logging.getLogger(name)  # Vytvorenie loggera
        self._msgs      = []                       # Zoznam vypisanych riadkov [(timestamp, level, filename:lineno, message)]

        #----------------------------------------------------------------------
        # Inicializujem logger
        #----------------------------------------------------------------------

        formater = logging.Formatter(_LOGGER_FORMAT)

        if logFile:

            fileHandler = logging.FileHandler(fileName + _LOGGER_FILENAME_POSTFIX, mode=fileMode)
            fileHandler.setFormatter(formater)
            self._logger.addHandler(fileHandler)

        if logConsole:

            consoleHandler = logging.StreamHandler()
            consoleHandler.setFormatter(formater)
            self._logger.addHandler(consoleHandler)

        #----------------------------------------------------------------------
        # Nastavim uroven logovania
        #----------------------------------------------------------------------
        self.setLevel(level, 'SiqoLogger.__init__')

        #----------------------------------------------------------------------
        self.info(f'SiqoLogger initialized with file={logFile}, filename={fileName}, fileMode={fileMode}, console={logConsole}, level={level}')

    #--------------------------------------------------------------------------
    def _callerInfo(self):
        "Get the filename and line number of the caller function"

        # [0] je táto funkcia, [1] je logger, [2] je volajúci
        currFrame   = inspect.currentframe()
        outerFrames = inspect.getouterframes(currFrame)

        #----------------------------------------------------------------------
        # Bezpečne zisti volajúceho, ak stack nie je dosť hlboký
        #----------------------------------------------------------------------
        if   len(outerFrames) > 3: callerFrame = outerFrames[3]
        elif len(outerFrames) > 1: callerFrame = outerFrames[1]
        else                     : callerFrame = currFrame

        #----------------------------------------------------------------------
        # Získam názov súboru a číslo riadku volajúcej funkcie
        #----------------------------------------------------------------------
        fileName = callerFrame.filename
        lineNo   = callerFrame.lineno

        return fileName, lineNo

    #--------------------------------------------------------------------------
    def _addRecord(self, record: logging.LogRecord):
        "Add message into list of messages. Retain only the last _MAX_LINES messages in memory"

        formatted = self._logger.handlers[0].formatter.format(record)

        #----------------------------------------------------------------------
        # Vytvorim formatovany zaznam do zoznamu sprav
        #----------------------------------------------------------------------
        # Struktura: [timestamp, level, filename:lineno, message]

        row = [col for col in formatted.split('|')]
        self._msgs.append(row)

        #----------------------------------------------------------------------
        # Retencia zoznamu sprav
        #----------------------------------------------------------------------
        if len(self._msgs) > _MAX_LINES:
            self._msgs = self._msgs[-_CUT_LINES:]

    #==========================================================================
    # API for users settings
    #--------------------------------------------------------------------------
    def setLevel(self, level, who=''):
        "Nastaví úroveň logovania (napr. logging.DEBUG, logging.INFO, ...)"

        if type(level) is str:

            if   level.upper() == 'DEBUG'   : level = logging.DEBUG
            elif level.upper() == 'INFO'    : level = logging.INFO
            elif level.upper() == 'WARNING' : level = logging.WARNING
            elif level.upper() == 'ERROR'   : level = logging.ERROR
            elif level.upper() == 'CRITICAL': level = logging.CRITICAL
            elif level.upper() == 'AUDIT'   : level = logging.AUDIT
            else:
                self.error(f'{self.name}.setLevel: Unknown logging level: {level}')
                return

        #----------------------------------------------------------------------
        self._logger.setLevel(level)
        self.audit(f"{self.name}.setLevel: Logger level was set to {self.getLevel()} by '{who}'")

    #--------------------------------------------------------------------------
    def getLevel(self, name=True):
        "Vrati aktualnu uroven logovania. Ak je name=True, vrati nazov levelu"

        level = self._logger.level

        if not name: return level

        #----------------------------------------------------------------------
        # Map numeric level to string name
        #----------------------------------------------------------------------
        if   level >= logging.AUDIT   : name = 'AUDIT'
        elif level >= logging.CRITICAL: name = 'CRITICAL'
        elif level >= logging.ERROR   : name = 'ERROR'
        elif level >= logging.WARNING : name = 'WARNING'
        elif level >= logging.INFO    : name = 'INFO'
        elif level >= logging.DEBUG   : name = 'DEBUG'
        elif level >= 0               : name = 'NOTSET'
        else: name = 'UNKNOWN'

        #----------------------------------------------------------------------
        return name

    #--------------------------------------------------------------------------
    def getLog(self, maxLines=40):
        "Vrati list poslednych <maxLines> sprav v zozname"

        toRet= self._msgs[-maxLines:]

        #----------------------------------------------------------------------
        return toRet

    #--------------------------------------------------------------------------
    def getTimes(self):
        "Return dict of durations of functions"

        return _timeStats

    #==========================================================================
    # API for users: logging methods
    #--------------------------------------------------------------------------
    def debug(self, message: str):
        "Log a debug message"

        #----------------------------------------------------------------------
        # Ak je uroven logovania vyssia ako DEBUG, tak nic nerobim
        #----------------------------------------------------------------------
        if self._logger.level > logging.DEBUG: return
        #----------------------------------------------------------------------

        filename, lineno = self._callerInfo()
        self._logger.debug(message, stacklevel=3)

        record = self._logger.makeRecord(self._logger.name, logging.DEBUG, filename, lineno, message, None, None )
        self._addRecord(record)

    #--------------------------------------------------------------------------
    def info(self, message: str):
        "Log an info message"

        #----------------------------------------------------------------------
        # Ak je uroven logovania vyssia ako INFO, tak nic nerobim
        #----------------------------------------------------------------------
        if self._logger.level > logging.INFO: return
        #----------------------------------------------------------------------

        filename, lineno = self._callerInfo()
        self._logger.info(message, stacklevel=3)

        record = self._logger.makeRecord(self._logger.name, logging.INFO,filename, lineno, message, None, None )
        self._addRecord(record)

    #--------------------------------------------------------------------------
    def warning(self, message: str):
        "Log a warning message"

        #----------------------------------------------------------------------
        # Ak je uroven logovania vyssia ako WARNING, tak nic nerobim
        #----------------------------------------------------------------------
        if self._logger.level > logging.WARNING: return
        #----------------------------------------------------------------------

        filename, lineno = self._callerInfo()
        self._logger.warning(message, stacklevel=3)

        record = self._logger.makeRecord(self._logger.name, logging.WARNING, filename, lineno, message, None, None )
        self._addRecord(record)

    #--------------------------------------------------------------------------
    def error(self, message: str):
        "Log an error message"

        #----------------------------------------------------------------------
        # Ak je uroven logovania vyssia ako ERROR, tak nic nerobim
        #----------------------------------------------------------------------
        if self._logger.level > logging.ERROR: return
        #----------------------------------------------------------------------

        filename, lineno = self._callerInfo()
        self._logger.error(message, stacklevel=3)

        record = self._logger.makeRecord(self._logger.name, logging.ERROR, filename, lineno, message, None, None )
        self._addRecord(record)

    #--------------------------------------------------------------------------
    def critical(self, message: str):
        "Log a critical message"

        #----------------------------------------------------------------------
        # Ak je uroven logovania vyssia ako CRITICAL, tak nic nerobim
        #----------------------------------------------------------------------
        if self._logger.level > logging.CRITICAL: return
        #----------------------------------------------------------------------

        filename, lineno = self._callerInfo()
        self._logger.critical(message, stacklevel=3)

        record = self._logger.makeRecord(self._logger.name, logging.CRITICAL, filename, lineno, message, None, None )
        self._addRecord(record)

    #--------------------------------------------------------------------------
    def audit(self, message: str):
        "Log a audit message"

        #----------------------------------------------------------------------
        # Ak je uroven logovania vyssia ako AUDIT, tak nic nerobim
        #----------------------------------------------------------------------
        if self._logger.level > logging.AUDIT: return
        #----------------------------------------------------------------------

        filename, lineno = self._callerInfo()
        self._logger.log(_LOGGER_AUDIT, message, stacklevel=3)

        record = self._logger.makeRecord(self._logger.name, logging.AUDIT, filename, lineno, message, None, None )
        self._addRecord(record)

#------------------------------------------------------------------------------

#==============================================================================
# Logger
#------------------------------------------------------------------------------
print(f'Siqo Logger ver {_VER}')

#==============================================================================
# Unit tests
#------------------------------------------------------------------------------
if __name__ == "__main__":

    logger1 = SiqoLogger()
    logger2 = SiqoLogger()

    if id(logger1) == id(logger2): print("Singleton works, both variables contain the same instance.")
    else                         : print("Singleton failed, variables contain different instances.")

    logger1.setLevel(logging.DEBUG)
    logger1.debug   ("This is a debug message."   )
    logger1.info    ("This is an info message."   )
    logger1.warning ("This is a warning message." )
    logger1.error   ("This is an error message."  )
    logger1.critical("This is a critical message.")
    logger1.audit   ("This is an audit message.")

    @stopWatch
    def test_function():
        import time
        time.sleep(1)
        return "Function completed"

    print(test_function())

    print("Logger messages:")
    for msg in logger1.getLog(maxLines=40):
        print(msg)

    #--------------------------------------------------------------------------
    # Znizim uroven logovania na ERROR
    #--------------------------------------------------------------------------
    print("\nChanging logger level to ERROR...")
    print()

    logger1.setLevel('ERROR', 'unitTest')
    logger1.info("This info message should not be logged due to the ERROR level setting.")

    logger1.debug   ("This is a debug message."   )
    logger1.info    ("This is an info message."   )
    logger1.warning ("This is a warning message." )
    logger1.error   ("This is an error message."  )
    logger1.critical("This is a critical message.")
    logger1.audit   ("This is an audit message."  )

    @stopWatch
    def test_function():
        import time
        time.sleep(6)
        return "Function completed"

    print(test_function())

    print(78 * '-')
    for msg in logger1.getLog(maxLines=40):
        print(msg)

    print(78 * '-')
    print("Time statistics:")
    for func, times in logger1.getTimes().items():
        print(f"{func}: {len(times)} calls")
        for start, duration in times:
            print(f"  Start: {start.strftime('%Y-%m-%d %H:%M:%S.%f')}, Duration: {duration:.2f} seconds")

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
