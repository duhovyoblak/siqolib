#==============================================================================
# Siqo general library
#------------------------------------------------------------------------------
import pandas        as pd
import os
import pickle
import json
import base64

#==============================================================================
# package's constants
#------------------------------------------------------------------------------

#==============================================================================
# package's variables
#------------------------------------------------------------------------------


#==============================================================================
# Persistency
#------------------------------------------------------------------------------
def lines2str(lines, delim='\n'):
    
    toRet = ''

    for line in lines:
        toRet = toRet + line + delim
        
    return toRet
    
#------------------------------------------------------------------------------
def loadFile(journal, fileName):
    
    toRet = []
    
    if os.path.exists(fileName): 
        
        with open(fileName) as file:
            toRet = [line.replace('\n', '') for line in file]

        journal.M(f'SIQO.loadFile: From {fileName} was loaded {len(toRet)} lines')
        
    else: journal.M(f'SIQO.loadFile: ERROR File {fileName} does not exist', True)
    
    return toRet

#------------------------------------------------------------------------------
def saveFile(journal, fileName, lines):
    
    with open(fileName, 'w') as file:

        for line in lines:
            file.write(line)

    journal.M(f'SIQO.saveFile: File {fileName} was saved')
        
#------------------------------------------------------------------------------
def loadJson(journal, fileName, enc='utf-8'):
    
    toret = None
    
    if os.path.exists(fileName): 
        
        with open(fileName, encoding=enc) as file:
            toret = json.load(file)
            
        journal.M('SIQO.loadJson: From {} was loaded {} entries'.format(fileName, len(toret)))
        
    else: journal.M('SIQO.loadJson: ERROR File {} does not exist'.format(fileName), True)
    
    return toret

#------------------------------------------------------------------------------
def dumpJson(journal, fileName, data, enc='utf-8'):
    
    try:
        file = open(fileName, "w", encoding=enc)
        json.dump(data, file, indent = 6)
        file.close()    

        journal.M('SIQO.dumpJson: {} saved'.format(fileName))

    except Exception as err:
        journal.M('SIQO.dumpJson: {} ERROR {}'.format(fileName, err), True)
    
#------------------------------------------------------------------------------
def dumpCsv(journal, fileName, data):

    df = pd.DataFrame(data)
    df.to_csv(fileName, index=False)    
    
    journal.M('SIQO.dumpCsv: {} saved'.format(fileName))

#------------------------------------------------------------------------------
def picObj(journal, fileName, obj):
    
    dbfile = open(fileName, 'wb')
    pickle.dump(obj, dbfile)
    dbfile.close()
    
    journal.M('SIQO.picObj: {} saved'.format(fileName))

#------------------------------------------------------------------------------
def unPicObj(journal, fileName):
    
    dbfile = open(fileName, 'rb')
    obj = pickle.load(dbfile)
    dbfile.close()
    
    journal.M('SIQO.unPicObj: {} loaded'.format(fileName))
    return obj

#==============================================================================
# Tools
#------------------------------------------------------------------------------
def dictLen(dct, left=99):
    "Returns len of immersed dictionaries"
    
    toRet = 0
    
    for val in dct.values():
        
        if (type(val) in {dict, list}) and (left>0): toRet += dictLen(val, left-1)
        else                                       : toRet += 1
            
    return toRet

#------------------------------------------------------------------------------
def dictSort(dct, sortKey=(1,), reverse=False):
    "Returns sorted dictionary"
    
    toRet = dct
    
    try:
        if len(sortKey) == 1: 
            toRet = dict( sorted(dct.items(), key=lambda item: item[sortKey[0]], reverse=reverse) )
    
        else:
            toRet = dict( sorted(dct.items(), key=lambda item: item[sortKey[0]][sortKey[1]], reverse=reverse) )
            
    finally:
        return toRet

#------------------------------------------------------------------------------
def listSort(lst, key, reverse=False):
    "Returns sorted list of dictionaries"
    
    return sorted(lst, key=lambda d: d[key])

#------------------------------------------------------------------------------
def b64enc(s):

    return base64.b64encode(s.encode("ascii")).decode('ascii')
    
#------------------------------------------------------------------------------
def b64dec(s):
    
    return base64.b64decode(s.encode('ascii')).decode('ascii')
    
#------------------------------------------------------------------------------
def getPasw(journal, con, user):
    
    journal.I(f"SIQO.getPasw: '{con}', '{user}'")
    
    envKey   = f'PWD_{con.upper()}_{user.upper()}'
    b64_pasw = os.environ.get(envKey, None)
    
    if b64_pasw is None:
        journal.M(f"SIQO.getPasw: WARNING - Password for '{envKey}' does not exist", True)
        journal.O()
        return None
    
    journal.O()
    return b64dec(b64_pasw)

#==============================================================================
#   Inicializacia kniznice
#------------------------------------------------------------------------------
print('SIQO general library ver 1.08')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------