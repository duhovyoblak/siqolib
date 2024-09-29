#==============================================================================
# Siqo tkInter library
#------------------------------------------------------------------------------
import tkinter                as tk
from   tkinter                import (ttk, font)

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_ASC        = 'ᐃ'        # Sorted ascending sign
_DSC        = '▼'        # Sorted descending sign
_FLT        = '‼'        # Flag for filtered column


_WIDTH_MIN  =   6        # Min width of column in default setting in chars
_WIDTH_MAX  =  50        # Max width of column in default setting in chars
_WIDTH_SUM  = 220        # Default sum of max widths of all columns

#==============================================================================
# package's variables
#------------------------------------------------------------------------------

#==============================================================================
# Class SiqoTreeView
#------------------------------------------------------------------------------
class SiqoTreeView(ttk.Treeview):
    
    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, journal, name, frame, **kwargs):
        "Call constructor of SiqoTree and initialise it"

        self.journal = journal
        self.name    = name
        self.journal.I(f'{self.name}.init:')

        #----------------------------------------------------------------------
        # Initialise original tkInter.TreeView
        #----------------------------------------------------------------------
        if 'cursor' in kwargs.keys(): cur = kwargs['cursor']
        else                        : cur = None
        
        super().__init__(frame, cursor=cur)

        self.heading('#0', text=self.name, anchor='w')

        # scrollbar Y
        yscrl = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.yview)
        self.configure(yscroll=yscrl.set)
        yscrl.pack(fill=tk.Y, anchor=tk.E, expand=True)

        # scrollbar X
        xscrl = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.xview)
        self.configure(xscroll=xscrl.set)
        xscrl.pack(fill=tk.X, anchor=tk.S)

        #----------------------------------------------------------------------
        # Internal objects
        #----------------------------------------------------------------------
        self.where    = None   # Last clicked object
        self.selected = {}     # Last selection

        self.clear()

        #----------------------------------------------------------------------
        # Create right-click menu
        #----------------------------------------------------------------------
        self.rcm = tk.Menu(self, tearoff = 0)
        self.rcm.add_command(label ="Filter this", command=lambda sel=self.selected: self.addFilter(sel))

        #----------------------------------------------------------------------
        # Bind events on this TreeView to respective methods
        #----------------------------------------------------------------------
        self.bind('<ButtonRelease-1>', self.setSelect)
        self.bind('<Button-3>',        self.rcmMenu  )

        self.journal.O()

    #--------------------------------------------------------------------------
    def clear(self):
        "Clears all content of the TreeView"
        
        self.journal.I(f'{self.name}.clear:')
        
        for i in self.get_children():
            self.delete(i)
            
        #----------------------------------------------------------------------
        # Clear objects
        #----------------------------------------------------------------------
        self.where = None
        
        self.selected['colNum' ] = -1
        self.selected['col'    ] = ''
        self.selected['val'    ] = ''
        self.selected['row'    ] = {}
        self.selected['head'   ] = ''
        
        self.journal.O()
            
    #--------------------------------------------------------------------------
    def clickWhere(self, event):
        "Resolve object of the TreeView which was clicked on"
        
        self.journal.I(f'{self.name}.clickWhere:')
        
        row   = ''
        val   = ''
        col   = ''
        colid = -1
        head  = '' 
        
        #----------------------------------------------------------------------
        # Identify afected row
        #----------------------------------------------------------------------
        iid = self.identify_row(event.y)
      
        #----------------------------------------------------------------------
        # Set focus here if no rows was clicked on
        #----------------------------------------------------------------------
        if iid and len(self.selection()) == 0:
            self.focus(iid)
            self.selection_set(iid)
          
        #----------------------------------------------------------------------
        # If clicked on header
        #----------------------------------------------------------------------
        if self.identify_region(event.x,event.y) == 'heading':
            head  = self.identify_column(event.x)
            colid = int(self.identify_column(event.x)[1:]) - 1
            val   = self.heading(head, 'text')
            
        #----------------------------------------------------------------------
        # If clicked on row
        #----------------------------------------------------------------------
        elif self.identify_region(event.x,event.y) == 'cell':
            curItem = self.focus()
            val   = self.item(curItem, 'values')
            colid = int(self.identify_column(event.x)[1:]) - 1
            
            row   = val
            val   = val[colid]
            hd    = self.identify_column(event.x)
            col   = self.heading(hd, 'text').replace(' '+_FLT,'')
            
        #----------------------------------------------------------------------
        # Set ouput
        #----------------------------------------------------------------------
        self.where = {'head':head, 'row':row, 'col':col, 'val':val, 'colNum':colid}
        
        self.journal.M(f'{self.name}.clickWhere: {self.where}')
        self.journal.O()
        
        return self.where
       
    #--------------------------------------------------------------------------
    def setSelect(self, event):
        
        self.journal.I(f'{self.name}.setSelect:')
        
        where = self.clickWhere(event)
        
        #----------------------------------------------------------------------
        # If there is a valid click position
        #----------------------------------------------------------------------
        if where['colNum'] > -1:
            self.selected['colNum' ] = where['colNum']
            self.selected['col'    ] = where['col' ]
            self.selected['val'    ] = where['val' ]
            self.selected['row'    ] = where['row' ]
            self.selected['head'   ] = where['head']

        else:
            self.selected['colNum' ] = -1
            self.selected['col'    ] = ''
            self.selected['val'    ] = ''
            self.selected['row'    ] = {}
            self.selected['head'   ] = ''

        self.event_generate('<<SiqoTreeView-setSelect>>')
        
        self.journal.M(f'{self.name}.setSelect: {self.selected}')
        self.journal.O()
        
    #--------------------------------------------------------------------------
    def rcmMenu(self, event):
        
        if self.selected['colNum'] > -1:
 
            try    : self.rcm.tk_popup(event.x_root, event.y_root)
            finally: self.rcm.grab_release()
            
    #--------------------------------------------------------------------------
    def expand(self, parent=''):
        "Expands all branches for Treelike view"
        
        self.journal.I(f'{self.name}.expand:')
        
        self.item(parent, open=True)
        
        # Recursive expanding of children
        for child in self.get_children(parent):
            self.expand(child)
            
        self.journal.O()
        
    #==========================================================================
    # TreeView as a Table
    #
    # dat   : data to show as list of rows. Row [0] is for headers
    #         [[]]
    #
    # lights: Highlightning rules for rows
    #         [{'colId':int, 'test':str, 'val':str, 'tags':[]}]
    #         test can be one of {'starts', 'not starts', 'cont'}
    #
    #--------------------------------------------------------------------------
    def datToTab(self, dat, lights=[]):
        "Populates TreeView in form of Table. Returns message"
        
        self.journal.I(f'{self.name}.datToTab:')
        
        #----------------------------------------------------------------------
        # Check incoming data
        #----------------------------------------------------------------------
        if type(dat)!=list or len(dat)==0:
            
            self.journal.M(f'{self.name}.datToTab: Data is empty or in wrong structure', True)
            self.journal.O()
            return f"Data for TreeView '{self.name}' is empty or in wrong structure"
        
        #----------------------------------------------------------------------
        # Set headers from dat[0]
        #----------------------------------------------------------------------
        self["columns"] = dat[0]
        
        #----------------------------------------------------------------------
        # Get max width for each column and set coeff for shrinking
        #----------------------------------------------------------------------
        maxW = [0 for col in dat[0]]
        
        # First, find out actual max width for each column
        for row in dat:
            i = 0
            for col in row:
                if (col is not None): w = len(str(col)) 
                else                : w = 0
                
                if w > maxW[i]: maxW[i] = w
                i += 1

        #----------------------------------------------------------------------
        # Second, cut to WIDTH_MAX if needed                 
        sumW = sum(maxW)
        
        if sumW > _WIDTH_SUM:
            for i in range( len(maxW) ): 
                if maxW[i] > _WIDTH_MAX: maxW[i] = _WIDTH_MAX

        #----------------------------------------------------------------------
        # Third, shrink by coefficient if needed
        sumW = sum(maxW)

        if sumW > _WIDTH_SUM: cW = _WIDTH_SUM / sumW
        else                : cW = 1
        
        self.journal.M(f'{self.name}.datToTab: sumW={sumW}, cW={cW}')
        
        #----------------------------------------------------------------------
        # Define column's properties
        #----------------------------------------------------------------------
        i = 0
        for col in self["columns"]: 
            
            pixW = (9*maxW[i]) + 0  # Real width in pixels
            
            self.column(col, width=int(cW*pixW), minwidth=9*_WIDTH_MIN)
            i += 1
        
        #----------------------------------------------------------------------
        # Define column's headers
        #----------------------------------------------------------------------
        for col in self["columns"]:
            self.heading(col, text=col, anchor='w', command=lambda _col = col: self.sortColumn(_col, False))
        
        #----------------------------------------------------------------------
        # Populate rows from dat
        #----------------------------------------------------------------------
        odd = True
        for row in dat[1:]:
            
            colored = False
            #------------------------------------------------------------------
            # Highlighted rows
            #------------------------------------------------------------------
            for high in lights:
                
                #--------------------------------------------------------------
                if   high['test'] == 'starts':
                    
                    if row[ high['colId'] ].startswith( high['val']  ): 
                         self.insert('', tk.END, values=row, tags=high['tags'])
                         colored = True
                
                #--------------------------------------------------------------
                elif high['test'] == 'not starts':

                    if not row[ high['colId'] ].startswith( high['val']  ): 
                         self.insert('', tk.END, values=row, tags=high['tags'])
                         colored = True

                #--------------------------------------------------------------
                elif high['test'] == 'cont':

                    if row[ high['colId'] ].count( high['val'] ) > 0: 
                         self.insert('', tk.END, values=row, tags=high['tags'])
                         colored = True

            #------------------------------------------------------------------
            # Non-Highlighted rows
            #------------------------------------------------------------------
            if not colored:
                
                #--------------------------------------------------------------
                # Odd's row
                #--------------------------------------------------------------
                if odd:
                    
                    self.insert('', tk.END, values=row, tags=['TableCell'])
                    odd = False
                
                #--------------------------------------------------------------
                # Pair's row    
                #--------------------------------------------------------------
                else:
                    self.insert('', tk.END, values=row, tags=['TableCell', 'BlueRow'])
                    odd = True

        #----------------------------------------------------------------------
        # Styling
        #----------------------------------------------------------------------
        self['show'] = 'headings'
        self.tag_configure('TableCell', font=font.nametofont('TkFixedFont'))
        
        self.tag_configure('RedRow',    background='#ffcccc')   # red
        self.tag_configure('YellowRow', background='#ffffcc')   # yellow
        self.tag_configure('GreenRow',  background='#ccffcc')   # green 
        self.tag_configure('BlueRow',   background='#e6f3ff')   # blue
        
        self.journal.O()
        return 'OK'
        
    #==========================================================================
    # Filtering the Table
    #--------------------------------------------------------------------------
    def addFilter(self, sel):
        "Set filter based on "
        
        self.journal.I(f"{self.name}.addFilter: sel='{sel}'")
        #????
        
        if sel['colNum'] > -1:
            self.filterColumn(colNum=sel['colNum'], col=sel['col'], val=sel['val'])
        
        self.journal.O()
        
    #--------------------------------------------------------------------------
    def filterColumn(self, colNum, col, val):
        "Filter rows based on respective value"
        
        self.journal.I(f"{self.name}.filterColumn: colNum='{colNum}', col='{col}', val='{val}'")
        
        #----------------------------------------------------------------------
        # For all rows
        #----------------------------------------------------------------------
        for child in self.get_children():
            
            rowItem = self.item(child)
            
            # Test if row matches filters
            if str(rowItem["values"][colNum]) != val: self.delete(child)
            
        #----------------------------------------------------------------------
        # Ad flag to column's heading 
        #----------------------------------------------------------------------
        self.heading(col, text=f'{col} {_FLT}')
        self.journal.O()
            
    #==========================================================================
    # Sorting the column in the Table
    #--------------------------------------------------------------------------
    def sortColumn(self, col, reverse=False):

        self.journal.I(f"{self.name}.sortColumn: col='{col}', reverse={reverse}")
        
        # Ziskam zoznam zotriedenych hodnot        
        lst = [(self.set(k, col), k) for k in self.get_children('')]
        lst.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(lst):
            self.move(k, '', index)

        # Resetnem nazvy stlpcov na originalne nazvy
        for c in  self["columns"]: self.heading(c, text=c)
            
        # K nazvu sortovaneho stlpca doplnim zank ASC/DSC
        if reverse: text = f'{col} {_DSC}'
        else      : text = f'{col} {_ASC}'
        
        self.heading(col, text=text, command=lambda _col=col: self.sortColumn(_col, not reverse))

        self.journal.O()

    #==========================================================================
    # TreeView as a Tree
    #
    # dat   : data to show as list of rows. Row [0] is for headers
    #         [{}]
    #
    #
    #--------------------------------------------------------------------------
    def datToTree(self, dat, rootId=None, maxId=0, indent=12):
        
#        self.journal.I(f"{self.name}.datToTree: ")
        
        if rootId is None: self.tag_configure('TreeCell', font=font.nametofont('TkFixedFont'))
        localPos = 0
        
        if dat is None or len(dat)==0: return maxId
        
        #----------------------------------------------------------------------
        # Prejdem vsetky polozky dictionary
        #----------------------------------------------------------------------
        for key, val in dat.items():
            
            maxId += 1

            #------------------------------------------------------------------
            # Ak je item dictionary, potom rekurzia
            if type(val)==dict: 
                
                self.insert('', tk.END, text=f'[{key}]', iid=maxId, open=True, tags=['TreeCell'])
                if rootId is not None: self.move(maxId, rootId, localPos)
                
                maxId  = self.datToTree(val, maxId, maxId, indent)
            
            #------------------------------------------------------------------
            # Ak je item list
            elif type(val)==list: 
                
                self.insert('', tk.END, text=f'[{key}]', iid=maxId, open=True, tags=['TreeCell'])
                listRoot = maxId
                if rootId is not None: self.move(listRoot, rootId, localPos)

                # Vlozim list po riadkoch
                listPos = 0
                for row in val:
                    
                    maxId   += 1
                    self.insert('', tk.END, text=f'{str(row)}', iid=maxId, open=True, tags=['TreeCell'])
                    self.move(maxId, listRoot, listPos)
                    listPos += 1
            
            #------------------------------------------------------------------
            # Trivialna polozka
            else: 
                key = str(key).ljust(indent)
                
                # Vlozim do stromu
                self.insert('', tk.END, text=f'{key}: {str(val)}', iid=maxId, open=True, tags=['TreeCell'])
                
                # Ak som v podstrome, presuniem pod rootId
                if rootId is not None: self.move(maxId, rootId, localPos)
                
            #------------------------------------------------------------------
            # Zvysenie lokalnej pozicie
            localPos += 1
                
        return maxId
        
    #--------------------------------------------------------------------------

#==============================================================================
# Class SiqoLogin
#------------------------------------------------------------------------------
class SiqoLogin(tk.Toplevel):
    
    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, journal, name, **kwargs):
        "Call constructor of SiqoLogin and initialise it"

        self.journal = journal
        self.name    = name
        self.journal.I(f"{self.name}.init:")
        
        self.str_user = tk.StringVar(value = '')
        self.str_pasw = tk.StringVar(value = '')

        #----------------------------------------------------------------------
        # Inicializacia okna
        #----------------------------------------------------------------------
        super().__init__()

        #----------------------------------------------------------------------
        # Priprava premennych
        #----------------------------------------------------------------------
        lpix = 500  # self.winfo_x()
        hpix = 300  # self.winfo_y()
     
        if 'user' in kwargs.keys(): self.str_user.set(kwargs['user'])
        
        #----------------------------------------------------------------------
        # Create login window
        #----------------------------------------------------------------------
        self.geometry("240x200+%d+%d" % (lpix + 300, hpix + 100))

        # window title
        title_label = tk.Label(self, text=f'Login to {self.name}', bg= "#2c2c2c", fg="white")
        title_label.pack(fill='x', expand=True, padx=10)

        self.focus_force()
        self.grab_set()

        #----------------------------------------------------------------------
        # Nacitanie credentials
        #----------------------------------------------------------------------
        # user
        usr_label = ttk.Label(self, text="User:")
        usr_label.pack(fill='x', expand=True, padx=10)

        usr_entry = ttk.Entry(self, textvariable=self.str_user)
        usr_entry.pack(fill='x', expand=True, padx=10)
        usr_entry.focus()

        # password
        pass_label = ttk.Label(self, text="Password:")
        pass_label.pack(fill='x', expand=True, padx=10)

        pass_entry = ttk.Entry(self, textvariable=self.str_pasw, show="*")
        pass_entry.pack(fill='x', expand=True, padx=10)

        # login button
        login_button = ttk.Button(self, text="Login", command=self.login )
        login_button.pack(fill='x', expand=True, padx=10, pady=10)
        
        self.bind('<Return>', self.login      )
        self.bind('<Escape>', self.login_close)     
        
        self.journal.O()
        
    #--------------------------------------------------------------------------
    def getUser(self):
        "Returns edited user name"
        
        return self.str_user.get()
        
    #--------------------------------------------------------------------------
    def getPassword(self):
        "Returns and destroy password"
      
        pasw = self.str_pasw.get()
        self.str_pasw.set('')
        
        return pasw
    
    #--------------------------------------------------------------------------
    def login_close(self, event):
        "Destroy login window"
        
        self.winLogin.destroy()    
          
    #--------------------------------------------------------------------------
    def login(self, event=None):
        
        self.journal.I(f"{self.name}.login:")

        self.event_generate('<<SiqoLogin>>')
        self.destroy()

        self.journal.O()
        
#==============================================================================
#   Inicializacia kniznice
#------------------------------------------------------------------------------
print('SIQO tkInter library ver 1.02')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------