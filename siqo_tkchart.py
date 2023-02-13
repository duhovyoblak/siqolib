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

        journal.I(f'{name}.init:')

        self.journal = journal
        self.name    = name
        self.dat     = None
        self.w       = 600
        self.h       = 400
        
        self.fig = plt.figure(figsize=(self.w*_FIG_W/100, self.h*_FIG_H/100), dpi=_DPI)

        #----------------------------------------------------------------------
        # Initialise original tkInter.Tk
        #----------------------------------------------------------------------
        super().__init__(self.fig, master=container)

        self.navBar = NavigationToolbar2Tk(self, container)
        self.get_tk_widget().place(x=self.w*0.0, y=self.h*0.0)
        

        self.chart = self.fig.add_subplot()
        self.chart.set_title("Left", fontsize=14)
        self.chart.grid(False)
        self.chart.set_facecolor('yellow')
        self.chart.set_xlabel( 'X0' )
        self.chart.set_ylabel( 'X1')



        #----------------------------------------------------------------------
        # Internal objects
        #----------------------------------------------------------------------
        self.clear()
        

        #----------------------------------------------------------------------
        # Bind events on this TreeView to respective methods
        #----------------------------------------------------------------------
        self.fig.canvas.callbacks.connect('button_press_event', self.on_click)

        self.journal.O()

    #--------------------------------------------------------------------------
    def clear(self):
        
        pass
    
    #--------------------------------------------------------------------------
    def setData(self, dat):
        "Clears data and set new data"
        
        self.dat = dat
        
    #==========================================================================
    # Show the chart
    #--------------------------------------------------------------------------
    def show(self):

        self.journal.I(f'{self.name}.show:')
        
        dat = self.dat.getData()
        X = dat['x1']
        Y = dat['x2']
        C = dat['re']

        print(X)
        print(Y)
        print(C)
        
        sctrObj = self.chart.scatter( x=X, y=Y, c=C )
#        sctrObj = self.chart.scatter( x=dat['x1'], y=dat['x2'], c=dat['re'], marker="s", lw=0, s=(72./self.fig.dpi)**2, cmap='RdYlBu_r')
        self.fig.colorbar(sctrObj, ax=self.chart)
            

        # Vykreslenie noveho grafu
        self.fig.tight_layout()
#        self.update()
        self.draw()
        
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
    
        
    #==========================================================================
    # Tools for figure setting
    #--------------------------------------------------------------------------
    def getDataLabel(self, key):
        "Return data label for given data's key"
        
        return "${}$ [{}{}]".format(key, self.meta[key]['unit'], 
                                         self.meta[key]['dim' ])
    
    #--------------------------------------------------------------------------
    def getValByGrid(self, gv, key):
        "Return rescaled value for given grid's value and data's key"
        
        gl = self.meta['g'+key]['max'] - self.meta['g'+key]['min']
        vl = self.meta[    key]['max'] - self.meta[    key]['min']
        
        return (gv/gl) * vl * self.meta[key]['coeff']
    
    #--------------------------------------------------------------------------
    def getObjScatter(self):
        "Returns plotable data for Object value"
        
        self.journal.M( f"{self.name}.getObjScatter" )

#        return lib.squareData(baseObj=self.obj, vec=self.obj.prtLst)
#        return lib.spiralData(baseObj=self.obj, vec=self.obj.prtLst)
        
        
        

#==============================================================================
#   Inicializacia kniznice
#------------------------------------------------------------------------------
print('SIQO tkChart library ver 1.00')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------