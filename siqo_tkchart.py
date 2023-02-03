#==============================================================================
# Siqo tkChart library
#------------------------------------------------------------------------------
import sys
sys.path.append('..\siqo_lib')

from   siqo_journal        import SiqoJournal

import tkinter                as tk
from   tkinter                import (ttk, font, PanedWindow)

from   matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from   mpl_toolkits                      import mplot3d

import cmath             as cm
import numpy             as np
import matplotlib.pyplot as plt


#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_WIN            = '1300x740'
_DPI            = 100

_FIG_W          = 0.8    # Figure width
_FIG_H          = 1.0    # Figure height

#==============================================================================
# package's variables
#------------------------------------------------------------------------------

#==============================================================================
# Class SiqoChart
#------------------------------------------------------------------------------
class SiqoChart(FigureCanvasTkAgg):
    
    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, journal, name, container, **kwargs):
        "Call constructor of SiqoChart and initialise it"

        self.journal = journal
        self.name    = name
        self.journal.I(f'{self.name}.init:')
        self.w = 400
        self.h = 200
        
        self.fig = plt.figure(figsize=(self.w*_FIG_W/100, self.h*_FIG_H/100), dpi=_DPI)

        #----------------------------------------------------------------------
        # Initialise original tkInter.Tk
        #----------------------------------------------------------------------
        super().__init__(self.fig, master=container)

        self.navBar = NavigationToolbar2Tk(self, container)

        self.get_tk_widget().place(x=self.w*0.0, y=self.h*0.0)
        

        #----------------------------------------------------------------------
        # Internal objects
        #----------------------------------------------------------------------
        self.clear()
        
        self.show()


        #----------------------------------------------------------------------
        # Bind events on this TreeView to respective methods
        #----------------------------------------------------------------------
        self.fig.canvas.callbacks.connect('button_press_event', self.on_click)

        self.journal.O()

    #--------------------------------------------------------------------------
    def clear(self):
        
        pass
    
    #==========================================================================
    # Show the chart
    #--------------------------------------------------------------------------
    def show(self):
        
        
        
        pass
#        self.draw()
        
        
        
    #--------------------------------------------------------------------------
    def on_click(self, event):
        "Print information about mouse-given position"
        
        if event.inaxes is not None:
            
            ax = event.inaxes.get_title()
            x = float(event.xdata)
            y = float(event.ydata)
            
            print(f'x={x},  y={y}, ax={ax}')

            
        else:
            print('Clicked ouside axes bounds but inside plot window')
    
        
        

#==============================================================================
#   Inicializacia kniznice
#------------------------------------------------------------------------------
print('SIQO tkChart library ver 1.00')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------