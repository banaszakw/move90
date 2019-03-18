#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import itertools
import os
import shutil


class Model:

    def __init__(self, only_num, num_brand, brand_dict):
        self.only_num = only_num
        self.num_brand = num_brand
        self.brand_dict = brand_dict

    def get_tablist(self):
        return self.ORDER_NAMES

    def register(self, controller):
        """Register a controller to give callbacks to."""
        self.controller = controller

    def get_dir_path(self, dir_path_list):
        """Generuj pełne ścieżki katalogów dla danej listy ścieżek.
        Zwraca dwuelementowe krotki zawierające root i nazwę katalogu,
        np. ('ID66103_GOCAT_ODIS_AUDI_02/OC0000540_Audi', '01_poczatek').
        dir_path_list -- lista ścieżek, w którch będą szukane katalogi
        """
        for dir_dst in sorted(dir_path_list):
            for dst_root, dst_dirlist, dst_filelist in os.walk(dir_dst):
                for dir_ in sorted(dst_dirlist):
                    yield (dst_root, dir_)

    def reformat_dirname(self, dname, typeof):
        """Wez nazwe katalogu i w zaleznosci od typu zlecenia zwroc sam
        numer lub numer z nazwa marki, np. `OC0000673_Audi` zwróci: `OC0000673-Audi_21`.

        dname -- nazwa katalogu
        typeof -- typ zlecenia
        """
        num, brand, *_ = (dname + "_").split("_")
        if typeof.upper() in self.only_num:
            # return num or "False"
            return num
        elif typeof.upper() in self.num_brand:
            # return num + '-' + self.brand_dict.get(brand, brand) or "False"
            return num + '-' + self.brand_dict.get(brand, brand)

    def get_match_fpath(self, srcdir, dirname):
        """Generuje ściezki plików w katalogu `srcdir` i zwraca tę,
        która pasuje do wzorca - `dirname`.
        srcdir -- ściezka, katalog z plikami do przeniesienia, <string>
        dirname -- nazwa katalogu, przeformatowana już przez funkcję
        `reformat_dirname`
        """
        for root, dirlist, filelist in os.walk(srcdir):
            for f in sorted(filelist):
                fpath = os.path.join(root, f)
                if f.startswith(dirname) and os.path.isfile(fpath):
                    return fpath

    # def verify_pathlist(self, pathlist):  # nieużywana
    #     """ Sprawdza, czy ścieżki w liście ścieżek `pathlist` zawiera ścieżki do
    #     katalogów. Jeśli wszystkie ścieżki prowadzą do katalogów, zwraca tę
    #     listę. Jeśli choćby jedna ścieżka nie jest ścieżką katalogu, zwraca
    #     None.
    #     pathlist -- lista ścieżek
    #     """
    #     pathlist = list(filter(os.path.isdir, pathlist))
    #     if pathlist:
    #         return pathlist

    def moveto90(self, src, dst):
        """Przenosi plik `src` do katalgu `dst`.
        src -- ścieżka pliku
        dst -- ścieżka katalogu
        """
        try:
            shutil.move(src, dst)
            return 1
        except FileNotFoundError as err:
            self.controller.logger.error(err)
            return 0
        except shutil.Error as err:
            self.controller.logger.error(err)
            return 0
        except NotADirectoryError as err:
            self.controller.logger.error(err)
            return 0
        except IsADirectoryError as err:
            self.controller.logger.error(err)
            return 0

    def get_remaining(self, dirpath):
        """Podaje liczbę plików, które nie zostały przeniesione, czyli te,
        które pozostały w katalogu źródłowym, czyli `srcdir`.
        dirpath -- katalog źródłowy, czyli `srcdir`
        """
        files = 0
        for fname in os.listdir(dirpath):
            if os.path.isfile(os.path.join(dirpath, fname)):
                files += 1
        return files

    def search_dir(self, order_obj):
        self.counter = 0
        dstdir = list(itertools.compress(order_obj.dstdir, order_obj.active_dstdir))
        dstdir_gen = self.get_dir_path(dstdir)
        srcdir = order_obj.srcdir[0]  # jesli tylko jeden katalog srcdir
        # while True:
        while os.listdir(srcdir):
            try:
                dirpath, dirname = next(dstdir_gen)
            except StopIteration:
                break
            reformat_dir = self.reformat_dirname(dirname, order_obj.typeof)
            if not reformat_dir:
                continue
            match_fpath = self.get_match_fpath(srcdir, reformat_dir)
            if match_fpath:
                # src = os.path.join(srcdir, match_fpath)  # srcdir to tuple!
                dst = os.path.join(dirpath, dirname, '90_koniec')
                moved = self.moveto90(match_fpath, dst)
                self.counter += moved
                if moved and order_obj.tosend:
                    if os.path.basename(dirpath) != '_wyslane':
                        src = os.path.join(dirpath, dirname)
                        dst = os.path.join(dirpath, '_wyslane')
                        self.moveto90(src, dst)
                # break / continue
        return (self.counter, self.get_remaining(srcdir))


def main():
    only_num = ('Spam0', 'Spam1', 'Spam2')
    num_brand = ('Spam3', 'Spam4')
    brand_dict = {'Test0': 'Test_0',
                  'Test1': 'Test_1'}
    Model(only_num, num_brand, brand_dict)


if __name__ == '__main__':
    main()
