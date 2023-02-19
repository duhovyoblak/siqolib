#==============================================================================
# Siqo tkChart library
#------------------------------------------------------------------------------
import sys
sys.path.append('..\siqo_lib')

import tkinter                as tk
from   tkinter                import (ttk, font, PanedWindow)
from   tkinter.messagebox     import showinfo

from   matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from   mpl_toolkits                      import mplot3d

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
    def __init__(self, journal, name, container, dat, **kwargs):
        "Call constructor of SiqoChart and initialise it"

        journal.I(f'{name}.init:')

        self.journal = journal
        self.name    = name
        self.dat     = dat
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
        # Internal objects
        #----------------------------------------------------------------------
        self.type     = '2D'     # Actual type of the chart
        self.CPs      = []       # List of values (cP)
        self.actPoint = None     # Actual working point

        
        self.keyX     = ''       # Dimension name for coordinate X
        self.X        = None     # np array for coordinate X
        self.keyY     = ''       # Dimension name for coordinate Y
        self.Y        = None     # np array for coordinate Y
        self.C        = None     # np array for value color
        self.U        = None     # np array for quiver re value
        self.V        = None     # np array for quiver im value

        self.clear()

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
        frmBtn.columnconfigure(4, weight=1)
        
        frmBtn.rowconfigure(0, weight=1)
        frmBtn.rowconfigure(1, weight=1)
        
        #----------------------------------------------------------------------
        # Value
        #----------------------------------------------------------------------
        lblVal = ttk.Label(frmBtn, text="Value to show:")
        lblVal.grid(column=0, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.cbVal = ttk.Combobox(frmBtn, textvariable=self.strVal, width=5)
        self.cbVal['values'] = ['re', 'im', 'abs']
        self.cbVal['state' ] = 'readonly'
        self.cbVal.bind('<<ComboboxSelected>>', self.show)
        self.cbVal.grid(column=0, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)
        
        #----------------------------------------------------------------------
        # X axis
        #----------------------------------------------------------------------
        lblX = ttk.Label(frmBtn, text="Dim for X axis:")
        lblX.grid(column=1, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.cbX = ttk.Combobox(frmBtn, textvariable=self.strX, width=5)
        self.cbX['values'] = ['0', '1', '2', '3']
        self.cbX['state' ] = 'readonly'
        self.cbX.bind('<<ComboboxSelected>>', self.dataChanged)
        self.cbX.grid(column=1, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)
        
        self.cbLogX = ttk.Checkbutton(frmBtn, text='LogX', command=self.show)
        self.cbLogX.grid(column=1, row=1, pady=_PADY)
        
        #----------------------------------------------------------------------
        # Y axis
        #----------------------------------------------------------------------
        lblY = ttk.Label(frmBtn, text="Dim for Y axis:")
        lblY.grid(column=2, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.cbY = ttk.Combobox(frmBtn, textvariable=self.strY, width=5)
        self.cbY['values'] = ['1', '2', '3']
        self.cbY['state' ] = 'readonly'
        self.cbY.bind('<<ComboboxSelected>>', self.dataChanged)
        self.cbY.grid(column=2, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)
        
        self.cbLogY = ttk.Checkbutton(frmBtn, text='LogY', command=self.show)
        self.cbLogY.grid(column=2, row=1, pady=_PADY)

        #----------------------------------------------------------------------
        # Create a figure with the navigator bar and bind to mouse events
        #----------------------------------------------------------------------
        self.figure = plt.figure(figsize=(self.w*_FIG_W/100, self.h*_FIG_H/100), dpi=_DPI)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        
        self.canvas.callbacks.connect('button_press_event', self.on_click)
        
        NavigationToolbar2Tk(self.canvas, self)
        
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        #----------------------------------------------------------------------
        # Vytvorim Menu pre click on Point
        #----------------------------------------------------------------------
        self.pointMenu = tk.Menu(self, tearoff = 0)
        self.pointMenu.add_command(label ="Set to (0,0)", command=lambda c=complex(0,0): self.setPoint(c))
        self.pointMenu.add_command(label ="Set to (1,0)", command=lambda c=complex(1,0): self.setPoint(c))
        self.pointMenu.add_command(label ="Set to (0,1)", command=lambda c=complex(0,1): self.setPoint(c))
        self.pointMenu.add_command(label ="Set to (1,1)", command=lambda c=complex(1,1): self.setPoint(c))
        
        #----------------------------------------------------------------------
        # Initialisation
        #----------------------------------------------------------------------
        self.dataChanged()

        self.journal.O()

    #--------------------------------------------------------------------------
    def is1D(self):

        # Only axis X can be void
        axX = int(self.strX.get())
        
        if axX==0: return True
        else     : return False
        
#--------------------------------------------------------------------------
    def dataChanged(self, event=None):
        
        #----------------------------------------------------------------------
        # Read actual settings
        #----------------------------------------------------------------------
        axX = int(self.strX.get())
        axY = int(self.strY.get())
        
        self.journal.I(f'{self.name}.dataChanged: axX={axX}, axY={axY}')

        #----------------------------------------------------------------------
        # Default filter with placeholders for all dimensions
        #----------------------------------------------------------------------
#        cut = [0 for i in range(self.dat.getDimMax())]
        cut = [0,0]
        
        #----------------------------------------------------------------------
        # Set actual filter and get data
        #----------------------------------------------------------------------
        if self.is1D(): cut = [-1]
        else:
            cut[axX-1] = -1
            cut[axY-1] = -1
        
        self.journal.M(f'{self.name}.dataChanged: cut={cut}')

        dat = self.dat.getData(cut=cut)

        #----------------------------------------------------------------------
        # Assign coordinate arrays
        #----------------------------------------------------------------------
        self.keyY = dat[axY-1]['key']
        self.Y    = dat[axY-1]['arr']
        self.journal.M(f'{self.name}.dataChanged: keyY={self.keyY}')
        
        if self.is1D():
            self.keyX = 'No dimension'
            self.X    = np.zeros(len(self.Y))
            
        else:
            self.keyX = dat[axX-1]['key']
            self.X    = dat[axX-1]['arr']

        self.journal.M(f'{self.name}.dataChanged: keyX={self.keyX}')
        
        #----------------------------------------------------------------------
        # Remember values (list of cP) for this dataset
        #----------------------------------------------------------------------
        self.CPs = dat[-1]['arr']
        
        self.journal.O()
        self.show()
        
    #--------------------------------------------------------------------------
    def clear(self):
        
        pass
    
    #--------------------------------------------------------------------------
    def setData(self, dat):
        "Clears data and set new data"
        
        self.dat = dat
        
    #--------------------------------------------------------------------------
    def setPoint(self, c):
        
        self.journal.M(f'{self.name}.setPoint: {self.actPoint} = {c}')
        
        self.actPoint.setVal(c)
        self.dataChanged()
        
    #==========================================================================
    # Show the chart
    #--------------------------------------------------------------------------
    def show(self, event=None):

        self.journal.I(f'{self.name}.show:')
        
        #----------------------------------------------------------------------
        # Assign value arrays
        #----------------------------------------------------------------------
        val = self.strVal.get()
        arrC = []
        
        # Value is in the last position in the list
        for cP in self.CPs:
            
            if   val == 're'  : arrC.append( cP.real() )
            elif val == 'im'  : arrC.append( cP.imag() )
            elif val == 'abs' : arrC.append( cP.abs()  )
            
        self.C = np.array(arrC)
        
        #----------------------------------------------------------------------
        # Prepre the chart
        #----------------------------------------------------------------------
        self.figure.clear() 
        self.chart = self.figure.add_subplot()

        self.chart.set_title(val, fontsize=14)
        self.chart.grid(False)
        self.chart.set_facecolor('white')
        self.chart.set_xlabel(self.keyX)
        self.chart.set_ylabel(self.keyY)
        
        #----------------------------------------------------------------------
        # Log axis X, Y
        #----------------------------------------------------------------------
        if 'selected' in self.cbLogX.state(): self.chart.set_xscale('log')
        if 'selected' in self.cbLogY.state(): self.chart.set_yscale('log')
        
        #----------------------------------------------------------------------
        # Show the chart
        #----------------------------------------------------------------------
#        sctrObj = self.chart.scatter( x=self.X, y=self.Y, c=self.C )
        
        sctrObj = self.chart.scatter( x=self.X, y=self.Y, c=self.C, marker="s", cmap='RdYlBu_r')
#        sctrObj = self.chart.scatter( x=self.X, y=self.Y, c=self.C, marker="s", lw=0, s=(72./self.figure.dpi)**2, cmap='RdYlBu_r')
#        self.figure.colorbar(sctrObj, ax=self.chart)
            

        # Vykreslenie noveho grafu
        self.figure.tight_layout()
        self.update()
        self.canvas.draw()
        
        self.journal.O()
        
    #--------------------------------------------------------------------------
    def on_click(self, event):
        "Print information about mouse-given position"
        
        self.journal.I(f'{self.name}.on_click:')

        if event.inaxes is not None:
            
            ax  = event.inaxes.get_title()
            btn = event.button
            #           btn = event.num
            x = round(float(event.xdata), 3)
            y = round(float(event.ydata), 3)
            
            if self.is1D(): coord = [y   ]
            else          : coord = [y, x]
            
            self.actPoint = self.dat.getPointByCoord(coord)
            
            #------------------------------------------------------------------
            # Left button
            #------------------------------------------------------------------
            if btn == 1: #MouseButton.LEFT:
               tit = f'Nearest point to [{round(y,2)}, {round(x,2)}]'
               mes = str(self.actPoint)
               showinfo(title=tit, message=mes)
            
            #------------------------------------------------------------------
            # Right button - edit value menu
            #------------------------------------------------------------------
            elif btn == 3: #MouseButton.RIGHT:
                
                self.journal.M(f'{self.name}.on_click: right click for {self.actPoint}')
                
                try    : self.pointMenu.tk_popup(event.x, event.y)
                finally: self.pointMenu.grab_release()
            
            #------------------------------------------------------------------
            
        else:
            self.actPoint = None
            print('Clicked ouside axes bounds but inside plot window')
        
        self.journal.O()

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