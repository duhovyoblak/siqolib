#==============================================================================
# Siqo general library
#------------------------------------------------------------------------------
import pandas        as pd
import os
import pickle
import json

#==============================================================================
# package's constants
#------------------------------------------------------------------------------

#==============================================================================
# package's variables
#------------------------------------------------------------------------------


#==============================================================================
# Lists methods
#------------------------------------------------------------------------------
def deepCopy(src):
    "Make deep copy of the source"
    
    #--------------------------------------------------------------------------
    # Source is list
    #--------------------------------------------------------------------------
    if   type(src) == list: 
        
        toRet = list()
        for val in src: toRet.append(deepCopy(val))
        
    #--------------------------------------------------------------------------
    # Source is dictionary
    #--------------------------------------------------------------------------
    elif type(src) == dict: 
        
        toRet = dict()
        for key, val in src.items(): toRet[key] = deepCopy(val)
    
    #--------------------------------------------------------------------------
    # Source is set
    #--------------------------------------------------------------------------
    if   type(src) == set: 
        
        toRet = set()
        for val in src: toRet.add(deepCopy(val))
        
    #--------------------------------------------------------------------------
    # Source is primitive object
    #--------------------------------------------------------------------------
    else: toRet = src
    
    #--------------------------------------------------------------------------
    return toRet
    
#==============================================================================
# Persistency
#------------------------------------------------------------------------------
def loadJson(journal, fileName):
    
    toret = None
    
    if os.path.exists(fileName): 
        
        with open(fileName) as file:
            toret = json.load(file)
            
        journal.M('SIQO.loadJson: From {} was loaded {} entries'.format(fileName, len(toret)))
        
    else: journal.M('SIQO.loadJson: ERROR File {} does not exist'.format(fileName), True)
    
    return toret

#------------------------------------------------------------------------------
def dumpJson(journal, fileName, data):
    
    try:
        file = open(fileName, "w")
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
#   Inicializacia kniznice
#------------------------------------------------------------------------------
print('SIQO general library ver 1.04')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------