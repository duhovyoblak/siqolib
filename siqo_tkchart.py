#==============================================================================
# Siqo tkChart library
#------------------------------------------------------------------------------
import sys
sys.path.append('..\siqo_lib')

from   siqo_journal        import SiqoJournal

import tkinter                as tk
from   tkinter                import (ttk, font, PanedWindow)
from tkinter.messagebox import showinfo

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

_PADX           = 5
_PADY           = 5

#==============================================================================
# package's variables
#------------------------------------------------------------------------------

#==============================================================================
# Class SiqoChart
#------------------------------------------------------------------------------
class SiqoChart(ttk.Frame):
    
    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, journal, name, container, **kwargs):
        "Call constructor of SiqoChart and initialise it"

        journal.I(f'{name}.init:')

        self.journal = journal
        self.name    = name
        self.dat     = None
        self.w       = 1200
        self.h       =  800
        
        self.strVal = tk.StringVar()
        self.strX   = tk.StringVar()
        self.strY   = tk.StringVar()
        
        if 'val' in kwargs.keys(): self.strVal.set(kwargs['val'])
        else                     : self.strVal.set('re')

        if 'axX' in kwargs.keys(): self.strX.set(kwargs['axX'])
        else                     : self.strX.set('0')

        if 'axY' in kwargs.keys(): self.strY.set(kwargs['axY'])
        else                     : self.strY.set('1')

        #----------------------------------------------------------------------
        # Initialise original tkInter.Tk
        #----------------------------------------------------------------------
        super().__init__(container)

        #----------------------------------------------------------------------
        # Create button bar
        #----------------------------------------------------------------------
        frmBtn = ttk.Frame(self)
        frmBtn.pack(fill=tk.X, expand=True, side=tk.TOP, anchor=tk.N)
 
        frmBtn.columnconfigure(0, weight=1)
        frmBtn.columnconfigure(1, weight=1)
        frmBtn.columnconfigure(2, weight=1)
        frmBtn.columnconfigure(3, weight=1)
        
        frmBtn.rowconfigure(0, weight=1)
        frmBtn.rowconfigure(1, weight=1)
        
        #----------------------------------------------------------------------
        # Value
        #----------------------------------------------------------------------
        lblVal = ttk.Label(frmBtn, text="Value to show:")
        lblVal.grid(column=0, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.cbVal = ttk.Combobox(frmBtn, textvariable=self.strVal)
        self.cbVal['values'] = ['re', 'im', 'abs']
        self.cbVal['state' ] = 'readonly'
        self.cbVal.bind('<<ComboboxSelected>>', self.chartChanged)
        self.cbVal.grid(column=0, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)
        
        #----------------------------------------------------------------------
        # X axis
        #----------------------------------------------------------------------
        lblX = ttk.Label(frmBtn, text="Dim for X axis:")
        lblX.grid(column=1, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.cbX = ttk.Combobox(frmBtn, textvariable=self.strX)
        self.cbX['values'] = ['0', '1', '2', '3']
        self.cbX['state' ] = 'readonly'
        self.cbX.bind('<<ComboboxSelected>>', self.chartChanged)
        self.cbX.grid(column=1, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)
        
        #----------------------------------------------------------------------
        # Y axis
        #----------------------------------------------------------------------
        lblY = ttk.Label(frmBtn, text="Dim for Y axis:")
        lblY.grid(column=2, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.cbY = ttk.Combobox(frmBtn, textvariable=self.strY)
        self.cbY['values'] = ['0', '1', '2', '3']
        self.cbY['state' ] = 'readonly'
        self.cbY.bind('<<ComboboxSelected>>', self.chartChanged)
        self.cbY.grid(column=2, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)
        
        #----------------------------------------------------------------------
        # Create a figure with the navigator bar and bind to mouse events
        #----------------------------------------------------------------------
        self.figure = plt.figure(figsize=(self.w*_FIG_W/100, self.h*_FIG_H/100), dpi=_DPI)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.callbacks.connect('button_press_event', self.on_click)
        
        NavigationToolbar2Tk(self.canvas, self)
        
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
       
        #----------------------------------------------------------------------
        # Internal objects
        #----------------------------------------------------------------------
        self.clear()
        
        self.journal.O()

    #--------------------------------------------------------------------------
    def chartChanged(self, event):
        
        self.show()
        
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
        
        #----------------------------------------------------------------------
        # Set filter and get data
        #----------------------------------------------------------------------
        axX = int(self.strX.get())
        axY = int(self.strY.get())
        val =     self.strVal.get()
        
        # Default filter with placeholders for all dimensions
        cut = [0 for i in range(self.dat.getDimMax())]
        if axX>0: cut[axX-1] = -1
        if axY>0: cut[axY-1] = -1
        
        dat = self.dat.getData(cut=cut)
        X = dat[axX-1]['arr']
        Y = dat[axY-1]['arr']
        
        for arr in dat:
            if arr['key'] == val: C = arr['arr']

        #----------------------------------------------------------------------
        # Show the data
        #----------------------------------------------------------------------
        self.figure.clear() 
        self.chart = self.figure.add_subplot()

        self.chart.set_title(val, fontsize=14)
        self.chart.grid(False)
        self.chart.set_facecolor('white')
        self.chart.set_xlabel(dat[axX-1]['key'])
        self.chart.set_ylabel(dat[axY-1]['key'])
        sctrObj = self.chart.scatter( x=X, y=Y, c=C )
        
#        sctrObj = self.chart.scatter( x=dat['x1'], y=dat['x2'], c=dat['re'], marker="s", lw=0, s=(72./self.fig.dpi)**2, cmap='RdYlBu_r')
#        self.figure.colorbar(sctrObj, ax=self.chart)
            

        # Vykreslenie noveho grafu
        self.figure.tight_layout()
        self.update()
        self.canvas.draw()
        
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