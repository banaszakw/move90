#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import controller
import model
import os
import shutil
#import sys
import unittest
from unittest import mock


def get_moved_files(fileslist):
    """Pomocnicza funkcja. `shutil.move`, gdy pomyślnie przenosi plik, zwraca
    `dst`. Taka lista to `move_values`. Funkcja z tej listy wyciaga nazwy
    plików.
    """
    moved_files = []
    for fp in fileslist:
        try:
            if os.path.splitext(fp)[1]:
                # print(os.path.split(fp)[1])
                moved_files.append(os.path.split(fp)[1])
        except (TypeError, AttributeError):  # TypeError > Python 3.5
            pass
    return sorted(moved_files)


def make_normpathlist_gener(alist):
    """Pomocniczna funkcja, przeznaczona dla generatora sciezek. Dla obydwu 
    elemenetw każdej krotki na liscie wywołuje funkcję `os.path.normpath_list`. 
    Zwraca: List[Tuple[str, str]].
    alist -- List[Tuple[str, str]]
    """
    return [(os.path.normpath(r),
             os.path.normpath(d)) for r, d in alist]


def make_normpathlist_mock(alist):
    """Pomocniczna funkcja, przeznaczona dla `mock.call`. Każdą krotke na liscie
    opakowuje funckją mock.call. Zwraca: List[mock.call(Tuple[str, str])].
    alist -- List[Tuple[str, str]]
    """
    return [mock.call(*t) for t in make_normpathlist_gener(alist)]


def make_normpathlist(alist):
    """Pomocnicza funkcja. Dla każdego elementu listy wywołuje funkcję 
    `os.norm.path`, jeśli nie da się, zostawia ten element. Zwraca: List[str]
    alist: List[str] 
    """
    normpath_list = []
    for p in alist:
        try:
            p = os.path.normpath(p)
        except (AttributeError, TypeError):
            pass
        normpath_list.append(p)
    return normpath_list


class TestModel(unittest.TestCase):

    def setUp(self):
        only_num = controller.Controller().only_num
        num_brand = controller.Controller().num_brand
        brand_dict = controller.Controller().brand_dict
        self.m = model.Model(only_num, num_brand, brand_dict)

    def test_reformat_dirname(self):
        dirnames = [('VRL011966_VW11', 'VRL011966', 'in'),
                    ('OC0000673_Audi', 'OC0000673-Audi_21', 'odis'),
                    ('OC0000176_VW51', 'OC0000176-VW_51', 'ODIS'),
                    ('OC0000314_Seat', 'OC0000314-Seat_41', 'Odis'),
                    ('12345_VW11', '12345', 'SLP'),
                    ('_wyslane', '', 'IN'),
                    ('__wyslane', '', 'IN'),
                    ('_wyslane', '-wyslane', 'ODIS'),
                    ('rozliczenia_dla_klienta', 'rozliczenia', 'ISLP'),
                    ('rozliczenia_dla_klienta', 'rozliczenia-dla', 'ODIS'),
                    ('01_poczatek', '01-poczatek', 'KDVDB'),
                    ('90_koniec', '90', 'IN')]
        for inp, out, brand in dirnames:
            with self.subTest(inp=inp, out=out, brand=brand):
                result = self.m.reformat_dirname(inp, brand)
                self.assertEqual(result, out)

    def test_get_dir_path(self):
        oswalk = [[('ID66100_GOCAT_ODIS_VW_02/', ['OC0000721_VW11'], []),
                   ('ID66100_GOCAT_ODIS_VW_02/OC0000721_VW11', ['01_poczatek', 'rozliczenia_dla_klienta', '90_koniec'],
                    []),
                   ('ID66100_GOCAT_ODIS_VW_02/OC0000721_VW11/01_poczatek', [], ['test.pdf']),
                   ('ID66100_GOCAT_ODIS_VW_02/OC0000721_VW11/rozliczenia_dla_klienta', [], []),
                   ('ID66100_GOCAT_ODIS_VW_02/OC0000721_VW11/90_koniec', [], [])],
                  [('ID66103_GOCAT_ODIS_AUDI_02/', ['OC0000540_Audi'], []),
                   ('ID66103_GOCAT_ODIS_AUDI_02/OC0000540_Audi',
                    ['01_poczatek', 'rozliczenia_dla_klienta', '90_koniec'], []),
                   ('ID66103_GOCAT_ODIS_AUDI_02/OC0000540_Audi/01_poczatek', [], ['test.pdf']),
                   ('ID66103_GOCAT_ODIS_AUDI_02/OC0000540_Audi/rozliczenia_dla_klienta', [], []),
                   ('ID66103_GOCAT_ODIS_AUDI_02/OC0000540_Audi/90_koniec', [], [])]]
        dir_path_list = ['ID66100_GOCAT_ODIS_VW_02', 'ID66103_GOCAT_ODIS_AUDI_02']
        model.os.walk = mock.Mock(side_effect=oswalk)
        out = [('ID66100_GOCAT_ODIS_VW_02/', 'OC0000721_VW11'),
               ('ID66100_GOCAT_ODIS_VW_02/OC0000721_VW11', '01_poczatek'),
               ('ID66100_GOCAT_ODIS_VW_02/OC0000721_VW11', '90_koniec'),
               ('ID66100_GOCAT_ODIS_VW_02/OC0000721_VW11', 'rozliczenia_dla_klienta'),
               ('ID66103_GOCAT_ODIS_AUDI_02/', 'OC0000540_Audi'),
               ('ID66103_GOCAT_ODIS_AUDI_02/OC0000540_Audi', '01_poczatek'),
               ('ID66103_GOCAT_ODIS_AUDI_02/OC0000540_Audi', '90_koniec'),
               ('ID66103_GOCAT_ODIS_AUDI_02/OC0000540_Audi', 'rozliczenia_dla_klienta')]
        result = self.m.get_dir_path(dir_path_list)
        self.assertListEqual(list(result), out)

    def test_get_match_fpath_0(self):
        oswalk = [(os.path.normpath('/_wyslane/ODIS'), [], ['OC0000515-VW_11_test.txt', 'OC0000499-VW_12_test.txt'])]
        srcdir = '/_wyslane/ODIS'
        dirname = 'OC0000515-VW_11'
        model.os.walk = mock.Mock(return_value=oswalk)
        model.os.path.isfile = mock.Mock(return_value=True)
        out = os.path.normpath('/_wyslane/ODIS/OC0000515-VW_11_test.txt')
        result = os.path.normpath(self.m.get_match_fpath(srcdir, dirname))
        self.assertEqual(result, out)

    def test_get_match_fpath_1(self):
        oswalk = [(os.path.normpath('/_wyslane/IN'), [], ['VRL011999-test.txt', 'VRL011966-test.txt'])]
        srcdir = '/_wyslane/IN'
        dirname = 'VRL011999'
        model.os.walk = mock.Mock(return_value=oswalk)
        model.os.path.isfile = mock.Mock(return_value=True)
        out = os.path.normpath('/_wyslane/IN/VRL011999-test.txt')
        result = os.path.normpath(self.m.get_match_fpath(srcdir, dirname))
        self.assertEqual(result, out)

    def test_get_match_fpath_2(self):
        oswalk = [(os.path.normpath('/_wyslane/IN'), [], ['VRL011999-test.txt', 'VRL011966-test.txt'])]
        srcdir = '/_wyslane/IN'
        dirname = 'VRL020045'
        model.os.walk = mock.Mock(return_value=oswalk)
        model.os.path.isfile = mock.Mock(return_value=True)
        result = self.m.get_match_fpath(srcdir, dirname)
        self.assertIsNone(result)

    @unittest.skip("Funkcja już nieużywana")
    def test_verify_pathlist(self):
        with mock.patch('model.os.path.isdir') as isdir:
            pathlist = ['/home/dir0', '/home/file0', '/home/dir1']
            isdir.side_effect = [True, False, True]
            result = self.m.verify_pathlist(pathlist)
#            print(result)
            self.assertTrue(result, True)

    def test_moveto90_0(self):
        self.m.controller = mock.Mock()
        model.shutil.move = mock.Mock()
        src, dst = '/foo', '/bar'
        result = self.m.moveto90(src, dst)
        model.shutil.move.assert_called_once_with(src, dst)
        self.assertFalse(self.m.controller.logger.error.called)
        self.assertEqual(result, 1)

    def test_moveto90_1(self):
        self.m.controller = mock.Mock()
        model.shutil.move = mock.Mock(side_effect=FileNotFoundError)
        src, dst = '/foo', '/bar'
        with self.assertRaises(FileNotFoundError):
            result = self.m.moveto90(src, dst)
            model.shutil.move.assert_called_once_with(src, dst)
            self.assertTrue(self.m.controller.logger.error.call_count == 1)
            self.assertEqual(result, 0)
            model.shutil.move(src, dst)

    def test_moveto90_2(self):
        self.m.controller = mock.Mock()
        model.shutil.move = mock.Mock(side_effect=shutil.Error)
        src, dst = '/foo', '/bar'
        with self.assertRaises(shutil.Error):
            result = self.m.moveto90(src, dst)
            model.shutil.move.assert_called_once_with(src, dst)
            self.assertTrue(self.m.controller.logger.error.call_count == 1)
            self.assertEqual(result, 0)
            model.shutil.move(src, dst)

    def test_moveto90_3(self):
        self.m.controller = mock.Mock()
        model.shutil.move = mock.Mock(side_effect=NotADirectoryError)
        src, dst = '/foo', '/bar'
        with self.assertRaises(NotADirectoryError):
            result = self.m.moveto90(src, dst)
            model.shutil.move.assert_called_once_with(src, dst)
            self.assertTrue(self.m.controller.logger.error.call_count == 1)
            self.assertEqual(result, 0)
            model.shutil.move(src, dst)

    def test_moveto90_4(self):
        self.m.controller = mock.Mock()
        model.shutil.move = mock.Mock(side_effect=IsADirectoryError)
        src, dst = '/foo', '/bar'
        with self.assertRaises(IsADirectoryError):
            result = self.m.moveto90(src, dst)
            model.shutil.move.assert_called_once_with(src, dst)
            self.assertTrue(self.m.controller.logger.error.call_count == 1)
            self.assertEqual(result, 0)
            model.shutil.move(src, dst)

    def test_search_dir_0(self):
        """W `srcdir` jest jeden plik ODIS. Zostaje przeniesiony. Nic nie
        zostaje w `srcdir`.
        """
        gener_paths = [
            ('GOCAT/VAS/ID66282_GOCAT_ODIS_VW_02/', 'OC0000515_VW11'),
            ('GOCAT/VAS/ID66282_GOCAT_ODIS_VW_02/OC0000515_VW11', '01_poczatek'),
            ('GOCAT/VAS/ID66282_GOCAT_ODIS_VW_02/OC0000515_VW11', '90_koniec'),
            ('GOCAT/VAS/ID66282_GOCAT_ODIS_VW_02/OC0000515_VW11', 'rozliczenia_dla_klienta'),
            ('GOCAT/VAS/ID66282_GOCAT_ODIS_VW_02/', 'OC0000721_VW11'),
            ('GOCAT/VAS/ID66282_GOCAT_ODIS_VW_02/OC0000721_VW11', '01_poczatek'),
            ('GOCAT/VAS/ID66282_GOCAT_ODIS_VW_02/OC0000721_VW11', '90_koniec'),
            ('GOCAT/VAS/ID66282_GOCAT_ODIS_VW_02/OC0000721_VW11', 'rozliczenia_dla_klienta')
        ]
#        mock_gener = iter([(os.path.normpath(r),
#                            os.path.normpath(d)) for r, d in gener_paths])
        mock_gener = iter(make_normpathlist_gener(gener_paths))
        mock_reformat = ['OC0000515-VW_11', '01-poczatek', '90-koniec', 'rozliczenia-dla',
                         'OC0000721-VW_11', '01-poczatek', '90-koniec', 'rozliczenia-dla']
        mock_match = ['', '', '', '',
                      os.path.normpath('_wyslane/ODIS/OC0000721-VW_11-test.sdlrpx'),
                      '', '', '']
        args = {'srcdir': [os.path.normpath('_wyslane/ODIS')],
                'dstdir': [os.path.normpath('GOCAT/AS/ID66282_GOCAT_ODIS_VW_02'),
                           '',
                           os.path.normpath('GOCAT/VAS/ID66285_GOCAT_ODIS_AUDI_01')],
                'active_dstdir': [True, False, False],
                'typeof': 'ODIS',
                'tosend': False}
        order_obj = mock.Mock(**args)
        self.m.get_dir_path = mock.Mock(return_value=mock_gener)
        self.m.reformat_dirname = mock.Mock(side_effect=mock_reformat)
        self.m.get_match_fpath = mock.Mock(side_effect=mock_match)
        self.m.moveto90 = mock.Mock(side_effect=[1])
        self.m.get_remaining = mock.Mock(return_value=12)
        with mock.patch('model.os.listdir') as oslistdir:
            # indeks gener_paths ścieżki, która pasuje do szukanego pliku ==
            # długość oslistdir.side_effect + []
            oslistdir.side_effect = [['a.sdlrpx'], ['a.sdlrpx'], ['a.sdlrpx'],
                                     ['a.sdlrpx'], ['a.sdlrpx'], []]
            result = self.m.search_dir(order_obj)
            self.assertTrue(self.m.moveto90.call_count == 1)
            self.assertEqual(self.m.counter, 1)
            self.assertEqual(result[0], 1)
            self.assertEqual(result[1], 12)
            calls_moveto90 = [mock.call(os.path.normpath('_wyslane/ODIS/OC0000721-VW_11-test.sdlrpx'),
                                        os.path.normpath('GOCAT/VAS/ID66282_GOCAT_ODIS_VW_02/OC0000721_VW11/90_koniec'))]
            self.m.moveto90.assert_has_calls(calls_moveto90)

    def test_search_dir_1(self):
        """ Dwa pliki IN do przeniesienia. """
        gener_paths = [
            ('GOCAT/IN_AUDI/2019-02/', '_wyslane'),
            ('GOCAT/IN_AUDI/2019-02/', 'ARL030011_Audi'),
            ('GOCAT/IN_AUDI/2019-02/', 'ARL030012_Audi'),
            ('GOCAT/IN_AUDI/2019-02/', 'ARL030013_Audi'),
            ('GOCAT/IN_AUDI/2019-02/ARL030011_Audi', '01_poczatek'),
            ('GOCAT/IN_AUDI/2019-02/ARL030011_Audi', '90_koniec'),
            ('GOCAT/IN_AUDI/2019-02/ARL030011_Audi', 'rozliczenia_dla_klienta'),
            ('GOCAT/IN_AUDI/2019-02/ARL030012_Audi', '01_poczatek'),
            ('GOCAT/IN_AUDI/2019-02/ARL030012_Audi', '90_koniec'),
            ('GOCAT/IN_AUDI/2019-02/ARL030012_Audi', 'rozliczenia_dla_klienta'),
            ('GOCAT/IN_AUDI/2019-02/ARL030013_Audi', '01_poczatek'),
            ('GOCAT/IN_AUDI/2019-02/ARL030013_Audi', '90_koniec'),
            ('GOCAT/IN_AUDI/2019-02/ARL030013_Audi', 'rozliczenia_dla_klienta')
        ]
#        mock_gener = iter([(os.path.normpath(r),
#                            os.path.normpath(d)) for r, d in gener_paths])
        mock_gener = iter(make_normpathlist_gener(gener_paths))
        mock_reformat = ['', 'ARL030011', 'ARL030012', 'ARL030013',
                         '01', '90', 'rozliczenia', '01', '90', 'rozliczenia', '01', '90', 'rozliczenia']
        mock_match = [os.path.normpath('_wyslane/IN/ARL030011-test.sdlrpx'),
                      None,
                      os.path.normpath('_wyslane/IN/ARL030013-test.sdlrpx'),
                      None, None, None, None, None, None, None, None, None]
        args = {'srcdir': [os.path.normpath('_wyslane/IN')],
                'typeof': 'IN',
                'tosend': True,
                'dstdir': [os.path.normpath('GOCAT/IN_AUDI/2019-02/'),
                           os.path.normpath('GOCAT/IN_SEAT/2019-02/'),
                           os.path.normpath('GOCAT/IN_VW/2019-02/')],
                'active_dstdir': [True, False, False]}
        order_obj = mock.Mock(**args)
        self.m.get_dir_path = mock.Mock(return_value=mock_gener)
        self.m.reformat_dirname = mock.Mock(side_effect=mock_reformat)
        self.m.get_match_fpath = mock.Mock(side_effect=mock_match)
        self.m.moveto90 = mock.Mock(side_effect=[1, 1, 1, 1])
        self.m.get_remaining = mock.Mock(return_value=0)
        with mock.patch('model.os.listdir') as oslistdir:
            # indeks gener_paths ścieżki, która pasuje do szukanego pliku ==
            # długość oslistdir.side_effect + []
            oslistdir.side_effect = [['a.sdlrpx'], ['a.sdlrpx'], ['a.sdlrpx'],
                                     ['a.sdlrpx'], ['a.sdlrpx'], []]
            result = self.m.search_dir(order_obj)
            self.assertTrue(self.m.moveto90.call_count == 4)
            self.assertEqual(self.m.counter, 2)
            self.assertEqual(result[0], 2)
            self.assertEqual(result[1], 0)
            calls_moveto90 = [
                mock.call(os.path.normpath('_wyslane/IN/ARL030011-test.sdlrpx'),
                          os.path.normpath('GOCAT/IN_AUDI/2019-02/ARL030011_Audi/90_koniec')),
                mock.call(os.path.normpath('GOCAT/IN_AUDI/2019-02/ARL030011_Audi'),
                          os.path.normpath('GOCAT/IN_AUDI/2019-02/_wyslane')),
                mock.call(os.path.normpath('_wyslane/IN/ARL030013-test.sdlrpx'),
                          os.path.normpath('GOCAT/IN_AUDI/2019-02/ARL030013_Audi/90_koniec')),
                mock.call(os.path.normpath('GOCAT/IN_AUDI/2019-02/ARL030013_Audi'),
                          os.path.normpath('GOCAT/IN_AUDI/2019-02/_wyslane'))]
            self.m.moveto90.assert_has_calls(calls_moveto90)
    # @unittest.skip("test_search_dir - na razie pomijam")
    def test_search_dir_3(self):
        """ W katalogu `src` jest 16 plików. Przeniesonych zostaje 9, zostaje 7
        (6 nie pasuje do żadnego katalogu, 1 nie zostaje przeniesiony, ponieważ
        w `dst` już znajduje się taki plik; dostaje więc wywołany wyjatek).
        Część katalogów zostaje przeniesiona do `_wyslane`, a część już tam
        jest. """
        gener_paths = [
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/', 'ARL006169_Audi'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/', 'ARL006175_Audi'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/', 'ARL006177_Audi'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/', '_wyslane'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/ARL006169_Audi', '01_poczatek'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/ARL006169_Audi', '02_przygotowanie'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/ARL006169_Audi', '90_koniec'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/ARL006169_Audi', 'rozliczenia_dla_klienta'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/ARL006169_Audi/02_przygotowanie', '01_sdlxliff_orig'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/ARL006169_Audi/02_przygotowanie', '02_sdlxliff_trans'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/ARL006175_Audi', '01_poczatek'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/ARL006175_Audi', '02_przygotowanie'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/ARL006175_Audi', '90_koniec'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/ARL006175_Audi', 'rozliczenia_dla_klienta'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/ARL006175_Audi/02_przygotowanie', '01_sdlxliff_orig'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/ARL006175_Audi/02_przygotowanie', '02_sdlxliff_trans'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/ARL006177_Audi', '01_poczatek'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/ARL006177_Audi', '02_przygotowanie'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/ARL006177_Audi', '90_koniec'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/ARL006177_Audi', 'rozliczenia_dla_klienta'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/ARL006177_Audi/02_przygotowanie', '01_sdlxliff_orig'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/ARL006177_Audi/02_przygotowanie', '02_sdlxliff_trans'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane', 'AIGG000975_Audi'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane', 'AKI000262_Audi'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane', 'ARL005849_Audi'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane/ARL005849_Audi', '01_poczatek'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane/ARL005849_Audi', '02_przygotowanie'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane/ARL005849_Audi', '90_koniec'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane/ARL005849_Audi', 'rozliczenia_dla_klienta'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane/ARL005849_Audi/02_przygotowanie', '01_sdlxliff_orig'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane/ARL005849_Audi/02_przygotowanie', '02_sdlxliff_trans'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane/AKI000262_Audi',  '01_poczatek'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane/AKI000262_Audi',  '02_przygotowanie'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane/AKI000262_Audi',  '90_koniec'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane/AKI000262_Audi',  'rozliczenia_dla_klienta'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane/AKI000262_Audi/02_przygotowanie', '01_sdlxliff_orig'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane/AKI000262_Audi/02_przygotowanie', '02_sdlxliff_trans'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane/AIGG000975_Audi', '01_poczatek'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane/AIGG000975_Audi', '02_przygotowanie'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane/AIGG000975_Audi', '90_koniec'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane/AIGG000975_Audi', 'rozliczenia_dla_klienta'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane/AIGG000975_Audi/02_przygotowanie', '01_sdlxliff_orig'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane/AIGG000975_Audi/02_przygotowanie',
                '02_sdlxliff_trans'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/', 'VAU002468_VW11'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/', 'VKI000434_VW12'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/', 'VRL012606_VW66'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/', '_wyslane'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/VRL012606_VW66', '01_poczatek'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/VRL012606_VW66', '02_przygotowanie'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/VRL012606_VW66', '90_koniec'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/VRL012606_VW66', 'rozliczenia_dla_klienta'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/VRL012606_VW66/02_przygotowanie', '01_sdlxliff_orig'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/VRL012606_VW66/02_przygotowanie', '02_sdlxliff_trans'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/VKI000434_VW12', '01_poczatek'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/VKI000434_VW12', '02_przygotowanie'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/VKI000434_VW12', '90_koniec'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/VKI000434_VW12', 'rozliczenia_dla_klienta'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/VKI000434_VW12/02_przygotowanie', '01_sdlxliff_orig'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/VKI000434_VW12/02_przygotowanie', '02_sdlxliff_trans'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/VAU002468_VW11', '01_poczatek'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/VAU002468_VW11', '02_przygotowanie'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/VAU002468_VW11', '90_koniec'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/VAU002468_VW11', 'rozliczenia_dla_klienta'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/VAU002468_VW11/02_przygotowanie',
             '01_sdlxliff_orig'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/VAU002468_VW11/02_przygotowanie',
             '02_sdlxliff_trans'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane', 'VIGG001224_VW12'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane', 'VKAH000006_VW11'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane', 'VRL010886_VW11'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VKAH000006_VW11',
             '01_poczatek'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VKAH000006_VW11',
             '02_przygotowanie'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VKAH000006_VW11',
             '90_koniec'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VKAH000006_VW11',
             'rozliczenia_dla_klienta'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VKAH000006_VW11/02_przygotowanie',
                '01_sdlxliff_orig'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VKAH000006_VW11/02_przygotowanie',
                '02_sdlxliff_trans'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VIGG001224_VW12',
             '01_poczatek'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VIGG001224_VW12',
             '02_przygotowanie'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VIGG001224_VW12',
             '90_koniec'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VIGG001224_VW12',
             'rozliczenia_dla_klienta'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VIGG001224_VW12/02_przygotowanie',
                '01_sdlxliff_orig'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VIGG001224_VW12/02_przygotowanie',
                '02_sdlxliff_trans'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VRL010886_VW11',
             '01_poczatek'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VRL010886_VW11',
             '02_przygotowanie'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VRL010886_VW11', '90_koniec'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VRL010886_VW11',
             'rozliczenia_dla_klienta'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VRL010886_VW11/02_przygotowanie',
                '01_sdlxliff_orig'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VRL010886_VW11/02_przygotowanie',
                '02_sdlxliff_trans')]
#        mock_gener = iter([(os.path.normpath(r),
#                            os.path.normpath(d)) for r, d in gener_paths])
        mock_gener = iter(make_normpathlist_gener(gener_paths))
        mock_reformat = ['ARL006169', 'ARL006175', 'ARL006177', '', '01', '02', '90', 'rozliczenia', '01', '02', '01',
                         '02', '90', 'rozliczenia', '01', '02', '01', '02', '90', 'rozliczenia', '01', '02',
                         'AIGG000975', 'AKI000262', 'ARL005849', '01', '02', '90', 'rozliczenia', '01', '02', '01',
                         '02', '90', 'rozliczenia', '01', '02', '01', '02', '90', 'rozliczenia', '01', '02',
                         'VAU002468', 'VKI000434', 'VRL012606', '', '01', '02', '90', 'rozliczenia', '01', '02', '01',
                         '02', '90', 'rozliczenia', '01', '02', '01', '02', '90', 'rozliczenia', '01', '02',
                         'VIGG001224', 'VKAH000006', 'VRL010886', '01', '02', '90', 'rozliczenia', '01', '02', '01',
                         '02', '90', 'rozliczenia', '01', '02', '01', '02', '90', 'rozliczenia', '01', '02']
        match_paths = [
            '/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/IN/ARL006169-V7.0_Audi R8_2007_Ratgeber Räder, Reifen_1991184137.sdlrpx',
            None,
            '/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/IN/ARL006177-V4.0_Audi A6_2019_Karosserie- Montagearbeiten Innen_1988441170.sdlrpx',
            None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
            '/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/IN/AIGG000975-V22.0_Audi A3_2013_1988040555.sdlrpx',
            '/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/IN/AKI000262-V9.0_Audi A1_2011_1986247817.sdlrpx',
            '/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/IN/ARL005849-V3.0_Audi A8_2018_Fahrwerk Front- und Allradantrieb_1986673800.sdlrpx',
            None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
            '/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/IN/VAU002468-V2.0_Golf Variant_2017_1 Golf Variant 2017 - Diesel_1994818472.sdlrpx',
            None,
            '/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/IN/VRL012606-V2.0_Beetle_2012_4-Zyl. Dieselmotor (2,0 l-Motor, Common Rail, Generation II)_1996149359.sdlrpx',
            None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
            '/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/IN/VIGG001224-V3.0_e-Crafter_2019_1990154803.sdlrpx',
            '/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/IN/VKAH000006-V5.0_1989340873.sdlrpx',
            '/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/IN/VRL010886-V1.0_Golf_2017_4-Zyl. Einspritzmotor (1,5 l, Erdgas, 4V, EA 211 EVO, Turbolader)_1988987112.sdlrpx',
            None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
        mock_match = make_normpathlist(match_paths)
        args = {'typeof': 'IN',
                'srcdir': [os.path.normpath('/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/IN/')],
                'dstdir': [os.path.normpath('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/'),
                           os.path.normpath('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_SEAT/2019-01/'),
                           os.path.normpath('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/')],
                'active_dstdir': [True, False, True],
                'tosend': True,
                'tosearch': True}
        order_obj = mock.Mock(**args)
        move_call_paths = [('/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/IN/ARL006169-V7.0_Audi R8_2007_Ratgeber Räder, Reifen_1991184137.sdlrpx',
            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/ARL006169_Audi/90_koniec'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/ARL006169_Audi',
             '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/IN/ARL006177-V4.0_Audi A6_2019_Karosserie- Montagearbeiten Innen_1988441170.sdlrpx',
             '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/ARL006177_Audi/90_koniec'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/ARL006177_Audi',
             '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/IN/AIGG000975-V22.0_Audi A3_2013_1988040555.sdlrpx',
             '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane/AIGG000975_Audi/90_koniec'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/IN/AKI000262-V9.0_Audi A1_2011_1986247817.sdlrpx',
             '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane/AKI000262_Audi/90_koniec'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/IN/ARL005849-V3.0_Audi A8_2018_Fahrwerk Front- und Allradantrieb_1986673800.sdlrpx',
             '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane/ARL005849_Audi/90_koniec'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/IN/VAU002468-V2.0_Golf Variant_2017_1 Golf Variant 2017 - Diesel_1994818472.sdlrpx',
             '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/VAU002468_VW11/90_koniec'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/VAU002468_VW11',
             '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/IN/VRL012606-V2.0_Beetle_2012_4-Zyl. Dieselmotor (2,0 l-Motor, Common Rail, Generation II)_1996149359.sdlrpx',
             '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/VRL012606_VW66/90_koniec'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/VRL012606_VW66',
             '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/IN/VIGG001224-V3.0_e-Crafter_2019_1990154803.sdlrpx',
             '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VIGG001224_VW12/90_koniec'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/IN/VKAH000006-V5.0_1989340873.sdlrpx',
             '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VKAH000006_VW11/90_koniec'),
            ('/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/IN/VRL010886-V1.0_Golf_2017_4-Zyl. Einspritzmotor (1,5 l, Erdgas, 4V, EA 211 EVO, Turbolader)_1988987112.sdlrpx',
             '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VRL010886_VW11/90_koniec')]
#        move_calls = [mock.call(a, b) for a, b in move_call_paths]
        move_calls = make_normpathlist_mock(move_call_paths)              
        move_paths = [
            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/ARL006169_Audi/90_koniec/ARL006169-V7.0_Audi R8_2007_Ratgeber Räder, Reifen_1991184137.sdlrpx',
            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane/ARL006169_Audi',
            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/ARL006177_Audi/90_koniec/ARL006177-V4.0_Audi A6_2019_Karosserie- Montagearbeiten Innen_1988441170.sdlrpx',
            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane/ARL006177_Audi',
            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane/AIGG000975_Audi/90_koniec/AIGG000975-V22.0_Audi A3_2013_1988040555.sdlrpx',
            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_AUDI/2019-01/_wyslane/ARL005849_Audi/90_koniec/ARL005849-V3.0_Audi A8_2018_Fahrwerk Front- und Allradantrieb_1986673800.sdlrpx',
            shutil.Error,  # przechwycony przez obsługę błędów w Model
            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/VAU002468_VW11/90_koniec/VAU002468-V2.0_Golf Variant_2017_1 Golf Variant 2017 - Diesel_1994818472.sdlrpx',
            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VAU002468_VW11',
            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/VRL012606_VW66/90_koniec/VRL012606-V2.0_Beetle_2012_4-Zyl. Dieselmotor (2,0 l-Motor, Common Rail, Generation II)_1996149359.sdlrpx',
            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VRL012606_VW66',
            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VIGG001224_VW12/90_koniec/VIGG001224-V3.0_e-Crafter_2019_1990154803.sdlrpx',
            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VKAH000006_VW11/90_koniec/VKAH000006-V5.0_1989340873.sdlrpx',
            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/IN_VW/2019-01/_wyslane/VRL010886_VW11/90_koniec/VRL010886-V1.0_Golf_2017_4-Zyl. Einspritzmotor (1,5 l, Erdgas, 4V, EA 211 EVO, Turbolader)_1988987112.sdlrpx']
        move_values = make_normpathlist(move_paths)
        srcdir_oswalk = [(os.path.normpath('/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/IN/'), [],
                          ['ERL003928-V1.0_Arona_2018_Kraftstoffversorgung - Erdgasmotoren_1996005923.sdlrpx',
                           'VRL010886-V1.0_Golf_2017_4-Zyl. Einspritzmotor (1,5 l, Erdgas, 4V, EA 211 EVO, Turbolader)_1988987112.sdlrpx',
                           'ERL003876-V17.0_Alhambra_2011_Karosserie, Montagearbeiten außen_1996068564.sdlrpx',
                           'ERL004010-V8.0_Alhambra_2016_4-Zylinder Benzinmotor (2,0 l Direkteinspritzung, 4 V, Abgasturbolader, Kettentri_1996047386.sdlrpx',
                           'VKAH000006-V5.0_1989340873.sdlrpx',
                           'AKI000262-V9.0_Audi A1_2011_1986247817.sdlrpx',
                           'AIGG000975-V22.0_Audi A3_2013_1988040555.sdlrpx',
                           'VIGG001224-V3.0_e-Crafter_2019_1990154803.sdlrpx',
                           'VRL999999-V1.0_powinienem_zostac.sdlrpx',
                           'VRL012606-V2.0_Beetle_2012_4-Zyl. Dieselmotor (2,0 l-Motor, Common Rail, Generation II)_1996149359.sdlrpx',
                           'ERL003963-V5.0_Arona_2018_3 Zylinder Benzin (1,0 l Erdgas, 4 V, EA211)_1996058347.sdlrpx',
                           'EIGG000443-V14.0_Arona_2018_1996053608.sdlrpx',
                           'ARL005849-V3.0_Audi A8_2018_Fahrwerk Front- und Allradantrieb_1986673800.sdlrpx',
                           'ARL006177-V4.0_Audi A6_2019_Karosserie- Montagearbeiten Innen_1988441170.sdlrpx',
                           'VAU002468-V2.0_Golf Variant_2017_1 Golf Variant 2017 - Diesel_1994818472.sdlrpx',
                           'ARL006169-V7.0_Audi R8_2007_Ratgeber Räder, Reifen_1991184137.sdlrpx'])]
        srcdir_start = srcdir_oswalk[0][2]
        srcdir_end = ['ERL003928-V1.0_Arona_2018_Kraftstoffversorgung - Erdgasmotoren_1996005923.sdlrpx',
                      'ERL003876-V17.0_Alhambra_2011_Karosserie, Montagearbeiten außen_1996068564.sdlrpx',
                      'ERL004010-V8.0_Alhambra_2016_4-Zylinder Benzinmotor (2,0 l Direkteinspritzung, 4 V, Abgasturbolader, Kettentri_1996047386.sdlrpx',
                      'AKI000262-V9.0_Audi A1_2011_1986247817.sdlrpx',
                      'VRL999999-V1.0_powinienem_zostac.sdlrpx',
                      'ERL003963-V5.0_Arona_2018_3 Zylinder Benzin (1,0 l Erdgas, 4 V, EA211)_1996058347.sdlrpx',
                      'EIGG000443-V14.0_Arona_2018_1996053608.sdlrpx']
        moved_expected = [
            'VRL010886-V1.0_Golf_2017_4-Zyl. Einspritzmotor (1,5 l, Erdgas, 4V, EA 211 EVO, Turbolader)_1988987112.sdlrpx',
            'VKAH000006-V5.0_1989340873.sdlrpx',
            'AIGG000975-V22.0_Audi A3_2013_1988040555.sdlrpx',
            'VIGG001224-V3.0_e-Crafter_2019_1990154803.sdlrpx',
            'VRL012606-V2.0_Beetle_2012_4-Zyl. Dieselmotor (2,0 l-Motor, Common Rail, Generation II)_1996149359.sdlrpx',
            'ARL005849-V3.0_Audi A8_2018_Fahrwerk Front- und Allradantrieb_1986673800.sdlrpx',
            'ARL006177-V4.0_Audi A6_2019_Karosserie- Montagearbeiten Innen_1988441170.sdlrpx',
            'VAU002468-V2.0_Golf Variant_2017_1 Golf Variant 2017 - Diesel_1994818472.sdlrpx',
            'ARL006169-V7.0_Audi R8_2007_Ratgeber Räder, Reifen_1991184137.sdlrpx']
        moved_real = get_moved_files(move_values)
        self.m.controller = mock.Mock()
        model.shutil.move = mock.Mock(side_effect=move_values)
        self.m.get_dir_path = mock.Mock(return_value=mock_gener)
        self.m.reformat_dirname = mock.Mock(side_effect=mock_reformat)
        self.m.get_match_fpath = mock.Mock(side_effect=mock_match)
        self.m.get_remaining = mock.Mock(return_value=len(srcdir_end))
        with mock.patch('model.os.listdir') as oslistdir:
            # indeks gener_paths ścieżki, która pasuje do szukanego pliku ==
            # długość oslistdir.side_effect + []
            oslistdir.side_effect = [['a.sdlrpx']] * 87 + [[]]
            # w katalogu srcdir zostaną pliki, więc pętla
            # while os.listdir(srcdir) będzie działać do wyczerpania generatora,
            # a nie do stanu os.listdir(srcdir) == []
            result = self.m.search_dir(order_obj)
            self.assertTrue(self.m.controller.logger.error.call_count == 1)
            model.shutil.move.assert_has_calls(move_calls)
            self.assertListEqual(move_calls, model.shutil.move.call_args_list)
            self.assertListEqual(sorted(moved_expected), moved_real)
            self.assertListEqual(sorted(srcdir_start), sorted(srcdir_end + moved_real))
            self.assertEqual(result[0], len(moved_expected))
            self.assertEqual(result[1], len(srcdir_end))

    # @unittest.skip("test_search_dir - na razie pomijam")
    def test_search_dir_4(self):
        gener_paths = [
            ('/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/', '00000_Audi'),
            ('/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/', '13077_Audi'),
            ('/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/', '13088_Audi'),
            ('/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/13077_Audi', '01_poczatek'),
            ('/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/13077_Audi', '90_koniec'),
            ('/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/13077_Audi', 'rozliczenia_dla_klienta'),
            ('/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/00000_Audi', '01_poczatek'),
            ('/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/00000_Audi', '90_koniec'),
            ('/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/00000_Audi', 'rozliczenia_dla_klienta'),
            ('/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/13088_Audi', '01_poczatek'),
            ('/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/13088_Audi', '90_koniec'),
            ('/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/13088_Audi', 'rozliczenia_dla_klienta'),
            ('/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/', '13060_VW11'),
            ('/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/', '13181_SLP-VW11'),
            ('/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/13060_VW11', '01_poczatek'),
            ('/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/13060_VW11', '10_tlumaczenie'),
            ('/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/13060_VW11', '90_koniec'),
            ('/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/13060_VW11', 'rozliczenia_dla_klienta'),
            ('/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/13181_SLP-VW11', '01_poczatek'),
            ('/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/13181_SLP-VW11', '10_tlumaczenie'),
            ('/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/13181_SLP-VW11', '90_koniec'),
            ('/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/13181_SLP-VW11',  'rozliczenie_dla_klienta')]
        mock_gener = iter(make_normpathlist_gener(gener_paths))
        mock_reformat = []
        match_paths = [None,
                       '/_do_wyslania_GOCAT/SLP/13077-Audi_Etron_2019_TM3_1988116091.sdlrpx',
                       '/_do_wyslania_GOCAT/SLP/13088-Audi_A5_2017_TM11_1988416399.sdlrpx',
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       '/_do_wyslania_GOCAT/SLP/13060-SLP Dezember_1986901079.sdlrpx',
                       '/_do_wyslania_GOCAT/SLP/13181-SLP Dezember Teil 2_1991424788.sdlrpx',
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       None]
        mock_match = make_normpathlist(match_paths)
        args = {'typeof': 'SLP',
                'srcdir': [os.path.normpath('/_do_wyslania_GOCAT/SLP/')],
                'dstdir': ['',
                           os.path.normpath('/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/'),
                           os.path.normpath('/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/')],
                'active_dstdir': [False, True, True],
                'tosend': False,
                'tosearch': True}
        order_obj = mock.Mock(**args)
        move_call_paths = [('/_do_wyslania_GOCAT/SLP/13077-Audi_Etron_2019_TM3_1988116091.sdlrpx',
                            '/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/13077_Audi/90_koniec'),
                           ('/_do_wyslania_GOCAT/SLP/13088-Audi_A5_2017_TM11_1988416399.sdlrpx',
                            '/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/13088_Audi/90_koniec'),
                           ('/_do_wyslania_GOCAT/SLP/13060-SLP Dezember_1986901079.sdlrpx',
                            '/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/13060_VW11/90_koniec'),
                           ('/_do_wyslania_GOCAT/SLP/13181-SLP Dezember Teil 2_1991424788.sdlrpx',
                            '/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/13181_SLP-VW11/90_koniec')]
        move_calls = make_normpathlist_mock(move_call_paths) 
        move_paths = [
            '/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/13077_Audi/90_koniec/13077-Audi_Etron_2019_TM3_1988116091.sdlrpx',
            '/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/13088_Audi/90_koniec/13088-Audi_A5_2017_TM11_1988416399.sdlrpx',
            '/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/13060_VW11/90_koniec/13060-SLP Dezember_1986901079.sdlrpx',
            '/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/13181_SLP-VW11/90_koniec/13181-SLP Dezember Teil 2_1991424788.sdlrpx']
        move_values = make_normpathlist(move_paths)
        srcdir_oswalk = [
            (os.path.normpath('/_do_wyslania_GOCAT/SLP/'), ['test'],
             ['13181-SLP Dezember Teil 2_1991424788.sdlrpx', '13060-SLP Dezember_1986901079.sdlrpx',
              '13077-Audi_Etron_2019_TM3_1988116091.sdlrpx', '13088-Audi_A5_2017_TM11_1988416399.sdlrpx']),
            (os.path.normpath('/_do_wyslania_GOCAT/SLP/test'), [], ['13077-Audi_Etron_2019_TM3_1988116091.sdlrpx'])]
        srcdir_start = srcdir_oswalk[0][2]
        srcdir_end = []
        moved_expected = ['13181-SLP Dezember Teil 2_1991424788.sdlrpx', '13060-SLP Dezember_1986901079.sdlrpx',
                          '13077-Audi_Etron_2019_TM3_1988116091.sdlrpx', '13088-Audi_A5_2017_TM11_1988416399.sdlrpx']
        moved_real = get_moved_files(move_values)
        self.m.controller = mock.Mock()
        model.shutil.move = mock.Mock(side_effect=move_values)
        self.m.get_dir_path = mock.Mock(return_value=mock_gener)
        # self.m.reformat_dirname = mock.Mock(side_effect=mock_reformat)
        self.m.get_match_fpath = mock.Mock(side_effect=mock_match)
        self.m.get_remaining = mock.Mock(return_value=len(srcdir_end))
        with mock.patch('model.os.listdir') as oslistdir:
            # indeks gener_paths ścieżki, która pasuje do szukanego pliku ==
            # długość oslistdir.side_effect + []
            oslistdir.side_effect = [['a.sdlrpx']] * 14 + [[]]
            result = self.m.search_dir(order_obj)
            self.assertFalse(self.m.controller.logger.error.called)
            model.shutil.move.assert_has_calls(move_calls)
            self.assertListEqual(move_calls, model.shutil.move.call_args_list)
            self.assertListEqual(sorted(moved_expected), moved_real)
            self.assertListEqual(sorted(srcdir_start), sorted(srcdir_end + moved_real))
            self.assertEqual(result[0], len(moved_expected))
            self.assertEqual(result[1], len(srcdir_end))

    def test_get_remaining(self):
        with mock.patch('model.os.listdir') as oslistdir, mock.patch('model.os.path.isfile') as isfile:
            oslistdir.return_value = ['directory0', 'file0.sdlrpx', 'file1.sdlrpx', 'file2.sdlrpx']
            isfile.side_effect = [False, True, True, True]
            dirpath = '/home/test'
            result = self.m.get_remaining(dirpath)
            self.assertEqual(3, result)


if __name__ == '__main__':
    unittest.main()

    # def test_search_dir_4(self):
    #     mock_gener = iter([(
    #                        '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/',
    #                        '00000_Audi'),
    #                        (
    #                        '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/',
    #                        '13077_Audi'),
    #                        (
    #                        '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/',
    #                        '13088_Audi'),
    #                        (
    #                        '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/13077_Audi',
    #                        '01_poczatek'),
    #                        (
    #                        '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/13077_Audi',
    #                        '90_koniec'), (
    #                        '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/13077_Audi',
    #                        'rozliczenia_dla_klienta'), (
    #                            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/00000_Audi',
    #                            '01_poczatek'), (
    #                            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/00000_Audi',
    #                            '90_koniec'), (
    #                            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/00000_Audi',
    #                            'rozliczenia_dla_klienta'), (
    #                            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/13088_Audi',
    #                            '01_poczatek'), (
    #                            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/13088_Audi',
    #                            '90_koniec'), (
    #                            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/13088_Audi',
    #                            'rozliczenia_dla_klienta'), (
    #                            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/',
    #                            '13060_VW11'), (
    #                            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/',
    #                            '13181_SLP-VW11'), (
    #                            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/13060_VW11',
    #                            '01_poczatek'), (
    #                            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/13060_VW11',
    #                            '10_tlumaczenie'), (
    #                            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/13060_VW11',
    #                            '90_koniec'), (
    #                            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/13060_VW11',
    #                            'rozliczenia_dla_klienta'), (
    #                            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/13181_SLP-VW11',
    #                            '01_poczatek'), (
    #                            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/13181_SLP-VW11',
    #                            '10_tlumaczenie'), (
    #                            '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/13181_SLP-VW11',
    #                            '90_koniec'),
    #                        (
    #                        '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/13181_SLP-VW11',
    #                        'rozliczenie_dla_klienta')])
    #     mock_reformat = []
    #     mock_match = [None,
    #                   '/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/SLP/13077-Audi_Etron_2019_TM3_1988116091.sdlrpx',
    #                   '/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/SLP/13088-Audi_A5_2017_TM11_1988416399.sdlrpx',
    #                   None,
    #                   None,
    #                   None,
    #                   None,
    #                   None,
    #                   None,
    #                   None,
    #                   None,
    #                   None,
    #                   '/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/SLP/13060-SLP Dezember_1986901079.sdlrpx',
    #                   '/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/SLP/13181-SLP Dezember Teil 2_1991424788.sdlrpx',
    #                   None,
    #                   None,
    #                   None,
    #                   None,
    #                   None,
    #                   None,
    #                   None,
    #                   None]
    #     args = {'typeof': 'SLP',
    #             'srcdir': ['/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/SLP/'],
    #             'dstdir': ['',
    #                        '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/',
    #                        '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/'],
    #             'active_dstdir': [False, True, True],
    #             'tosend': False,
    #             'tosearch': True}
    #     order_obj = mock.Mock(**args)
    #     move_calls = [mock.call(
    #         '/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/SLP/13077-Audi_Etron_2019_TM3_1988116091.sdlrpx',
    #         '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/13077_Audi/90_koniec'),
    #         mock.call(
    #             '/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/SLP/13088-Audi_A5_2017_TM11_1988416399.sdlrpx',
    #             '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/13088_Audi/90_koniec'),
    #         mock.call(
    #             '/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/SLP/13060-SLP Dezember_1986901079.sdlrpx',
    #             '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/13060_VW11/90_koniec'),
    #         mock.call(
    #             '/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/SLP/13181-SLP Dezember Teil 2_1991424788.sdlrpx',
    #             '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/13181_SLP-VW11/90_koniec')]
    #     move_values = [
    #         '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/13077_Audi/90_koniec/13077-Audi_Etron_2019_TM3_1988116091.sdlrpx',
    #         '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_AUDI/ID66287_GOCAT_SLP_AUDI_01/13088_Audi/90_koniec/13088-Audi_A5_2017_TM11_1988416399.sdlrpx',
    #         '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/13060_VW11/90_koniec/13060-SLP Dezember_1986901079.sdlrpx',
    #         '/home/wojciech/PycharmProjects/Move90/gocat_tree/GOCAT/SLP_VW/2019/ID66286_GOCAT_SLP_VW_01/13181_SLP-VW11/90_koniec/13181-SLP Dezember Teil 2_1991424788.sdlrpx']
    #     srcdir_oswalk = [('/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/SLP/', ['test'],
    #                       ['13181-SLP Dezember Teil 2_1991424788.sdlrpx', '13060-SLP Dezember_1986901079.sdlrpx',
    #                        '13077-Audi_Etron_2019_TM3_1988116091.sdlrpx', '13088-Audi_A5_2017_TM11_1988416399.sdlrpx']),
    #                      ('/home/wojciech/PycharmProjects/Move90/gocat_tree/_do_wyslania_GOCAT/SLP/test', [],
    #                       ['13077-Audi_Etron_2019_TM3_1988116091.sdlrpx'])]
    #     srcdir_start = srcdir_oswalk[0][2]
    #     srcdir_end = []
    #     moved_expected = ['13181-SLP Dezember Teil 2_1991424788.sdlrpx', '13060-SLP Dezember_1986901079.sdlrpx',
    #                        '13077-Audi_Etron_2019_TM3_1988116091.sdlrpx', '13088-Audi_A5_2017_TM11_1988416399.sdlrpx']
    #     moved_real = get_moved_files(move_values)
    #     self.m.controller = mock.Mock()
    #     model.shutil.move = mock.Mock(side_effect=move_values)
    #     # model.shutil.move = mock.Mock()
    #     self.m.get_dir_path = mock.Mock(return_value=mock_gener)
    #     # self.m.reformat_dirname = mock.Mock(side_effect=mock_reformat)
    #     self.m.get_match_fpath = mock.Mock(side_effect=mock_match)
    #     self.m.get_remaining = mock.Mock(return_value=len(srcdir_end))
    #     result = self.m.search_dir(order_obj)
    #     self.assertFalse(self.m.controller.logger.error.called)
    #     model.shutil.move.assert_has_calls(move_calls)
    #     self.assertListEqual(move_calls, model.shutil.move.call_args_list)
    #     self.assertListEqual(sorted(moved_expected), moved_real)
    #     self.assertListEqual(sorted(srcdir_start), sorted(srcdir_end + moved_real))
    #     self.assertEqual(result[0], len(moved_expected))
    #     self.assertEqual(result[1], len(srcdir_end))
