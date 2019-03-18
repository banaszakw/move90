#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import datetime
import itertools
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

BASIC_PAD = 5
TXT = {'browse': "Przeglądaj...",
       'err': "Błąd",
       'ok': "OK",
       'cancel': "Anuluj",
       'warn': "Ostrzeżenie",
       'from': "Przenieś z",
       'to': "Przenieś do",
       'move': "Przenieś katalog zlecenia do \"\_wyslane\"",
       'enabled': "Aktywne",
       'showlog': "Zobacz log"}
ERR = {'invalid': "Ścieżka nie jest katalogiem: '{}'",
       'noselect': "Nie wskazano katalogów w: {}",
       'noactive': "Nie wybrano typu zlecenia",
       'unittests': "View is currently running standalone - for unittests "
                    "purpose only."}


class BasicFrame:
    """Provides the basic widgets: Frame, Checkbutton and the method to
    (de)activate all of the children of Frame.

    Arguments:
    parents -- tkinter parent Widget
    """
    CHCK_BTN = {'expand': 0,
                'fill': tk.X,
                'pady': 5,
                'side': tk.LEFT}
    FRM = {'expand': 1,
           'fill': tk.BOTH,
           # 'padx': 5,
           # 'pady': 5,
           'side': tk.TOP}
    UNIT = 15

    def __init__(self, parent):
        self.parent = parent
        self.isactive = tk.BooleanVar(value=False)
        self.create_frame()

    def create_frame(self):
        """Create a core Frame widget."""
        self.frame = ttk.Frame(self.parent, padding=BASIC_PAD)
        self.frame.pack(self.FRM)

    def get_isactive(self):
        """Simple getter. Get the value of a given BasicFrame's
        attribute. Return boolean.
        """
        return self.isactive.get()

    def set_isactive(self, val):
        """Simple setter. Set the BasicFrame's attribute `isactive` to
        a given value. Function set() require a boolean value (but
        accepts even a boolean value as a string, e.g. `true`,
        `False`). If `val` is not a valid boolean value , tkinter raises
        an exception.
        """
        self.isactive.set(val)

    def retoggle(self, var):
        """Helper function of toggle_act. Disable Entry and Button
        widgets.
        Arguments:
        var -- boolean value
        """
        if var.get() and not self.get_isactive():
            try:
                self.entry.state(['disabled'])
                self.button.state(['disabled'])
            except AttributeError:
                pass  # do loga?

    def toggle_act(self, var, exclude=True):
        """
        Enable if is currently disabled or disable if is enabled,
        every child element of this Frame. Disabling and enabling
        depends on the `var` value (boolean value). This function
        is calls by a ttk.Checkbutton widget. So if `exclude` is
        True a ttk.Checkbutton widget stays enabled.
        winfo_children -- returns a list of the tkinter object(s)
        like ttk.Button, ttk.Checkbutton, ttk.Entry.

        Arguments:
        var -- boolean value
        exclude -- boolean value
        """
        for w in self.frame.winfo_children():
            if var.get():
                w.state(['!disabled'])
            else:
                w.state(['disabled'])
        if exclude:
            try:
                self.checkbutton.state(['!disabled'])  # zrobic osobna funkcje?
            except AttributeError:
                pass
        # to jest brzydkie rozwiazanie
        self.retoggle(var)

    def create_checkbutton(self, text=""):
        """Create a Checkbutton widget."""
        self.checkbutton = ttk.Checkbutton(self.frame,
                                           command=lambda:
                                               self.toggle_act(self.isactive),
                                           text=text,
                                           variable=self.isactive)
        self.checkbutton.pack(self.CHCK_BTN)
        self.toggle_act(self.isactive, False)


class DirectorySelector(BasicFrame):
    """Set of two widgets: Button and Entry to selecting path.

    Arguments:
    parents -- tkinter parent Widget"""

    ENTR = {'expand': 1,
            'fill': tk.X,
            'padx': 10,
            'side': tk.LEFT}

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.direc = tk.StringVar()
        self.err = ERR
        self.txt = TXT

    def getdirec(self):
        """Simple getter. Get the value of a given DirectorySelector's
        attribute. Return string.
        """
        return self.direc.get()

    def setdirec(self, val):
        """Simple setter. Set the DirectorySelector's attribute `direc`
        to a given value. Function set() require a string value (but
        accepts other types and converts them to a string.
        """
        self.direc.set(val)

    def opendirec(self, var):
        """Open a askdirectory dialog and set a directory path."""
        direc = filedialog.askdirectory(initialdir=var.get())
        if direc:
            self.setdirec(os.path.normpath(direc))

    def validate(self):
        """Check if a given path exists and is a directory."""
        # return os.path.isdir(self.direc.get())
        return os.path.isdir(self.getdirec())

    def showerror(self, msg):
        messagebox.showerror(title=self.txt['err'], message=msg)

    def invalid(self):
        """Get a selected directory path and show an error dialog that this
        path is not a valid path. Funtion is called by a Entry widget's
        `invalidcommand` attribute.
        """
        path = self.getdirec()
        msg = self.err['invalid'].format(path)
        self.showerror(msg)

    def create_widgets(self):
        """Create widgets."""
        entry_style = ttk.Style()
        entry_style.map('C.TEntry', foreground=[('invalid', 'red'),
                                                ('disabled', '#a3a3a3')])
        self.button = ttk.Button(self.frame,
                                 command=lambda: self.opendirec(self.direc),
                                 text=self.txt['browse'],
                                 width=self.UNIT)
        self.button.pack(side=tk.LEFT)
        self.entry = ttk.Entry(self.frame,
                               invalidcommand=self.invalid,
                               textvariable=self.direc,
                               style='C.TEntry',
                               validate='focusout',
                               # wczesniej: funkcja `validate` w nawiasie
                               validatecommand=(self.validate),
                               width=5*self.UNIT)
        self.entry.pack(self.ENTR)


class TabWidget(BasicFrame):
    """Tab Widget"""

    def __init__(self, parent, typeof):
        super().__init__(parent)
        self.parent = parent
        self.typeof = typeof
        self.tosearch = tk.BooleanVar(value=False)
        self.from_dirsel_list = []
        self.dest_dirsel_list = []
        self.txt = TXT
        self.enable_tosend = ('IN',)
        self.create_widget()

    def create_active_btn(self):
        """Create a Checkbutton widget to (de)activate entire tab."""
        frame = ttk.Frame(self.parent, padding=BASIC_PAD)
        ttk.Checkbutton(frame,
                        command=self.active_toggle,
                        text=self.txt['enabled'],
                        variable=self.tosearch).pack(self.CHCK_BTN)
        frame.pack(BasicFrame.FRM, padx=5)

    def create_from_panel(self, amount=1):
        """Create a panel containing widgets used for selecting path
        providing by a DirectorySelector class.

        Arguments:
        amount -- number of the panels.
        """
        labelframe = ttk.LabelFrame(self.parent,
                                    padding=BASIC_PAD,
                                    text=self.txt['from'])
        for i in range(amount):
            dirsel = DirectorySelector(labelframe)
            dirsel.create_checkbutton()
            dirsel.create_widgets()
            self.from_dirsel_list.append(dirsel)
            if amount == 1:
                dirsel.isactive.set(True)
        labelframe.pack(self.FRM, pady=5)

    def create_dest_panel(self, amount=3):
        """Create a panel containing widgets used for selecting
        destination path(s) providing by a DirectorySelector and
        a BasicFrame class.

        Arguments:
        amount -- number of the panels.
        """
        labelframe = ttk.LabelFrame(self.parent,
                                    padding=BASIC_PAD,
                                    text=self.txt['to'])
        self.tosend = BasicFrame(labelframe)
        self.tosend.create_checkbutton(self.txt['move'])
        for i in range(amount):
            dirsel = DirectorySelector(labelframe)
            dirsel.create_checkbutton()
            dirsel.create_widgets()
            self.dest_dirsel_list.append(dirsel)
        labelframe.pack(self.FRM, pady=5)

    def active_toggle(self):
        """(De)activate the checbuttons and call functions to
        (de)activating rest of the widgets defined in other classes.
        from_dirsel_list -- list of DirectorySelector object(s)
        dest_dirsel_list -- list of DirectorySelector object(s)
        """
        for (from_dirsel,
             dest_dirsel) in itertools.zip_longest(self.from_dirsel_list,
                                                   self.dest_dirsel_list):
            if from_dirsel:
                from_dirsel.toggle_act(self.tosearch, False)
                from_dirsel.checkbutton.state(['disabled'])
            if dest_dirsel:
                dest_dirsel.toggle_act(self.tosearch, False)
        self.tosend.toggle_act(self.tosearch, False)
        if self.typeof.upper() not in self.enable_tosend:
            self.tosend.checkbutton.state(['disabled'])

    def get_from_direc(self):
        """Return n-elements (`n` == `amount` in create_from_panel)
        list of the strings with paths.
        from_dirsel_list -- list of DirectorySelector object(s)
        getdirec -- DirectorySelector's method, returns string
        get_isactive -- BasicFrame's method. DirectorySelector inherits
        it from BasicFrame, returns boolean
        """
        return [dirsel.getdirec() for dirsel
                in self.from_dirsel_list
                if dirsel.get_isactive()]

    def get_dest_direc(self):
        """Return n-elements (`n` == `amount` in create_dest_panel)
        list of the (possibly empty) strings. Strings can be empty,
        because paths validation takes place in Controller. This allows
        to write empty path to the config file.
        dest_dirsel_list -- list of DirectorySelector object(s)
        getdirec -- DirectorySelector's method, returns string
        """
        return [dirsel.getdirec() for dirsel in self.dest_dirsel_list]

    def get_active_direc(self):
        """Return n-elements (`n` == `amount` in create_dest_panel)
        list of the boolean values.
        get_isactive -- BasicFrame's method. DirectorySelector inherits
        it from BasicFrame, returns boolean
        """
        return [dirsel.get_isactive() for dirsel in self.dest_dirsel_list]

    def get_tosend(self):
        """Return a boolean value of the Checkbox widget in BasicFrame.
        This checkbox decides whether the Entry widget is active or not.
        Default value is False.
        tosend -- a BasicFrame object
        get_isactive -- BasicFrame's method, returns boolean
        """
        return self.tosend.get_isactive()

    def get_tosearch(self):
        """Return a boolean value. Default is False."""
        return self.tosearch.get()

    def set_srcdir(self, val, fill=''):
        """Call the DirectorySelector method for every DirectorySelector
        object to setting value of given entry. Function is called by
        Controller.
        from_dirsel_list -- list of DirectorySelector object(s)
        setdirec -- DirectorySelector's method, requires string
        Arguments:
        val -- list of strings values
        fill -- default value
        """
        for from_dirsel, ival in itertools.zip_longest(self.from_dirsel_list,
                                                       val,
                                                       fillvalue=fill):
            from_dirsel.setdirec(ival)

    def set_dstdir(self, val, fill=''):
        """Call the DirectorySelector method for every DirectorySelector
        object to setting value of given entry. Function is called by
        Controller.
        dest_dirsel_list -- list of DirectorySelector object(s)
        setdirec -- DirectorySelector's method, requires string
        Arguments:
        val -- list of strings values
        fill -- default value
        """
        for dest_dirsel, ival in itertools.zip_longest(self.dest_dirsel_list,
                                                       val,
                                                       fillvalue=fill):
            dest_dirsel.setdirec(ival)

    def set_active_direc(self, val, fill=False):
        """Call the DirectorySelector method for every DirectorySelector
        object to setting value of given checkbox. Function is called by
        Controller.
        dest_dirsel_list -- list of DirectorySelector object(s)
        set_isactive -- BasicFrame's method. DirectorySelector inherits
        it from BasicFrame, requires boolean
        Arguments:
        val -- list of strings values
        fill -- default value
        """
        for dest_dirsel, ival in itertools.zip_longest(self.dest_dirsel_list,
                                                       val,
                                                       fillvalue=fill):
            dest_dirsel.set_isactive(ival)

    def set_tosend(self, val):
        """Set the value of BasicFrame object attribute `isactive`
        controlled by a Checkbox widget. Function is called by
        Controller and then calls BasicFrame's method.
        tosend -- BasicFrame object
        set_isactive -- BasicFrame's method, requires boolean"""
        self.tosend.set_isactive(val)

    def create_widget(self):
        self.create_active_btn()
        self.create_from_panel()
        self.create_dest_panel()
        self.active_toggle()


class MainApp:

    BTN = {'expand': 0, 'padx': (2, 0), 'pady': 2, 'side': tk.RIGHT}
    LBL = {'expand': 1, 'fill': tk.X, 'padx': (0, 2), 'pady': 2, 'side': tk.LEFT}

    def __init__(self):
        self.root = tk.Tk()
        self.controller = None
        self.err = ERR
        self.txt = TXT
        self.root.resizable(1, 0)
        # self.root.mainloop()

    def register(self, controller):
        """Register a controller to give callbacks to."""
        self.controller = controller

    def add_spaces(self, tablist, offset=4):
        """Add leading and trailling spaces around tabs name. This
        solves a tkinter bug of displaying tabs name in default theme on
        Windows.
        """
        tablist = [i.strip() for i in tablist]
        filler = len(max(tablist, key=len)) + offset
        return ["{:^{f}}".format(i, f=filler) for i in tablist]

    # def select_theme(self):
    #     if sys.platform.startswith('win'):
    #         self.style = ttk.Style()
    #         self.style.theme_use('vista')
    #         print(self.style.theme_names())

    def create_tabs(self, tabsname):
        """Create the ttk.Notebook widget and insert into it the tabs
        widgets.

        Arguments:
        tabsname -- a list of tabs names
        """
        frame = ttk.Frame(self.root, padding=5)
        tabbar = ttk.Notebook(frame)
        self.tablist = []
        for tname in self.add_spaces(tabsname):
            tabframe = ttk.Frame(self.root)
            self.order = TabWidget(tabframe, tname.strip())
            tabbar.add(tabframe, compound=tk.CENTER,  padding=5, text=tname)
            self.tablist.append(self.order)
        tabbar.pack(BasicFrame.FRM)
        frame.pack(expand=1, fill=tk.BOTH)

    def callback(self, event):
        """Show logfile content in text editor. Called by Label widget."""
        try:
            self.controller.showlogg()
        except AttributeError:
            print(ERR['unittests'])

    def create_bottom_bar(self):
        """Create a bottom bar containing two buttons and status bar."""
        frame = ttk.Frame(self.root, padding=5)
        self.status = tk.StringVar()
        ttk.Button(frame,
                   command=self._quit,
                   text=self.txt['cancel'],
                   width=BasicFrame.UNIT).pack(self.BTN)
        ttk.Button(frame,
                   command=self.run,
                   text=self.txt['ok'],
                   width=BasicFrame.UNIT).pack(self.BTN)
        ttk.Label(frame,
                  borderwidth=1,
                  justify=tk.LEFT,
                  padding=5,
                  relief=tk.SUNKEN,
                  textvariable=self.status).pack(self.LBL)
        frame.pack(expand=0, fill=tk.X)
        logfile_link = ttk.Label(frame,
                                 cursor='hand2',
                                 foreground='blue',
                                 justify=tk.LEFT,
                                 padding=5,
                                 text=self.txt['showlog'])
        logfile_link.pack(self.BTN)
        logfile_link.bind('<Button-1>', self.callback)

    def get_tablist(self):
        """Get list of tabs."""
        return self.tablist

    def get_last_modif(self):
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(__file__))
        return "Last modification: " + str(mtime)

    def set_statusbar(self, msg=None):
        if msg is None:
            msg = self.get_last_modif()
        self.status.set(msg)

    def show_warning(self, msg):
        messagebox.showwarning(title=self.txt['warn'], message=msg)

    def isdir_selected(self):
        """Check if all directory paths in all TabWidget object(s) are
        selected. Returns boolean.
        tablist -- the list of the TabWidget object(s)
        get_tosearch -- TabWidget's method, returns a boolean value
        get_from_direc -- TabWidget's method, returns list of strings
        get_dest_direc -- TabWidget's method, returns list of strings
        """
        for t in self.tablist:
            if t.get_tosearch():
                if not any(t.get_from_direc()) or not any(t.get_dest_direc()):
                    msg = self.err['noselect'].format(t.typeof)
                    self.show_warning(msg)
                    return False
        return True

    def isany_active(self):
        """Check if at least one of the TabWidget object is for 
        searching. Returns boolean.
        """
        if any(t.get_tosearch() for t in self.tablist):
            return True
        self.show_warning(self.err['noactive'])
        return False

    def run(self):
        """Main function of the View."""
        if self.isany_active() and self.isdir_selected():
            try:
                self.controller.run()
            except AttributeError:
                print(ERR['unittests'])

    def _quit(self):
        self.root.quit()
        self.root.destroy()

    def mainloop(self):
        self.root.mainloop()


def main():
    print("View is currently running standalone")
    testlist = ["Test" + str(i) for i in range(10)]
    testlist.insert(0, 'IN')
    app = MainApp()
    app.root.title("Test")
    app.create_tabs(testlist)
    app.create_bottom_bar()
    app.set_statusbar("Test msg")
    app.mainloop()


if __name__ == "__main__":
    main()
