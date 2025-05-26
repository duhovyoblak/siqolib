#==============================================================================
# Siqo tkInter library
#------------------------------------------------------------------------------
import tkinter                as tk
from   tkinter                import ttk, scrolledtext,simpledialog , messagebox

#==============================================================================
# package's constants
#------------------------------------------------------------------------------

#==============================================================================
# package's variables
#------------------------------------------------------------------------------

#==============================================================================
# Class SiqoMessage
#------------------------------------------------------------------------------
class SiqoMessage(tk.Toplevel):
    
    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, journal, name, text, wpix=500, hpix=500, lpix=300, tpix=200):
        "Call constructor of SiqoMessage and initialise it"

        self.journal = journal
        self.name    = name
        self.journal.I(f"tk.{self.name}.init:")

        #----------------------------------------------------------------------
        # Inicializacia okna
        #----------------------------------------------------------------------
        super().__init__()

        #----------------------------------------------------------------------
        # Create message window
        #----------------------------------------------------------------------
        self.geometry(f"{wpix}x{hpix}+{lpix}+{tpix}")

        # window title
        title_label = tk.Label(self, text=f'{self.name}', bg= "#2c2c2c", fg="white")
        title_label.pack(fill='x')

        self.focus_force()
        self.grab_set()

        #----------------------------------------------------------------------
        # Priprava scrollText-u
        #----------------------------------------------------------------------
        st = scrolledtext.ScrolledText(self, width=100,  height=10)
        st.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)  
        self.bind('<Escape>', self.close)     
     
        #----------------------------------------------------------------------
        # Nacitanie textu
        #----------------------------------------------------------------------
        for row in text: 
            st.insert(tk.END, row + '\n')
        
        self.journal.O()
        
    #--------------------------------------------------------------------------
    def close(self, event=None):
        "Destroy window"
        
        self.destroy()    
        
#==============================================================================
# Ask dialogs
#------------------------------------------------------------------------------
def askInt(container, title="Integer dialog", prompt="Zadaj celé číslo:", min=None, max=None):

    while True:

        result = simpledialog.askstring(title, prompt, parent=container)

        if result is None:
            return None  # Používateľ stlačil Cancel
        try:
            value = int(result)

            if min is not None and value < min:
                messagebox.showerror("Chyba", f"Zadaj celé číslo väčšie alebo rovné {min}!", parent=container)
                continue  # Opakovať, ak je hodnota menšia ako minimum
          
            if max is not None and value > max:
                messagebox.showerror("Chyba", f"Zadaj celé číslo menšie alebo rovné {max}!", parent=container)
                continue

            return value

        except ValueError:
            messagebox.showerror("Chyba", "Zadaj platné celé číslo!", parent=container)

#------------------------------------------------------------------------------
def askReal(container, title="Real number dialog", prompt="Zadaj číslo:", min=None, max=None):

    while True:

        result = simpledialog.askstring(title, prompt, parent=container)

        if result is None:
            return None  # Používateľ stlačil Cancel
        
        try:
            value = float(result)

            if min is not None and value < min:
                messagebox.showerror("Chyba", f"Zadaj číslo väčšie alebo rovné {min}!", parent=container)
                continue  # Opakovať, ak je hodnota menšia ako minimum
          
            if max is not None and value > max:
                messagebox.showerror("Chyba", f"Zadaj číslo menšie alebo rovné {max}!", parent=container)
                continue

            return value

        except ValueError:
            messagebox.showerror("Chyba", "Zadaj platné číslo!", parent=container)

#==============================================================================
# Class SiqoEntry
#------------------------------------------------------------------------------
def getNumber(journal, name, label, entry='', wpix=500, hpix=500, lpix=300, tpix=200):
    
    journal.I(f"tk.getNumber: {name}")
    number = None
    
    winEntry = SiqoEntry(journal, name, label, entry, wpix, hpix, lpix, tpix)
    winEntry.wait_window(winEntry)
    entry = winEntry.getEntry()
    
    #--------------------------------------------------------------------------
    # Kontrola ci je cislo
    #--------------------------------------------------------------------------
    if entry is not None:
        
        try              : number = float(entry)
        except ValueError: messagebox.showerror(title='Error',  message=f'{entry} is a not valid number')
    
    journal.O(f"tk.getNumber: {number}")
    return number
    
#------------------------------------------------------------------------------
def getEntry(journal, name, label, entry='', wpix=500, hpix=500, lpix=300, tpix=200):
    
    journal.I(f"tk.getEntry: {name}")
    
    entry = None
    
    winEntry = SiqoEntry(journal, name, label, entry, wpix, hpix, lpix, tpix)
    winEntry.wait_window(winEntry)
    entry = winEntry.getEntry()
    
    journal.O(f"tk.getEntry: {entry}")
    
    return entry
    
#------------------------------------------------------------------------------
class SiqoEntry(tk.Toplevel):
    
    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, journal, name, label, entry='', wpix=250, hpix=150, lpix=300, tpix=200):
        "Call constructor of SiqoEntry and initialise it"

        self.journal = journal
        self.name    = name
        self.journal.I(f"tk.{self.name}.init:")

        #----------------------------------------------------------------------
        # Inicializacia okna
        #----------------------------------------------------------------------
        super().__init__()

        #----------------------------------------------------------------------
        # Priprava premennych
        #----------------------------------------------------------------------
        self.str_entry = tk.StringVar(value = entry)

        #----------------------------------------------------------------------
        # Create entry window
        #----------------------------------------------------------------------
        self.geometry(f"{wpix}x{hpix}+{lpix}+{tpix}")

        # window title
        title_label = tk.Label(self, text=f'{self.name}', bg= "#2c2c2c", fg="white")
        title_label.pack(fill='x')

        self.focus_force()
        self.grab_set()

        #----------------------------------------------------------------------
        # Nacitanie entry
        #----------------------------------------------------------------------
        ent_label = ttk.Label(self, text=label)
        ent_label.pack(expand=True, anchor=tk.W, padx=10, pady=10)

        ent_entry = ttk.Entry(self, textvariable=self.str_entry)
        ent_entry.pack(expand=False, fill='x', anchor=tk.E, padx=10, pady=10)
        ent_entry.focus()

        #----------------------------------------------------------------------
        # OK button
        #----------------------------------------------------------------------
        ok_button = ttk.Button(self, text="OK", command=self.entry )
        ok_button.pack(expand=True, anchor=tk.E, padx=10, pady=10)
        
        self.bind('<Return>', self.entry )
        self.bind('<Escape>', self.close )     
        
        self.journal.O()
        
    #--------------------------------------------------------------------------
    def getEntry(self):
        "Returns edited entry"
 
        toRet = self.str_entry.get().strip()
        
        if toRet == '': toRet=None
        self.journal.M(f"tk.{self.name}.getEntry: {toRet}")
        
        return toRet
        
    #--------------------------------------------------------------------------
    def close(self, event=None):
        "Destroy window"
        
        self.journal.M(f"tk.{self.name}.close:")
        self.destroy() 

    #--------------------------------------------------------------------------
    def entry(self, event=None):
        
        self.journal.I(f"tk.{self.name}.entry:")
        
        self.event_generate('<<SiqoEntry>>')
        self.close()       
        self.journal.O()
        
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
        self.journal.I(f"tk.{self.name}.init:")
        
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
        if 'pasw' in kwargs.keys(): self.str_pasw.set(kwargs['pasw'])
        
        #----------------------------------------------------------------------
        # Create login window
        #----------------------------------------------------------------------
        self.geometry("300x200+%d+%d" % (lpix + 300, hpix + 100))

        # window title
        title_label = tk.Label(self, text=f'Login to {self.name}', bg= "#2c2c2c", fg="white")
        title_label.pack(fill='x')

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
        pass_label = ttk.Label(self, text="Password/Token:")
        pass_label.pack(fill='x', expand=True, padx=10)

        pass_entry = ttk.Entry(self, textvariable=self.str_pasw, show="*")
        pass_entry.pack(fill='x', expand=True, padx=10)

        # login button
        login_button = ttk.Button(self, text="Login", command=self.login )
        login_button.pack(fill='x', expand=True, padx=10, pady=10)
        
        self.bind('<Return>', self.login )
        self.bind('<Escape>', self.close )     
        
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
        
#        self.journal.M(f"tk.{self.name}.getPassword: '{pasw}'")
        return pasw
    
    #--------------------------------------------------------------------------
    def close(self, event=None):
        "Destroy login window"
        
        self.destroy()    
          
    #--------------------------------------------------------------------------
    def login(self, event=None):
        
        self.journal.I(f"tk.{self.name}.login:")
        
        self.event_generate('<<SiqoLogin>>')
        self.close()

        self.journal.O()
        
#==============================================================================
#   Inicializacia kniznice
#------------------------------------------------------------------------------
print('SIQO message library ver 1.08')


if __name__ == "__main__":
    
    
    from   siqolib.journal          import SiqoJournal

    journal = SiqoJournal('InfoMarixGui component test', debug=4)

    #--------------------------------------------------------------------------
    # Test of the InfoMarixGui class
    #--------------------------------------------------------------------------
    journal.I('Test of InfoMarixGui class')

    win = tk.Tk()
    win.configure(bg='silver', highlightthickness=2, highlightcolor='green')
    win.title('Test of siqo_message class')
    win.minsize(width=600, height=300)
    win.config(highlightbackground = "green", highlightcolor= "green")

    #--------------------------------------------------------------------------
    # Zaciatok testu 
    #--------------------------------------------------------------------------

    # Pridanie buttonu na vyvolanie askInt
    def onAskInt():
        value = askInt(win, title="Zadaj číslo", prompt="Zadaj celé číslo:")
        print(f"Zadané číslo: {value}")

    btn_ask_int = tk.Button(win, text="Zadaj celé číslo", command=onAskInt)
    btn_ask_int.pack(pady=20)


    win.mainloop()

    journal.O()

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------