#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import itertools
import logging
import model
import os
import view
import webbrowser


CONFIGERR = {'nofile': "Brak pliku konfiguracyjnego",
             'parse': "Błąd odczytu pliku konfiguracyjnego",
             'keyerr': "{}: Brak żądanej wartości w pliku konfiguracyjnym. " \
                       "Użyto wartości domyślnych",
             'omit': "Pominięto szukanie {0}, ponieważ wskazano nieprawidłowe " \
                     "ścieżki lub nie wskazano żadnych ścieżek"}
MSG = {'done': "Gotowe! Przeniesiono: {0}. Nie przeniesiono: {1}.",
       'work': "Szukanie i przenoszenie: {}..."}


class Order:

    """ Class doc """
    def __init__(self, typeof, srcdir, dstdir, active_dstdir, tosend, tosearch):
        self.typeof = typeof
        self.srcdir = srcdir
        self.dstdir = dstdir
        self.active_dstdir = active_dstdir
        self.tosend = tosend
        self.tosearch = tosearch


class Controller:
    """ The controller's job is to take the user's input and figure out
        what to do with it. """

    def __init__(self):
        self.appname = "Move90"
        self.version = "0.1"
        self.userdir = os.path.expanduser('~')
        self.tablist = ["IN", "ODIS", "SLP", "ISLP", "WT", "GUI",
                        "KDVDB"]
        self.only_num = ("IN", "ISLP", "SLP", "WT", "GUI")
        self.num_brand = ("ODIS", "KDVDB")
        self.brand_dict = {'Audi': 'Audi_21',
                           'Seat': 'Seat_41',
                           'Skoda': 'Skoda_31',
                           'VW11': 'VW_11',
                           'VW12': 'VW_12',
                           'VW51': 'VW_51',
                           'VW66': 'VW_66'}
        self.configerr = CONFIGERR
        self.msg = MSG
        self.model = model.Model(self.only_num, 
                                 self.num_brand, 
                                 self.brand_dict)
        self.model.register(self)

    def make_gui(self):
        """Test"""
        self.view = view.MainApp()
        self.view.register(self)
        self.view.root.title(self.appname)
        self.view.create_tabs(self.tablist)
        self.view.create_bottom_bar()
        self.view.set_statusbar(" ".join((self.appname,
                                          'ver.',
                                          self.version)))

    def show_view(self):
        self.view.mainloop()

    def init_config(self):
        """ Initialise a ConfigParser object, creates a config file
            path, calls a function loading values from a config
            file. """
        self.config = configparser.ConfigParser()
        self.configfile = os.path.join(self.appdir, '.settings.ini')
        self.load_config()

    def create_appdir(self):
        """ Create a hidden application directory used by a config file
            and log files. """
        self.appdir = os.path.join(self.userdir,
                                   r'.woffice',
                                   r'.' + self.appname)
        os.makedirs(self.appdir, exist_ok=True)

    def create_log(self):
        """ Initialise a logging object and creates a log file. """
        self.logfile = os.path.join(self.appdir,
                               ''.join(('.', self.appname, '.log')))
        logging.basicConfig(filename=self.logfile,
                            filemode='w',
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        self.logger = logging.getLogger(__name__)
        
    def showlogg(self):
        webbrowser.open(self.logfile)

    def get_order_obj(self):
        """ Z Model pobiera listę obiektów, z ktorych we View zrobi
            interfejs. """
        return self.model.order_obj

    def format_input(self):
        """ Function doc """
        self.model.run()

    def callerr(self, path, msg):
        """ Function doc """
        self.view.callerr(path, msg)

    #def show_error(self, msg):
        #self.view.showwarning(msg)

    def show_warning(self, msg):
        self.view.showwarning(msg)

    def format_config(self, obj):
        """Pobiera pola z obiektu. Te spośród z nich, które są listami
        konwertuje na tekst rozdzielany znakami zapytania. Zwraca
        słownik.
        """
        obj_dict = obj.__dict__
        for key, val in obj_dict.items():
            if isinstance(val, list):
                obj_dict[key] = "?".join([str(v) for v in val])
        return obj_dict

    def write_config(self, objlist):
        """Checks if appdir exists and creates it if not. Writes data
        to a config file.

        Arguments:
        objlist -- list of Order object(s)
        """
        for obj in objlist:
            obj_dict = self.format_config(obj)
            typeof = obj_dict.get('typeof')
            self.config[typeof] = obj_dict
        if not os.path.isdir(self.appdir):
            os.makedirs(self.appdir, exist_ok=True)
        with open(self.configfile, 'w+') as fw:
            self.config.write(fw)

    def load_config(self):
        """ Checks if a configuration file exists, parses and loads
            data from it to the View. Splits into the list received data
            from the config file. """
        if os.path.isfile(self.configfile):
            try:
                self.config.read(self.configfile)
            except configparser.ParsingError:
                self.logger.warning(self.configerr['parse'])
        else:
            self.logger.warning(self.configerr['nofile'])
        for tab in self.view.get_tablist():
            typeof = tab.typeof
            try:
                srcdir = self.config[typeof]['srcdir']
                dstdir = self.config[typeof]['dstdir']
                active_dstdir = self.config[typeof]['active_dstdir']
                tosend = self.config[typeof]['tosend']
            except KeyError:
                self.logger.warning(self.configerr['keyerr'].format(typeof))
                srcdir = ''
                dstdir = ''
                active_dstdir = 'False' 
                # boolean as String because:
                # - String has the split() attribite
                # - data in the configfile is stored as String 
                tosend = False  # sprawdzic dlaczego nie String!
            tab.set_srcdir(srcdir.split('?'), fill='')
            tab.set_dstdir(dstdir.split('?'), fill='')
            tab.set_active_direc(active_dstdir.split('?'), fill=False)
            tab.set_tosend(tosend)

    def tosearch_checker(self, obj):
        """Get lists of the paths, check if are valid and return
        True. If are not valid write info to the log file and
        show a warning window.

        Arguments:
        obj -- Controller.Order object
        """
        if obj.tosearch:
            from_direc = obj.srcdir
            dest_direc = obj.dstdir
            active_direc = obj.active_dstdir
            dest_direc = list(itertools.compress(dest_direc, active_direc))
            if False not in map(os.path.isdir, from_direc) and \
                    False not in map(os.path.isdir, dest_direc):
                return True
            msg = self.configerr['omit'].format(obj.typeof)
            self.logger.warning(msg)
            self.view.show_warning(msg)
        return False

    def create_obj_from_other(self, inp_obj):
        """Get data from input object and create the Order object, pass
        receiving data to this new object.

        Arguments:
        new inp_obj -- view.TabWidget object
        """
        typeof = inp_obj.typeof
        from_direc = inp_obj.get_from_direc()
        dest_direc = inp_obj.get_dest_direc()
        active_direc = inp_obj.get_active_direc()
        tosend = inp_obj.get_tosend()
        tosearch = inp_obj.get_tosearch()
        return Order(typeof,
                     from_direc,
                     dest_direc,
                     active_direc,
                     tosend,
                     tosearch)

    def verify_obj(self, inp_obj):
        pass

    def run(self):
        """Main function of the Controller.
        objlist -- list of view.TabWidget object(s)
        """
        objlist = self.view.get_tablist()
        orderlist = []
        counter = 0
        remaining = 0
        for obj in objlist:
            order = self.create_obj_from_other(obj)
            orderlist.append(order)
            if self.tosearch_checker(order):
                msg = self.msg['work'].format(order.typeof)
                self.view.set_statusbar(msg)
                c, r = self.model.search_dir(order)
                counter += c
                remaining += r
        msg = self.msg['done'].format(counter, remaining)
        self.view.set_statusbar(msg)
        self.write_config(orderlist)


def main():
    Controller()


if __name__ == '__main__':
    main()
