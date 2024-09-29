"""
#==============================================================================
# Siqo tkInter library
#------------------------------------------------------------------------------
2024-08-27 - GHH - SiqoTreeview class prerobena na Frame = Treeview + 2x Scrolbar
"""
import tkinter                as tk
#from   tkinter                import (ttk, font, scrolledtext, messagebox)
from   tkinter                import (ttk, font, messagebox)

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_VER         = '1.21'

_ASC         = 'ᐃ'       # Sorted ascending sign
_DSC         = '▼'       # Sorted descending sign
_FLT         = '‼'       # Flag for filtered column

_WIDTH_MIN   =   6       # Min width of column in default setting in chars
_WIDTH_MAX   =  50       # Max width of column in default setting in chars
_WIDTH_SUM   = 220       # Default sum of max widths of all columns

_EXTRA_AFTER =  20       # If there is more rows, add extra row because y-scrollbar

#==============================================================================
# package's variables
#------------------------------------------------------------------------------

#==============================================================================
# Class SiqoTreeView
#------------------------------------------------------------------------------
class SiqoTreeView(tk.Frame):
    
    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, journal, name, frame, lineNum=True, **kwargs):
        "Call constructor of SiqoTree and initialise it"

        self.journal = journal
        self.name    = name
        self.journal.I(f'{self.name}.init:')
        
        self.lineNum = lineNum   # Shows line numbers in Table view
        self.tabular = False     # keep info if Table or Tree view
        self.lights = []         # Highlightning rules

        #----------------------------------------------------------------------
        # Initialise original tkInter.TreeView
        #----------------------------------------------------------------------
        if 'cursor' in kwargs.keys(): cur = kwargs['cursor']
        else                        : cur = None
        
        super().__init__(frame, cursor=cur)

        # TV = TreeView
        self.TV = ttk.Treeview(self, cursor=cur)
        self.TV.heading('#0', text=self.name, anchor='w')

        # scrollbar Y
        self.yscrl = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.TV.yview)
        self.TV.configure(yscroll=self.yscrl.set)

        # scrollbar X
        self.xscrl = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.TV.xview)
        self.TV.configure(xscroll=self.xscrl.set)

        # Pack - zalezi na poradi !
        self.yscrl.pack(fill='y', side='right')
        self.xscrl.pack(fill='x', side='bottom')
        self.TV.pack(fill='both',side='top', expand='True')
        
        #----------------------------------------------------------------------
        # Internal objects
        #----------------------------------------------------------------------
        self.where    = None   # Last clicked object
        self.selected = {}     # Last selection

        #----------------------------------------------------------------------
        # Create right-click menu
        #----------------------------------------------------------------------
        self.rcm = tk.Menu(self.TV, tearoff = 0)
        self.rcm.add_command(label ="Filter this" , command=self.addFilter)
        self.rcm.add_command(label ="Show value"  , command=self.showValue)
        self.rcm.add_command(label ="Copy value"  , command=self.copyValue)
        self.rcm.add_command(label ="Expand All"  , command=lambda: self.expand())
        self.rcm.add_command(label ="Collapse All", command=lambda: self.collapse())
        
        #----------------------------------------------------------------------
        # Bind events on this TreeView to respective methods
        #----------------------------------------------------------------------
        self.TV.bind('<Double-Button-1>', self.doubleClick)
        self.TV.bind('<Button-3>',        self.rcmMenu  )
        self.TV.bind('<Control-a>',       self.selectAll)
        self.TV.bind('<Control-c>',       self.copyToClip)

        #----------------------------------------------------------------------
        # Styling
        #----------------------------------------------------------------------
        self.TV.tag_configure('TableCell',  font=font.nametofont('TkFixedFont'))
        self.TV.tag_configure('TreeCell',   font=font.nametofont('TkFixedFont'))
        
        self.TV.tag_configure('RedRow',     background='#ffcccc')   # red
        self.TV.tag_configure('YellowRow',  background='#ffffcc')   # yellow
        self.TV.tag_configure('GreenRow',   background='#ccffcc')   # green 
        self.TV.tag_configure('BlueRow',    background='#e6f3ff')   # blue
        self.TV.tag_configure('GrayRow',    background='#dddddd')   # gray
        self.TV.tag_configure('OrangeRow',  background='#ffcc99')   # orange
        self.TV.tag_configure('PurpleRow',  background='#e6ccff')   # purple
        self.TV.tag_configure('BrownRow',   background='#ffcc99')   # brown

        #----------------------------------------------------------------------
        self.journal.O()

    #--------------------------------------------------------------------------
    def clear(self):
        "Clears all content of the TreeView"
        
        self.journal.I(f'{self.name}.clear:')
        
        for i in self.TV.get_children():
            self.TV.delete(i)
            
        #----------------------------------------------------------------------
        # Clear objects
        #----------------------------------------------------------------------
        self.where = None
        
        self.selected['region' ] = ''
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
        
        reg   = ''
        row   = ''
        val   = ''
        col   = ''
        colid = -1
        head  = '' 
        
        #----------------------------------------------------------------------
        # Identify afected row
        #----------------------------------------------------------------------
        iid = self.TV.identify_row(event.y)
      
        #----------------------------------------------------------------------
        # Set focus here if no rows was clicked on
        #----------------------------------------------------------------------
        if iid:
            self.TV.focus(iid)
            self.TV.selection_set(iid)
        
        reg = self.TV.identify_region(event.x,event.y)
        #----------------------------------------------------------------------
        # If clicked on header
        #----------------------------------------------------------------------
        if reg == 'heading':
            
            head    = self.TV.identify_column(event.x)
            colid   = int(self.TV.identify_column(event.x)[1:]) - 1
            val     = self.TV.heading(head, 'text')
            
        #----------------------------------------------------------------------
        # If clicked on row in a table
        #----------------------------------------------------------------------
        elif reg == 'cell':

            curItem = self.TV.focus()
            val     = self.TV.item(curItem, 'values')
            colid   = int(self.TV.identify_column(event.x)[1:]) - 1
            
            row     = val
            val     = val[colid]
            hd      = self.TV.identify_column(event.x)
            col     = self.TV.heading(hd, 'text').replace(' '+_FLT,'')
            
        #----------------------------------------------------------------------
        # If clicked on row in a tree
        #----------------------------------------------------------------------
        elif reg == 'tree':
            
            curItem = self.TV.focus()
            val     = self.TV.item(curItem)
            
            row     = int(curItem)-1
            val     = val['text']
            hd      = self.TV.identify_column(event.x)
            col     = self.TV.heading(hd, 'text').replace(' '+_FLT,'')
            colid   = 1                                             # copy whole tree row

        #----------------------------------------------------------------------
        self.where = { 'region':reg, 'head':head, 'row':row, 'col':col, 'val':val, 'colNum':colid}

        #----------------------------------------------------------------------
        self.journal.M(f'{self.name}.clickWhere: {self.where}')
        self.journal.O()
        
        return self.where

    #--------------------------------------------------------------------------
    def setSelected(self, event):
        
        self.journal.I(f'{self.name}.setSelected:')
        
        where = self.clickWhere(event)
        
        #----------------------------------------------------------------------
        # If there is a valid click position
        #----------------------------------------------------------------------
        if (where['colNum'] > -1) or (where['region'] == 'tree'):
            
            self.selected['region' ] = where['region']
            self.selected['colNum' ] = where['colNum']
            self.selected['col'    ] = where['col' ]
            self.selected['val'    ] = where['val' ]
            self.selected['row'    ] = where['row' ]
            self.selected['head'   ] = where['head']

        #----------------------------------------------------------------------
        # NOT a valid click position
        #----------------------------------------------------------------------
        else:
            self.selected['region' ] = ''
            self.selected['colNum' ] = -1
            self.selected['col'    ] = ''
            self.selected['val'    ] = ''
            self.selected['row'    ] = {}
            self.selected['head'   ] = ''

        #----------------------------------------------------------------------
        self.journal.M(f'{self.name}.clickWhere: {self.where}')
        self.journal.O()
        
        return self.selected
       
    #--------------------------------------------------------------------------
    def doubleClick(self, event):

        self.journal.I(f'{self.name}.doubleClick:')

        self.setSelected(event)
        self.event_generate('<<SiqoTreeView-DoubleLeftClick>>')
        
        self.journal.M(f'{self.name}.doubleClick: {self.selected}')
        self.journal.O()
        
    #--------------------------------------------------------------------------
    def rcmMenu(self, event):
        
        self.setSelected(event)

        #----------------------------------------------------------------------
        if (self.selected['region'] in ['tree','cell']):
            try    : self.rcm.tk_popup(event.x_root, event.y_root)
            finally: self.rcm.grab_release()
            
    #--------------------------------------------------------------------------
    def expand(self, parent=''):
        "Expands all branches for Treelike view"
        
        self.journal.I(f'{self.name}.expand:')
        
        self.TV.item(parent, open=True)
        
        # Recursive expanding of children
        for child in self.TV.get_children(parent):
            self.expand(child)
            
        self.journal.O()
        
    def collapse(self, parent=''):
        "Collapses all branches for Treelike view"
        
        self.journal.I(f'{self.name}.collapse:')
        
        self.TV.item(parent, open=False)
        
        # Recursive collapsing of children
        for child in self.TV.get_children(parent):
            self.collapse(child)
            
        self.journal.O()
        
    #--------------------------------------------------------------------------
    def datToTab(self, dat, lights=[]):
        """
        # Populates TreeView in form of a Table. Returns message
        #==========================================================================
        # TreeView as a Table
        #
        # dat   : data to show as list of rows. Row [0] is for headers
        #         [[]]
        #
        # lights: Highlightning rules for rows
        #         [{'colId':int, 'test':str, 'val':str, 'tags':[]}]
        #         test can be one of {'starts', 'not starts', 'cont', 'is', 'lt', 'gt'}
        #
        #--------------------------------------------------------------------------
        """
        
        self.journal.I(f'{self.name}.datToTab:')
        self.lights = lights

        #----------------------------------------------------------------------
        # Check incoming data
        #----------------------------------------------------------------------
        if not isinstance(dat,list) or len(dat)==0:
            
            self.journal.M(f'{self.name}.datToTab: Data is empty or in wrong structure', True)
            self.journal.O()
            return f"Data for TreeView '{self.name}' is empty or in wrong structure"
        
        #----------------------------------------------------------------------
        # Set headers from dat[0]
        #----------------------------------------------------------------------
        if self.lineNum: columns = ["POS"]
        else           : columns = []
        
        columns.extend(dat[0])
        self.TV["columns"] = columns

        #----------------------------------------------------------------------
        # Get max width for each column and set coeff for shrinking
        #----------------------------------------------------------------------
        maxW = [1] * len(self.TV["columns"])

        #----------------------------------------------------------------------
        # First, find out actual max width for each column
        #----------------------------------------------------------------------
        for row in dat:
            
            # Nastavim pociatocny index ppodla lineNum
            if self.lineNum: 
                i = 1
                maxW[0] = 5  #POS 5-ciferny
            else           : i = 0
            
            #------------------------------------------------------------------
            # Prejdem vsetky skutocne col v riadku
            #------------------------------------------------------------------
            for col in row:
                if col: w = len(str(col)) 
                else  : w = 0

                if w > maxW[i]: maxW[i] = w
                i += 1

        #----------------------------------------------------------------------
        # Second, cut to WIDTH_MAX                 
        sumW = sum(maxW)
        
        if sumW > _WIDTH_SUM:
            for i in range( len(maxW) ): 
                if maxW[i] > _WIDTH_MAX: maxW[i] = _WIDTH_MAX

        #----------------------------------------------------------------------
        # Third, shrink/expand by coefficient
        sumW = sum(maxW)
        cW = _WIDTH_SUM / sumW
        
        self.journal.M(f'{self.name}.datToTab: sumW={sumW}, cW={cW}')
        
        #----------------------------------------------------------------------
        # Define column's properties
        #----------------------------------------------------------------------
        i = 0
        for col in self.TV["columns"]: 
            
            pixW = int(9*cW*maxW[i]) + 0    # vypocitana width in pixels
            minW = 9*len(col)               # min width = 9 pix * dlzka hlavicky
            if pixW < minW: pixW = minW     # ak je minW vacsie ako vypocitane, tak minW
            self.TV.column(col, width=pixW, minwidth=minW, stretch=False)
            i += 1
        
        #----------------------------------------------------------------------
        # Define column's headers
        #----------------------------------------------------------------------
        for col in self.TV["columns"]:
            self.TV.heading(col, text=col, anchor='w', command=lambda _col = col: self.sortColumn(_col, False))
        
        #----------------------------------------------------------------------
        # Populate rows from dat
        #----------------------------------------------------------------------
        pos = 1
        for row in dat[1:]:
            
            #------------------------------------------------------------------
            # Add line number
            #------------------------------------------------------------------
            if self.lineNum: row.insert(0, pos)
            pos += 1
            
            #------------------------------------------------------------------
            # Add row to TreeView
            self.TV.insert('', tk.END, values=row)

        #----------------------------------------------------------------------
        # Styling
        #----------------------------------------------------------------------
        self.TV['show'] = 'headings'
        self.coloring()
        self.tabular = True

        # enable/disable right-click menu commands
        self.rcm_enabler()

        #----------------------------------------------------------------------
        self.journal.O()
        return 'OK'

    def coloring(self):
        # colort rows in treeview based in Ligths values
        for i, rowItem in enumerate(self.TV.get_children()):
            #get row values
            row = self.TV.item(rowItem)
            # if row has values
            if row["values"]:
                row = row["values"]
            else:
                continue

            #------------------------------------------------------------------
            # Highlighted rows
            colored = False
            for high in self.lights:
                    
                # If does not contain high['colId'], then break
                if row[ high['colId'] ] is None: break

                # If colored already, then break
                if colored: break

                #--------------------------------------------------------------
                if   high['test'] == 'starts':
                    
                    if row[ high['colId'] ].startswith( high['val']  ): 
                        self.TV.item(rowItem, tags=high['tags'])
                        colored = True
                
                #--------------------------------------------------------------
                elif high['test'] == 'not starts':

                    if not row[ high['colId'] ].startswith( high['val']  ): 
                        self.TV.item(rowItem, tags=high['tags'])
                        colored = True

                #--------------------------------------------------------------
                elif high['test'] == 'cont':

                    if high['val'] in row[ high['colId'] ]:
                        self.TV.item(rowItem, tags=high['tags'])
                        colored = True

                #--------------------------------------------------------------
                elif high['test'] == 'is':

                    if row[ high['colId'] ] == high['val']: 
                        self.TV.item(rowItem, tags=high['tags'])
                        colored = True

                #--------------------------------------------------------------
                elif high['test'] == 'lt':
                    rr = 0 if row[high['colId']] == 'None' else row[high['colId']]
                    if rr < high['val']: 
                        self.TV.item(rowItem, tags=high['tags'])
                        colored = True

                #--------------------------------------------------------------
                elif high['test'] == 'gt':
                    rr = 0 if row[high['colId']] == 'None' else row[high['colId']]
                    if rr > high['val']: 
                        self.TV.item(rowItem, tags=high['tags'])
                        colored = True

            #------------------------------------------------------------------
            # Non-Highlighted rows
            if not colored:
                # Even/Odd rows
                self.TV.item(rowItem, tags=['TableCell'] if i % 2 == 0 else ['TableCell', 'BlueRow'])

    #==========================================================================
    # Working with the Value
    #--------------------------------------------------------------------------
    def showValue(self):
        "Show value from selected cell"
        
        sel=self.selected
        self.journal.I(f"{self.name}.showValue: sel='{sel}'")
        
        if sel['colNum'] > -1:
            
            val = sel['val']
            
            self.clipboard_clear()
            self.clipboard_append(val)
            messagebox.showinfo(title=f"Column: {sel['col']}",  message=val)
        
        self.journal.O()
    
    def copyValue(self):
        "Copy value from selected cell"
        
        sel=self.selected
        self.journal.I(f"{self.name}.showValue: sel='{sel}'")
        
        if sel['colNum'] > -1:
            
            val = sel['val']
            
            self.clipboard_clear()
            self.clipboard_append(val)
        
        self.journal.O()
        
    #==========================================================================
    # Filtering the Table
    #--------------------------------------------------------------------------
    def addFilter(self):
        "Set filter based on "
        # Filter only in tabular form
        if self.tabular:
            sel=self.selected
            self.journal.I(f"{self.name}.addFilter: sel='{sel}'")
            
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
        for child in self.TV.get_children():
            
            rowItem = self.TV.item(child)

            #------------------------------------------------------------------
            # Ak riadok obsahuje stlpce, t.j. nieje to fiktivny prazdny riadok
            #------------------------------------------------------------------
            if rowItem["values"] != '':
                    
                #--------------------------------------------------------------
                # Test if row matches filters
                #--------------------------------------------------------------
                if str(rowItem["values"][colNum]) != val: self.TV.delete(child)
            
        #----------------------------------------------------------------------
        # Ad flag to column's heading 
        #----------------------------------------------------------------------
        self.TV.heading(col, text=f'{col} {_FLT}')
        self.journal.O()
            
    #==========================================================================
    # Sorting the column in the Table
    #--------------------------------------------------------------------------
    def sortColumn(self, col, reverse=False):

        self.journal.I(f"{self.name}.sortColumn: col='{col}', reverse={reverse}")
        
        # Ziskam zoznam zotriedenych hodnot        
        lst = [(self.TV.set(k, col), k) for k in self.TV.get_children('')]
        lst.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(lst):
            self.TV.move(k, '', index)

        # Resetnem nazvy stlpcov na originalne nazvy
        for c in  self.TV["columns"]: self.TV.heading(c, text=c)
            
        # K nazvu sortovaneho stlpca doplnim zank ASC/DSC
        if reverse: text = f'{col} {_DSC}'
        else      : text = f'{col} {_ASC}'
        
        self.TV.heading(col, text=text, command=lambda _col=col: self.sortColumn(_col, not reverse))
        self.coloring()

        self.journal.O()

    #--------------------------------------------------------------------------
    def datToTree(self, dat, rootId=None, maxId=0, indent=12, openLvl=2, lvl=0, lights=[]):
        """
        # Populates TreeView in form of a Tree. Returns max Id
        #==========================================================================
        # TreeView as a Tree
        #
        # dat   : data to show as list of rows. Row [0] is for headers
        #         [{}]
        #
        #
        # lights: Highlightning rules for dictionary
        #         [{'key':str, 'test':str, 'val':variable, 'tags':[]}]
        #         test can be one of {'starts', 'not starts', 'cont', 'is', 'lt', 'gt'}
        #
        #--------------------------------------------------------------------------
        """
        
        #----------------------------------------------------------------------
        # Kontrola existencie udajov
        #----------------------------------------------------------------------
        if dat is None or len(dat)==0: return maxId
        
        #----------------------------------------------------------------------
        # Pri prvom prechode metodou konfiguracia zobrazenia
        #----------------------------------------------------------------------
        if rootId is None: 
            self.journal.I(f"{self.name}.datToTree: len = {len(dat)}")
            self.tabular = False
            self.lights = lights

        #----------------------------------------------------------------------
        # Nastavim lokalne hodnoty
        #----------------------------------------------------------------------
        localPos = 0


        #----------------------------------------------------------------------
        # Prejdem vsetky polozky dictionary
        #----------------------------------------------------------------------
        for key, val in dat.items():
            
            maxId += 1
            tags   = ['TreeCell']

            #------------------------------------------------------------------
            # Ak je value dictionary, potom rekurzia
            #------------------------------------------------------------------
            if type(val)==dict: 
                
                if lvl < openLvl: opn = True
                else            : opn = False
                
                #--------------------------------------------------------------
                # Highlightning test if dat[key] ?? testValue
                #--------------------------------------------------------------
                tags.extend( self.getTreeDicTags(val) )

                #--------------------------------------------------------------
                # Vlozenie header riadku pre dictionary s hodnotou key
                #--------------------------------------------------------------
                self.TV.insert('', tk.END, text=f'[{key}]', iid=maxId, open=opn, tags=tags)
                if rootId is not None: self.TV.move(maxId, rootId, localPos)
                
                maxId  = self.datToTree(val, maxId, maxId, indent, openLvl, lvl+1, lights)
            
            #------------------------------------------------------------------
            # Ak je value list
            #------------------------------------------------------------------
            elif type(val)==list: 
                
                self.TV.insert('', tk.END, text=f'[{key}]', iid=maxId, open=True, tags=tags)
                listRoot = maxId
                if rootId is not None: self.TV.move(listRoot, rootId, localPos)

                # Vlozim list po riadkoch
                listPos = 0
                for row in val:
                    
                    maxId   += 1
                    self.TV.insert('', tk.END, text=f'{str(row)}', iid=maxId, open=True, tags=tags)
                    self.TV.move(maxId, listRoot, listPos)
                    listPos += 1
            
            #------------------------------------------------------------------
            # Trivialna polozka
            #------------------------------------------------------------------
            else: 
                #--------------------------------------------------------------
                # Highlightning test ak som na spravnom riadku
                #--------------------------------------------------------------
                tags.extend( self.getTreeLineTags(key, val) )

                #--------------------------------------------------------------
                # Vlozim do stromu
                #--------------------------------------------------------------
                key = str(key).ljust(indent)
                self.TV.insert('', tk.END, text=f'{key:20}: {str(val)}', iid=maxId, open=True, tags=tags)
                
                #--------------------------------------------------------------
                # Ak som v podstrome, presuniem pod rootId
                #--------------------------------------------------------------
                if rootId is not None: self.TV.move(maxId, rootId, localPos)
                
            #------------------------------------------------------------------
            # Zvysenie lokalnej pozicie
            #------------------------------------------------------------------
            localPos += 1
                
        #----------------------------------------------------------------------
        # Pri poslednom prechode metodou 
        #----------------------------------------------------------------------
        if rootId is None: 
            # enable/disable right-click menu
            self.rcm_enabler()
            self.journal.O()

        #----------------------------------------------------------------------
        return maxId
        
    #--------------------------------------------------------------------------
    def getTreeDicTags(self, dic):
        
        tagSet = set()  # Set pretoze moze dojst k opakovanemu vlozeniu rovnakeho tagu
        
        #----------------------------------------------------------------------
        # Otestujem vsetky zaznamy v dic
        #----------------------------------------------------------------------
        for key, val in dic.items():
            
            tagSet.update(self.getTreeLineTags(key, val))
        
        #----------------------------------------------------------------------
        # Konverzia tagSet na list
        #----------------------------------------------------------------------
        toRet = [tag for tag in tagSet]
        
        return toRet        

    #--------------------------------------------------------------------------
    def getTreeLineTags(self, key, val):
        
        tagSet = set()  # Set pretoze moze dojst k opakovanemu vlozeniu rovnakeho tagu
        
        #----------------------------------------------------------------------
        # Prejdem vsetky pravidla highligthningu
        #----------------------------------------------------------------------
        for high in self.lights:
            
            tKey = high['key' ]
            tVal = high['val' ]
            tags = high['tags']
            
            #------------------------------------------------------------------
            # Ak som na riadku ktory sa ma zvyraznit
            #------------------------------------------------------------------
            if key == tKey:

                #--------------------------------------------------------------
                # Test podmienky highlightningu
                #--------------------------------------------------------------
                if   high['test'] == 'starts':                 

                    if val.startswith(tVal)    : tagSet.update(tags)
                
                #--------------------------------------------------------------
                elif high['test'] == 'not starts':

                    if not val.startswith(tVal): tagSet.update(tags)
                
                #--------------------------------------------------------------
                elif high['test'] == 'cont':

                    if val.count(tVal) > 0     : tagSet.update(tags)

                #--------------------------------------------------------------
                elif high['test'] == 'is':

                    if val == tVal             : tagSet.update(tags)

                #--------------------------------------------------------------
                elif high['test'] == 'lt':

                    if val < tVal              : tagSet.update(tags)

                #--------------------------------------------------------------
                elif high['test'] == 'gt':

                    if val > tVal              : tagSet.update(tags)

        #----------------------------------------------------------------------
        # Konverzia tagSet na list
        #----------------------------------------------------------------------
        toRet = [tag for tag in tagSet]
        
        return toRet
        
    #--------------------------------------------------------------------------
    def selectAll(self, _):
        # Ctrl+A
        # Najjednoduchsi Select All
        self.TV.selection_set(self.TV.get_children())

    #--------------------------------------------------------------------------
    def copyToClip(self, _):
      # Ctrl+C
      # TAB Seperated Value do Clipboard
      # Najrpv kopirovat hlavicky, potom riadky
      if self.TV.selection():
        self.clipboard_clear()
        hdrs = "\t".join(self.TV["columns"])
        self.clipboard_append(hdrs+'\n')
        for row in self.TV.selection():
            val= "\t".join(self.TV.item(row, 'values') )
            self.clipboard_append(val+'\n')

    #--------------------------------------------------------------------------
    def rcm_enabler(self):
        # for all rcm elements enable it based on tabular value
        for i in range(self.rcm.index('end')+1):
            if self.rcm.type(i) == 'separator':
                continue
            id = self.rcm.entrycget(i, 'label')
            if not self.tabular and id == 'Filter this':
                self.rcm.delete(i)
            if self.tabular and id == 'Expand All':
                # po delete by sa zmenil index, najpr delete Collapse All
                self.rcm.delete(i+1)
                self.rcm.delete(i)

#==============================================================================
#   Inicializacia kniznice
#------------------------------------------------------------------------------
print(f'SIQO TreeView library ver {_VER}')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------