#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import controller
import io
import os
import sys
import unittest
from unittest import mock


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.c = controller.Controller()
        self.c.configfile = io.StringIO()
        self.c.config = configparser.ConfigParser()
        self.c.view = mock.Mock()
        self.c.logger = mock.Mock()

    def test_create_appdir(self):
        controller.os.makedirs = mock.Mock()
        self.c.appname = os.path.normpath('testapp')
        self.c.userdir = os.path.normpath('/home/user')
        out = os.path.normpath('/home/user/.woffice/.testapp')
        self.c.create_appdir()
        controller.os.makedirs.assert_called_once_with(out, exist_ok=True)

    def test_init_config(self):
        self.c.load_config = mock.Mock()
        self.c.appdir = os.path.normpath('/home/user/.woffice/.testapp')
        out = os.path.normpath('/home/user/.woffice/.testapp/.settings.ini')
        self.c.init_config()
        self.assertEqual(self.c.configfile, out)
        assert self.c.load_config.called

    def test_format_config(self):
        """ Scenario : All of the tests are passed. """
        inp0 = {'typeof': 'Spam0',
                'active_dstdir': [False, False, False],
                'tosend': False,
                'tosearch': False,
                'dstdir': ['/home', '', ''],
                'srcdir': ['']}
        out0 = {'tosend': False,
                'tosearch': False,
                'srcdir': '',
                'dstdir': '/home??',
                'typeof': 'Spam0',
                'active_dstdir': 'False?False?False'}
        obj0 = controller.Order(**inp0)

        inp1 = {'typeof': 'Spam1',
                'active_dstdir': [False, False, True],
                'tosend': True,
                'tosearch': True,
                'dstdir': ['', '/home', ''],
                'srcdir': ['']}
        out1 = {'tosend': True,
                'tosearch': True,
                'srcdir': '',
                'dstdir': '?/home?',
                'typeof': 'Spam1',
                'active_dstdir': 'False?False?True'}
        obj1 = controller.Order(**inp1)

        inp2 = {'typeof': 'Spam2',
                'active_dstdir': [True, False, True],
                'tosend': False,
                'tosearch': True,
                'dstdir': ['', '', '/home'],
                'srcdir': ['/home']}
        out2 = {'tosend': False,
                'tosearch': True,
                'srcdir': '/home',
                'dstdir': '??/home',
                'typeof': 'Spam2',
                'active_dstdir': 'True?False?True'}
        obj2 = controller.Order(**inp1)

        alist = [(inp0, out0, obj0),
                 (inp1, out1, obj1),
                 (inp2, out2, obj2)]
        for inp, out, obj in alist:
            with self.subTest():
                with mock.patch.dict(obj.__dict__, inp):
                    result = self.c.format_config(obj)
                    self.assertDictEqual(result, out)

    def test_write_config_0(self):
        """ Scenario 0: Config file exists, so os.makedirs isn't
            called. Config file is written successfully. """
        self.c.appdir = os.path.normpath('/home')
        typeof_list = [
            {'typeof': 'Spam0', 'tosend': False},
            {'typeof': 'Spam1', 'tosend': True}]
        objlist = list(range(len(typeof_list)))
        calls = [mock.call().write('[Spam0]\n'),
                 mock.call().write('tosend = False\n'),
                 mock.call().write('typeof = Spam0\n'),
                 mock.call().write('\n'),
                 mock.call().write('[Spam1]\n'),
                 mock.call().write('tosend = True\n'),
                 mock.call().write('typeof = Spam1\n'),
                 mock.call().write('\n')]
        self.c.format_config = mock.Mock(side_effect=typeof_list)
        controller.os.path.isdir = mock.Mock(return_value=True)
        controller.os.makedirs = mock.Mock()
        m = mock.mock_open()
        if sys.version_info < (3, 5):
            mopen = mock.patch('builtins.open', m, create=True)
        else:
            mopen = mock.patch('controller.open', m)
        mopen.start()
        self.c.write_config(objlist)
        m.assert_called_once_with(self.c.configfile, 'w+')
        assert m().write.call_count == len(calls)
        m.assert_has_calls(calls, any_order=True)
        assert not controller.os.makedirs.called
        mopen.stop()

    def test_write_config_1(self):
        """Scenario 1: Config file doesn't exist, so os.makedirs is
        called. Config file is written successfully.
        """
        self.c.appdir = os.path.normpath('/home')
        typeof_list = [
            {'typeof': 'Spam2', 'tosend': False},
            {'typeof': 'Spam3', 'active_dstdir': 'True?False?True'}]
        objlist = list(range(len(typeof_list)))
        calls = [mock.call().write('[Spam2]\n'),
                 mock.call().write('tosend = False\n'),
                 mock.call().write('typeof = Spam2\n'),
                 mock.call().write('\n'),
                 mock.call().write('[Spam3]\n'),
                 mock.call().write('active_dstdir = True?False?True\n'),
                 mock.call().write('typeof = Spam3\n'),
                 mock.call().write('\n')]
        self.c.format_config = mock.Mock(side_effect=typeof_list)
        controller.os.path.isdir = mock.Mock(return_value=False)
        controller.os.makedirs = mock.Mock()
        m = mock.mock_open()
        if sys.version_info < (3, 5):
            mopen = mock.patch('builtins.open', m, create=True)
        else:
            mopen = mock.patch('controller.open', m)
        mopen.start()
        self.c.write_config(objlist)
        m.assert_called_once_with(self.c.configfile, 'w+')
        assert m().write.call_count == len(calls)
        m.assert_has_calls(calls, any_order=True)
        assert controller.os.makedirs.called
        mopen.stop()

    def test_load_config_0(self):
        """ Scenario 0: Everything is OK.
            - the config file exists - os.path.isfile: True
            - the config file is read successfully,
            - the values are loaded from the config file,
            - logger doesn't write any messages to the log file.
            """
        controller.os.path.isfile = mock.Mock(return_value=True)
        tabwidget0 = mock.Mock(typeof='Spam0')
        tabwidget1 = mock.Mock(typeof='Spam1')
        tablist = [tabwidget0, tabwidget1]
        self.c.view.get_tablist = mock.Mock(return_value=tablist)
        self.c.config.read_dict({'Spam0': {'typeof': 'Spam0',
                                           'tosend': 'True',
                                           'dstdir': '/home?/home/user0?',
                                           'srcdir': '/home/test0',
                                           'active_dstdir': 'True?False?False'},
                                 'Spam1': {'typeof': 'Spam1',
                                           'tosend': 'False',
                                           'dstdir': '/home??',
                                           'srcdir': '/home/test1',
                                           'active_dstdir': 'False?True?True'}})
        calls0 = [mock.call.set_srcdir(['/home/test0'], fill=''),
                  mock.call.set_dstdir(['/home', '/home/user0', ''], fill=''),
                  mock.call.set_active_direc(['True', 'False', 'False'], fill=False),
                  mock.call.set_tosend('True')]
        calls1 = [mock.call.set_srcdir(['/home/test1'], fill=''),
                  mock.call.set_dstdir(['/home', '', ''], fill=''),
                  mock.call.set_active_direc(['False', 'True', 'True'], fill=False),
                  mock.call.set_tosend('False')]
        self.c.config.read = mock.Mock()
        self.c.load_config()
        assert self.c.config.read.call_count == 1
        assert not self.c.logger.warning.called
        tabwidget0.assert_has_calls(calls0, any_order=True)
        tabwidget1.assert_has_calls(calls1, any_order=True)

    def test_load_config_1(self):
        """ Scenario 1:
            - the config file exists - os.path.isfile: True
            - the config file is read successfully,
            - the default values are loaded to the View,
            - logger writes one messages to the log file.
            """
        typeof = 'Spam3'
        controller.os.path.isfile = mock.Mock(return_value=True)
        tabwidget0 = mock.Mock(typeof=typeof)
        tablist = [tabwidget0]
        self.c.view.get_tablist = mock.Mock(return_value=tablist)
        self.c.config.read_dict({'Spam0': {'typeof': 'Spam0',
                                           'tosend': 'True',
                                           'dstdir': '/home?/home/user0?',
                                           'srcdir': '/home/test0',
                                           'active_dstdir': 'True?False?False'}})
        self.c.config.read = mock.Mock()
        self.c.load_config()
        assert self.c.config.read.call_count == 1
        assert self.c.logger.warning.called
        with self.assertRaises(KeyError):
            self.c.config['Spam3']
        tabwidget0.set_srcdir.assert_called_once_with([''], fill='')
        tabwidget0.set_dstdir.assert_called_once_with([''], fill='')
        tabwidget0.set_active_direc.assert_called_once_with(['False'], fill=False)
        tabwidget0.set_tosend.set_active_direc(False)
        self.c.logger.warning.assert_called_once_with(self.c.configerr['keyerr'].format(typeof))

    def test_load_config_2(self):
        """ Scenario 2:
            - the config file doesn'texist - os.path.isfile: False,
            - the dafault values are loaded to the View,
            - logger writes two messages to the log file.
            """
        typeof = 'Spam0'
        controller.os.path.isfile = mock.Mock(return_value=False)
        tabwidget0 = mock.Mock(typeof=typeof)
        tablist = [tabwidget0]
        self.c.view.get_tablist = mock.Mock(return_value=tablist)
        self.c.config.read_dict({})
        calls = [mock.call.warning(self.c.configerr['nofile']),
                 mock.call.warning(self.c.configerr['keyerr'].format(typeof))]
        self.c.config.read = mock.Mock()
        self.c.load_config()
        assert not self.c.config.read.called
        tabwidget0.set_srcdir.assert_called_once_with([''], fill='')
        tabwidget0.set_dstdir.assert_called_once_with([''], fill='')
        tabwidget0.set_active_direc.assert_called_once_with(['False'], fill=False)
        tabwidget0.set_tosend.set_active_direc(False)
        self.c.logger.warning.assert_has_calls(calls)
        assert self.c.logger.warning.call_count == 2

    def test_load_config_3(self):
        """ Scenario 3:
            - the config file exists - os.path.isfile: True
            - the config file reading failed,
            - the dafault values are loaded to the View,
            - logger writes one messages to the log file.
            """
        typeof = 'Spam0'
        controller.os.path.isfile = mock.Mock(return_value=True)
        self.c.config.read = mock.Mock(side_effect=configparser.ParsingError('None'))
        tabwidget0 = mock.Mock(typeof=typeof)
        tablist = [tabwidget0]
        self.c.view.get_tablist = mock.Mock(return_value=tablist)
        self.c.load_config()
        assert self.c.config.read.call_count == 1
        calls = [mock.call.warning(self.c.configerr['parse']),
                 mock.call.warning(self.c.configerr['keyerr'].format(typeof))]
        with self.assertRaises(KeyError):
            self.c.config['Spam3']
        with self.assertRaises(configparser.ParsingError):
            self.c.config.read()
        tabwidget0.set_srcdir.assert_called_once_with([''], fill='')
        tabwidget0.set_dstdir.assert_called_once_with([''], fill='')
        tabwidget0.set_active_direc.assert_called_once_with(['False'], fill=False)
        tabwidget0.set_tosend.set_active_direc(False)
        self.c.logger.warning.assert_has_calls(calls)
        assert self.c.logger.warning.call_count == 2


class TestRun(unittest.TestCase):

    def setUp(self):
        self.c = controller.Controller()
        self.c.configfile = io.StringIO()
        self.c.config = configparser.ConfigParser()
        self.c.view = mock.Mock()
        self.c.logger = mock.Mock()
        self.c.model = mock.Mock()

    def test_tosearch_checker_0(self):
        """Scenario 0: Everything is OK.
        - controller.Order object is for searching, tosearch is True,
        - tosearch_checker returns True.
        """
        order = mock.Mock(typeof='Spam0',
                          srcdir=['/home'],
                          dstdir=['/etc', '/tmp/test', ''],
                          active_dstdir=[True, False, True],
                          tosend=True,
                          tosearch=True)
        with mock.patch('os.path.isdir') as isdir:
            isdir.side_effect = [True, True, True]  # trzy bo 1 z srcdir, 2 z dstdir
            result = self.c.tosearch_checker(order)
            self.assertTrue(result)
            assert not self.c.view.show_warning.called
            assert not self.c.logger.warning.called

    def test_tosearch_checker_1(self):
        """Scenariusz 1:
        - controller.Order będzie szukany: `tosearch` = False, dlatego
        `tosearch_checker` zwraca False.
        """
        order = mock.Mock(typeof='Spam1',
                          srcdir=['/home'],
                          dstdir=['/etc', '/tmp/test', ''],
                          active_dstdir=[True, False, True],
                          tosend=True,
                          tosearch=False)
        result = self.c.tosearch_checker(order)
        self.assertFalse(result)
        assert not self.c.view.show_warning.called
        assert not self.c.logger.warning.called

    def test_tosearch_checker_2(self):
        """Scenario 2:
        - controller.Order object is for searching, tosearch is True,
        - paths are not valid directory paths,
        - tosearch_checker returns False,
        - show_warning and logger.warning are called.
        """
        order = mock.Mock(typeof='Spam2',
                          srcdir=['/home'],
                          dstdir=[' ', '', ''],
                          active_dstdir=[True, True, True],
                          tosend=False,
                          tosearch=True)
        with mock.patch('os.path.isdir') as isdir:
            isdir.side_effect = [True, False, False, False]
            result = self.c.tosearch_checker(order)
            self.assertFalse(result)
            msg = self.c.configerr['omit'].format('Spam2')
            self.c.view.show_warning.assert_called_once_with(msg)
            self.c.logger.warning.assert_called_once_with(msg)

    def test_create_obj_from_other(self):
        tabwidget = mock.Mock(typeof='Spam0')
        tabwidget.get_from_direc = mock.Mock(return_value=['/home'])
        tabwidget.get_dest_direc = mock.Mock(return_value=['/etc', '/tmp/test', ''])
        tabwidget.get_active_direc = mock.Mock(return_value=[True, False, True])
        tabwidget.get_tosend = mock.Mock(return_value=True)
        tabwidget.get_tosearch = mock.Mock(return_value=True)
        out = {'typeof': 'Spam0',
               'srcdir': ['/home'],
               'dstdir': ['/etc', '/tmp/test', ''],
               'active_dstdir': [True, False, True],
               'tosend': True,
               'tosearch': True}
        result = self.c.create_obj_from_other(tabwidget)
        self.assertDictEqual(result.__dict__, out)
        self.assertTrue(isinstance(result, controller.Order))

    def test_run_0(self):
        order0 = mock.Mock(typeof='Spam0',
                           srcdir=['/home'],
                           dstdir=['/etc', '/tmp/test', ''],
                           active_dstdir=[True, False, True],
                           tosend=True,
                           tosearch=False)
        order1 = mock.Mock(typeof='Spam1',
                           srcdir=['/home'],
                           dstdir=['/etc', '/tmp/test', ''],
                           active_dstdir=[True, False, True],
                           tosend=True,
                           tosearch=True)
        order2 = mock.Mock(typeof='Spam2',
                           srcdir=['/home'],
                           dstdir=[' ', '', ''],
                           active_dstdir=[True, True, True],
                           tosend=False,
                           tosearch=True)
        calls_msg = [mock.call(self.c.msg['work'].format('Spam0')),
                     mock.call(self.c.msg['work'].format('Spam1')),
                     mock.call(self.c.msg['done'].format(2, 4))]
        ordlist = [order0, order1, order2]
        self.c.view.get_tablist = mock.Mock(return_value=[0, 1, 2])
        self.c.create_obj_from_other = mock.Mock(side_effect=ordlist)
        self.c.tosearch_checker = mock.Mock(side_effect=[True, True, False])
        self.c.model.search_dir = mock.Mock(side_effect=[(0, 1), (2, 3)])
        self.c.view.set_statusbar = mock.Mock()
        self.c.write_config = mock.Mock()
        self.c.run()
        self.assertTrue(self.c.model.search_dir.call_count == 2)
        self.assertTrue(self.c.create_obj_from_other.call_count == 3)
        self.c.view.set_statusbar.assert_has_calls(calls_msg)
        self.assertTrue(self.c.view.set_statusbar.call_count == 3)
        self.assertTrue(self.c.write_config.called)
        self.c.write_config.assert_called_once_with(ordlist)

    def test_run_1(self):
        order0 = mock.Mock(typeof='Spam3',
                           srcdir=['/home'],
                           dstdir=['/etc', '/tmp/test', ''],
                           active_dstdir=[True, False, True],
                           tosend=True,
                           tosearch=False)
        order1 = mock.Mock(typeof='Spam4',
                           srcdir=['/home'],
                           dstdir=['/etc', '/tmp/test', ''],
                           active_dstdir=[True, False, True],
                           tosend=True,
                           tosearch=True)
        order2 = mock.Mock(typeof='Spam2',
                           srcdir=['/home'],
                           dstdir=[' ', '', ''],
                           active_dstdir=[True, True, True],
                           tosend=False,
                           tosearch=True)
        calls_msg = [mock.call(self.c.msg['work'].format('Spam3')),
                     mock.call(self.c.msg['work'].format('Spam4')),
                     mock.call(self.c.msg['done'].format(2, 4))]
        ordlist = [order0, order1, order2]
        self.c.view.get_tablist = mock.Mock(return_value=[0, 1, 2])
        self.c.create_obj_from_other = mock.Mock(side_effect=ordlist)
        self.c.tosearch_checker = mock.Mock(side_effect=[True, True, False])
        self.c.model.search_dir = mock.Mock(side_effect=[(0, 1), (2, 3)])
        self.c.view.set_statusbar = mock.Mock()
        self.c.write_config = mock.Mock()
        self.c.run()
        self.assertTrue(self.c.model.search_dir.call_count == 2)
        self.assertTrue(self.c.create_obj_from_other.call_count == 3)
        self.c.view.set_statusbar.assert_has_calls(calls_msg)
        self.assertTrue(self.c.view.set_statusbar.call_count == 3)
        self.assertTrue(self.c.write_config.called)
        self.c.write_config.assert_called_once_with(ordlist)


if __name__ == '__main__':
    unittest.main()
