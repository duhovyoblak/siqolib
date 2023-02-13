#==============================================================================
# Siqo tkChart library
#------------------------------------------------------------------------------
import sys
sys.path.append('..\siqo_lib')

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

        journal.I(f'{name}.init:')
        
        self.journal = journal
        self.name    = name
        self.dat     = None
        self.typ     = 'quiver'  # Type of axis ['quiver','2D','3D']

        #----------------------------------------------------------------------
        # Initialise original FigureCanvasTkAgg
        #----------------------------------------------------------------------
        self.w       = container.winfo_width()
        self.h       = container.winfo_height()
        self.fig     = plt.figure(figsize=(self.w*_FIG_W/100, self.h*_FIG_H/100), dpi=_DPI)

        super().__init__(self.fig, master=container)

        self.get_tk_widget().place(x=0, y=0)
        self.fig.canvas.callbacks.connect('button_press_event', self.on_click)
        
        #----------------------------------------------------------------------
        # Initialise navigation bar for a figure
        #----------------------------------------------------------------------
        self.navBar = NavigationToolbar2Tk(self, container)
        
        #----------------------------------------------------------------------
        # Internal objects
        #----------------------------------------------------------------------
        self.clear()
        self.show()


        self.journal.O()

    #--------------------------------------------------------------------------
    def clear(self):
        "Clear and destroy all data"
        
        pass
    
    #==========================================================================
    # API
    #--------------------------------------------------------------------------
    def setData(self, dat):
        "Clears data and set new data"
        
        self.clear()
        self.dat = dat

    #--------------------------------------------------------------------------
    def setType(self, typ):
        "Set type of the axis"
        
        self.journal.I(f'{self.name}.setType: type = {typ}')

        self.typ = typ

        self.journal.O()
        
    #==========================================================================
    # Show the chart
    #--------------------------------------------------------------------------
    def show(self):
        "Shows chart of the data for respective axis type"
        
        self.journal.I(f'{self.name}.show: type = {self.typ}')
        
        
        
        self.journal.O()
        
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