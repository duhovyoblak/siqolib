#==============================================================================
# Siqo common library
#------------------------------------------------------------------------------

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_VER  = '1'

#==============================================================================
# package's variables
#------------------------------------------------------------------------------

#==============================================================================
# Singleton meta class
#------------------------------------------------------------------------------
class SingletonMeta(type):
    """
    Metaclass for creating singleton-like classes.
    To create a singleton class, inherit from this metaclass using argument `metaclass=SingletonMeta`.
    This will ensure that only one instance of the class is created, regardless of how many times it is called.
    """

    #--------------------------------------------------------------------------
    # Class variable to hold the single instance of each class
    #--------------------------------------------------------------------------
    _instances = {}

    #--------------------------------------------------------------------------
    # Override the call operator to ensure that only one instance of the class is created.
    # If an instance already exists, it returns that instance instead of creating a new one.
    #--------------------------------------------------------------------------
    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:

            # If the instance does not exist yet, create it and store it in the class variable
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance

        #----------------------------------------------------------------------
        # Return the existing instance
        #----------------------------------------------------------------------
        return cls._instances[cls]

#------------------------------------------------------------------------------
print(f'Siqo singleton meta class ver {_VER}')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
