#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import io
import os
import tkinter as tk
import unittest
from unittest import mock
import view


class TestBasicFrame(unittest.TestCase):

    def setUp(self):
        # view.tk.Tk = mock.Mock()
        self.r = tk.Tk()
        view.MainApp.create_widgets = mock.Mock()
        # parent = mock.Mock(name='parent')
        # view.tk.BooleanVar = mock.Mock()
        # view.ttk.Frame = mock.Mock()
        # self.bf = view.BasicFrame(view.ttk.Frame())
        self.bf = view.BasicFrame(self.r)

    def tearDown(self):
        # view.ttk.Frame.reset_mock()
        self.r.quit()
        self.r.destroy()

    def test_create_frame(self):
        view.ttk.Frame = mock.Mock()
        self.bf.create_frame()
        calls = [mock.call(mock.ANY, padding=view.BASIC_PAD),
                 mock.call().pack(self.bf.FRM)]
        self.assertTrue(view.ttk.Frame.call_count == 1)
        view.ttk.Frame.assert_has_calls(calls)

    def test_set_isactive(self):
        inp_True = [True, 'True', 'true', 1, '1', 2]
        inp_False = [False, 'False', 'false', 0, '0']
        inp_excep = ['', 'test', '2']
        for inp in inp_True:
            with self.subTest(inp):
                self.bf.set_isactive(inp)
                result = self.bf.isactive.get()
                self.assertEqual(result, True)
        for inp in inp_False:
            with self.subTest(inp):
                self.bf.set_isactive(inp)
                result = self.bf.isactive.get()
                self.assertEqual(result, False)
        for inp in inp_excep:
            with self.subTest(inp):
                with self.assertRaises(tk.TclError):
                    self.bf.set_isactive(inp)

    def test_get_isactive(self):
        inp_True = [True, 'True', 'true', 1, '1', 2]
        inp_False = [False, 'False', 'false', 0, '0']
        for inp in inp_True:
            with self.subTest(inp):
                self.bf.isactive.set(inp)
                result = self.bf.get_isactive()
                self.assertEqual(result, True)
        for inp in inp_False:
            with self.subTest(inp):
                self.bf.isactive.set(inp)
                result = self.bf.get_isactive()
                self.assertEqual(result, False)

    def test_retoggle_0(self):
        """Scenario 0: """
        vgetval = True
        isactive = True
        self.bf.get_isactive = mock.Mock(return_value=isactive)
        v = mock.Mock()
        v.get.return_value = vgetval
        self.bf.entry = mock.Mock()
        self.bf.entry.state.return_value = None
        self.bf.button = mock.Mock()
        self.bf.button.state.return_value = None
        self.bf.retoggle(v)
        self.assertFalse(self.bf.entry.state.called)
        self.assertFalse(self.bf.button.state.called)

    def test_retoggle_1(self):
        """Scenario 1: """
        vgetval = True
        isactive = False
        self.bf.get_isactive = mock.Mock(return_value=isactive)
        v = mock.Mock()
        v.get.return_value = vgetval
        self.bf.entry = mock.Mock()
        self.bf.entry.state.return_value = None
        self.bf.button = mock.Mock()
        self.bf.button.state.return_value = None
        self.bf.retoggle(v)
        self.bf.entry.state.assert_called_once_with(['disabled'])
        self.bf.button.state.assert_called_once_with(['disabled'])

    def test_retoggle_2(self):
        """Scenario 2: """
        vgetval = False
        isactive = True
        self.bf.get_isactive = mock.Mock(return_value=isactive)
        v = mock.Mock()
        v.get.return_value = vgetval
        self.bf.entry = mock.Mock()
        self.bf.entry.state.return_value = None
        self.bf.button = mock.Mock()
        self.bf.button.state.return_value = None
        self.bf.retoggle(v)
        self.assertFalse(self.bf.entry.state.called)
        self.assertFalse(self.bf.button.state.called)

    def test_retoggle_3(self):
        """Scenario 3: """
        vgetval = False
        isactive = False
        self.bf.get_isactive = mock.Mock(return_value=isactive)
        v = mock.Mock()
        v.get.return_value = vgetval
        self.bf.entry = mock.Mock()
        self.bf.entry.state.return_value = None
        self.bf.button = mock.Mock()
        self.bf.button.state.return_value = None
        self.bf.retoggle(v)
        self.assertFalse(self.bf.entry.state.called)
        self.assertFalse(self.bf.button.state.called)

    def test_retoggle_4(self):
        """Scenario 4: The AttributeError is raised."""
        vgetval = False
        isactive = False
        self.bf.get_isactive = mock.Mock(return_value=isactive)
        v = mock.Mock()
        v.get.return_value = vgetval
        self.bf.entry = mock.Mock(spec=[])
        self.bf.button = mock.Mock(spec=[])
        self.bf.retoggle(v)
        with self.assertRaises(AttributeError):
            self.bf.checkbutton.state(['disabled'])

    def test_toggle_act_0(self):
        """Scenario 0: view.BasicFrame.toogle_act is called with:
        True and exclude=True.
        """
        vgetval = True
        exclude = True
        v = mock.Mock()
        v.get.return_value = vgetval
        fchild0 = mock.Mock(name='fchild0')
        fchild1 = mock.Mock(name='fchild1')
        fchild0.state.return_value = None
        fchild1.state.return_value = None
        fchildren = [fchild0, fchild1]
        self.bf.checkbutton = mock.Mock()
        self.bf.checkbutton.state.return_value = None
        self.bf.frame.winfo_children = mock.Mock(side_effect=[fchildren])
        self.bf.retoggle = mock.Mock()
        self.bf.toggle_act(v, exclude)
        fchild0.state.assert_called_once_with(['!disabled'])
        fchild1.state.assert_called_once_with(['!disabled'])
        self.bf.checkbutton.state.assert_called_once_with(['!disabled'])
        self.assertTrue(self.bf.retoggle.call_count == 1)

    def test_toggle_act_1(self):
        """Scenario 1: view.BasicFrame.toogle_act is called with:
        True and exclude=False.
        """
        vgetval = True
        exclude = False
        v = mock.Mock()
        v.get.return_value=vgetval
        fchild0 = mock.Mock(name='fchild0')
        fchild1 = mock.Mock(name='fchild1')
        fchild0.state.return_value = None
        fchild1.state.return_value = None
        fchildren = [fchild0, fchild1]
        self.bf.checkbutton = mock.Mock()
        self.bf.checkbutton.state.return_value = None
        self.bf.frame.winfo_children = mock.Mock(side_effect=[fchildren])
        self.bf.retoggle = mock.Mock()
        self.bf.toggle_act(v, exclude)
        fchild0.state.assert_called_once_with(['!disabled'])
        fchild1.state.assert_called_once_with(['!disabled'])
        self.assertFalse(self.bf.checkbutton.state.called)
        self.assertTrue(self.bf.retoggle.call_count == 1)

    def test_toggle_act_2(self):
        """Scenario 2: view.BasicFrame.toogle_act is called with:
        False and exclude=True. Additional the AttributeError is
        raised.
        """
        vgetval = False
        exclude = True
        v = mock.Mock()
        v.get.return_value = vgetval
        fchild0 = mock.Mock(name='fchild0')
        fchild1 = mock.Mock(name='fchild1')
        fchild0.state.return_value = None
        fchild1.state.return_value = None
        fchildren = [fchild0, fchild1]
        self.bf.checkbutton = mock.Mock(spec=[])
        self.bf.frame.winfo_children = mock.Mock(side_effect=[fchildren])
        self.bf.retoggle = mock.Mock()
        self.bf.toggle_act(v, exclude)
        fchild0.state.assert_called_once_with(['disabled'])
        fchild1.state.assert_called_once_with(['disabled'])
        # kiedy wywołanie danej funkcji wywołuje Exception, mock_calls
        # czy method_calls nie zapisują niczego, bo takie wywołanie nie
        # jest liczone, stąd []
        self.assertListEqual(self.bf.checkbutton.method_calls, [])
        with self.assertRaises(AttributeError):
            self.bf.checkbutton.state(['disabled'])
        self.assertTrue(self.bf.retoggle.call_count == 1)

    def test_toggle_act_3(self):
        """Scenario 3: view.BasicFrame.toogle_act is called with:
        False and exclude=False.
        """
        vgetval = False
        exclude = False
        v = mock.Mock()
        v.get.return_value = vgetval
        fchild0 = mock.Mock(name='fchild0')
        fchild1 = mock.Mock(name='fchild1')
        fchild0.state.return_value = None
        fchild1.state.return_value = None
        fchildren = [fchild0, fchild1]
        self.bf.checkbutton = mock.Mock()
        self.bf.frame.winfo_children = mock.Mock(side_effect=[fchildren])
        self.bf.retoggle = mock.Mock()
        self.bf.toggle_act(v, exclude)
        fchild0.state.assert_called_once_with(['disabled'])
        fchild1.state.assert_called_once_with(['disabled'])
        self.assertListEqual(self.bf.checkbutton.method_calls, [])
        self.assertFalse(self.bf.checkbutton.state.called)
        self.assertTrue(self.bf.retoggle.call_count == 1)

    def test_create_checkbutton(self):
        view.ttk.Checkbutton = mock.Mock()
        self.bf.toggle_act = mock.Mock()
        self.bf.isactive = mock.Mock()
        self.bf.create_checkbutton()
        calls = [mock.call(mock.ANY, command=mock.ANY,
                           text="", variable=self.bf.isactive),
                 mock.call().pack(self.bf.CHCK_BTN)]
        view.ttk.Checkbutton.assert_has_calls(calls)
        self.assertTrue(view.ttk.Checkbutton.call_count == 1)
        self.bf.toggle_act.assert_called_once_with(mock.ANY, False)


class TestTabWidget(unittest.TestCase):

    def setUp(self):
        self.r = tk.Tk()
        view.tk.BooleanVar = mock.Mock()
        view.TabWidget.create_widget = mock.Mock()
        self.tw = view.TabWidget(self.r, 'Spam0')

    def tearDown(self):
        self.r.quit()
        self.r.destroy()

    def test_create_active_btn(self):
        view.ttk.Frame = mock.Mock(name='view.ttk.Frame')
        view.ttk.Checkbutton = mock.Mock(name='view.ttk.Checkbutton')
        calls_frame = [mock.call(mock.ANY, padding=view.BASIC_PAD)]
        calls_checkbutton = [mock.call(mock.ANY, command=mock.ANY,
                                       text=self.tw.txt['enabled'],
                                       variable=self.tw.tosearch),
                             mock.call().pack(self.tw.CHCK_BTN)]
        self.tw.create_active_btn()
        view.ttk.Frame.assert_has_calls(calls_frame)
        view.ttk.Checkbutton.assert_has_calls(calls_checkbutton)
        self.assertTrue(view.ttk.Frame.call_count == 1)
        self.assertTrue(view.ttk.Checkbutton.call_count == 1)

    def test_create_from_panel_0(self):
        """Scenario 0: keyword argument `amount` in create_from_panel
        is 1 (default).
        """
        amount = 1
        view.ttk.LabelFrame = mock.Mock(name='view.ttk.LabelFrame')
        calls_labelframe = [mock.call(mock.ANY, padding=view.BASIC_PAD,
                                      text=self.tw.txt['from']),
                            mock.call().pack(self.tw.FRM, pady=5)]
        calls_ds = [mock.call(mock.ANY),
                    mock.call().create_checkbutton(),
                    mock.call().create_widgets(),
                    mock.call().isactive.set(True)]
        ds_patch = mock.patch('view.DirectorySelector')
        ds_patch.start()
        self.tw.create_from_panel(amount=amount)
        view.ttk.LabelFrame.assert_has_calls(calls_labelframe)
        view.DirectorySelector.assert_has_calls(calls_ds)
        self.assertTrue(view.DirectorySelector.call_count == amount)
        self.assertTrue(len(self.tw.from_dirsel_list) == amount)
        ds_patch.stop()

    def test_create_from_panel_1(self):
        """Scenario 1: keyword argument `amount` in create_from_panel
        is 2.
        """
        amount = 2
        view.ttk.LabelFrame = mock.Mock(name='view.ttk.LabelFrame')
        calls_labelframe = [mock.call(mock.ANY, padding=view.BASIC_PAD,
                                      text=self.tw.txt['from']),
                            mock.call().pack(self.tw.FRM, pady=5)]
        calls_ds = [mock.call(mock.ANY),
                    mock.call().create_checkbutton(),
                    mock.call().create_widgets()]
        ds_patch = mock.patch('view.DirectorySelector')
        ds_patch.start()
        self.tw.create_from_panel(amount=amount)
        view.DirectorySelector.assert_has_calls(calls_ds * amount,
                                                any_order=True)
        self.assertTrue(view.DirectorySelector.call_count == amount)
        view.ttk.LabelFrame.assert_has_calls(calls_labelframe)
        self.assertTrue(len(self.tw.from_dirsel_list) == amount)
        ds_patch.stop()

    def test_create_dest_panel_0(self):
        """Scenario 0: keyword argument `amount` in create_from_panel
        is 3 (default).
        """
        amount = 3
        view.ttk.LabelFrame = mock.Mock(name='view.ttk.LabelFrame')
        view.BasicFrame = mock.Mock(name='view.BasicFrame')
        calls_labelframe = [mock.call(mock.ANY, padding=view.BASIC_PAD,
                                      text=self.tw.txt['to']),
                            mock.call().pack(self.tw.FRM, pady=5)]
        calls_basicframe = [mock.call(mock.ANY),
                            mock.call().create_checkbutton(
                                self.tw.txt['move'])]
        calls_ds = [mock.call(mock.ANY),
                    mock.call().create_checkbutton(),
                    mock.call().create_widgets()]
        ds_patch = mock.patch('view.DirectorySelector')
        ds_patch.start()
        self.tw.create_dest_panel(amount=amount)
        view.ttk.LabelFrame.assert_has_calls(calls_labelframe)
        self.assertTrue(view.ttk.LabelFrame.call_count == 1)
        view.BasicFrame.assert_has_calls(calls_basicframe)
        self.assertTrue(view.BasicFrame.call_count == 1)
        view.DirectorySelector.assert_has_calls(calls_ds * amount,
                                                any_order=True)
        self.assertTrue(view.DirectorySelector.call_count == amount)
        self.assertTrue(len(self.tw.dest_dirsel_list) == amount)
        ds_patch.stop()

    def test_active_toggle_0(self):
        """Scenario 0: typeof is not 'IN'."""
        self.tw.tosearch = True
        self.tw.tosend = mock.Mock()
        self.tw.typeof = 'SPAM0'
        from_dir0 = mock.Mock()
        dest_dir0 = mock.Mock()
        dest_dir1 = mock.Mock()
        self.tw.from_dirsel_list = [from_dir0]
        self.tw.dest_dirsel_list = [dest_dir0, dest_dir1]
        calls = [mock.call.toggle_act(self.tw.tosearch, False),
                 mock.call.checkbutton.state(['disabled'])]
        self.tw.active_toggle()
        from_dir0.assert_has_calls(calls)
        dest_dir0.toggle_act.assert_called_once_with(self.tw.tosearch,
                                                     False)
        dest_dir1.toggle_act.assert_called_once_with(self.tw.tosearch,
                                                     False)
        self.tw.tosend.assert_has_calls(calls)

    def test_active_toggle_1(self):
        """Scenario 1: typeof is 'IN'."""
        self.tw.tosearch = True
        self.tw.tosend = mock.Mock()
        self.tw.typeof = 'in'
        from_dir0 = mock.Mock()
        dest_dir0 = mock.Mock()
        dest_dir1 = mock.Mock()
        self.tw.from_dirsel_list = [from_dir0]
        self.tw.dest_dirsel_list = [dest_dir0, dest_dir1]
        calls = [mock.call.toggle_act(self.tw.tosearch, False),
                 mock.call.checkbutton.state(['disabled'])]
        self.tw.active_toggle()
        from_dir0.assert_has_calls(calls)
        dest_dir0.toggle_act.assert_called_once_with(self.tw.tosearch,
                                                     False)
        dest_dir1.toggle_act.assert_called_once_with(self.tw.tosearch,
                                                     False)
        self.tw.tosend.toggle_act.assert_called_once_with(self.tw.tosearch,
                                                          False)

    def test_get_tosend(self):
        self.tw.tosend = mock.Mock()
        self.tw.tosend.get_isactive.side_effect = [True, False]
        result = self.tw.get_tosend()
        self.assertTrue(result)
        result = self.tw.get_tosend()
        self.assertFalse(result)

    def test_get_tosearch(self):
        self.tw.tosearch.get.side_effect = [True, False]
        result = self.tw.get_tosearch()
        self.assertTrue(result)
        result = self.tw.get_tosearch()
        self.assertFalse(result)

    def test_get_from_direc(self):
        out = ['/home', '/usr/bin']
        ds0_args = {'getdirec.return_value': '/home',
                    'get_isactive.return_value': True}
        ds1_args = {'getdirec.return_value': '/opt',
                    'get_isactive.return_value': False}
        ds2_args = {'getdirec.return_value': '/usr/bin',
                    'get_isactive.return_value': True}
        self.tw.from_dirsel_list = [mock.Mock(**ds0_args),
                                    mock.Mock(**ds1_args),
                                    mock.Mock(**ds2_args)]
        result = self.tw.get_from_direc()
        self.assertListEqual(result, out)

    def test_get_dest_direc(self):
        out = ['/opt', '', '/usr/bin/env']
        ds0_args = {'getdirec.return_value': '/opt'}
        ds1_args = {'getdirec.return_value': ''}
        ds2_args = {'getdirec.return_value': '/usr/bin/env'}
        self.tw.dest_dirsel_list = [mock.Mock(**ds0_args),
                                    mock.Mock(**ds1_args),
                                    mock.Mock(**ds2_args)]
        result = self.tw.get_dest_direc()
        self.assertListEqual(result, out)

    def test_get_active_direc(self):
        out = [True, False, True]
        ds0_args = {'get_isactive.return_value': True}
        ds1_args = {'get_isactive.return_value': False}
        ds2_args = {'get_isactive.return_value': True}
        self.tw.dest_dirsel_list = [mock.Mock(**ds0_args),
                                    mock.Mock(**ds1_args),
                                    mock.Mock(**ds2_args)]
        result = self.tw.get_active_direc()
        self.assertListEqual(result, out)
        
    def test_set_srcdir(self):
        ds0 = mock.Mock()
        ds1 = mock.Mock()
        self.tw.from_dirsel_list = [ds0, ds1]
        val = ['/home']
        self.tw.set_srcdir(val)
        ds0.setdirec.assert_called_once_with('/home')
        ds1.setdirec.assert_called_once_with('')
        
    def test_set_dstdir_0(self):
        ds0 = mock.Mock()
        ds1 = mock.Mock()
        ds2 = mock.Mock()
        self.tw.dest_dirsel_list = [ds0, ds1, ds2]
        val = ['/test/TEST 01', '/opt', '/TEST i TEST/test']
        self.tw.set_dstdir(val)
        ds0.setdirec.assert_called_once_with(val[0])
        ds1.setdirec.assert_called_once_with(val[1])
        ds2.setdirec.assert_called_once_with(val[2])
        
    def test_set_dstdir_1(self):
        ds0 = mock.Mock()
        ds1 = mock.Mock()
        ds2 = mock.Mock()
        self.tw.dest_dirsel_list = [ds0, ds1, ds2]
        val = ['']
        self.tw.set_dstdir(val)
        ds0.setdirec.assert_called_once_with(val[0])
        ds1.setdirec.assert_called_once_with('')
        ds2.setdirec.assert_called_once_with('')
            
    def test_set_active_direc_0(self):
        ds0 = mock.Mock()
        ds1 = mock.Mock()
        ds2 = mock.Mock()
        self.tw.dest_dirsel_list = [ds0, ds1, ds2]
        val = ['False', 'True', 'False']
        self.tw.set_active_direc(val)
        ds0.set_isactive.assert_called_once_with(val[0])
        ds1.set_isactive.assert_called_once_with(val[1])
        ds2.set_isactive.assert_called_once_with(val[2])
            
    def test_set_active_direc_1(self):
        ds0 = mock.Mock()
        ds1 = mock.Mock()
        ds2 = mock.Mock()
        self.tw.dest_dirsel_list = [ds0, ds1, ds2]
        val = ['False']
        self.tw.set_active_direc(val)
        ds0.set_isactive.assert_called_once_with(val[0])
        ds1.set_isactive.assert_called_once_with(False)
        ds2.set_isactive.assert_called_once_with(False)
        
    def test_set_tosend(self):
        val = ['True', 'False', 'true', 'false', True, False]
        self.tw.tosend = mock.Mock()
        for v in val:
            with self.subTest(v=v):
                self.tw.set_tosend(v)
                self.tw.tosend.set_isactive.assert_called_once_with(v)
                self.tw.tosend.set_isactive.reset_mock()

    @unittest.skip("Nie będę testować")
    def test_create_widget(self):
        self.tw.create_active_btn = mock.Mock()
        self.tw.create_from_panel = mock.Mock()
        self.tw.create_dest_panel = mock.Mock()
        self.tw.active_toggle = mock.Mock()
        self.tw.create_widget()
        print(self.tw.create_widget.call_count)


class TestDirectorySelector(unittest.TestCase):

    def setUp(self):
        self.r = tk.Tk()
        self.ds = view.DirectorySelector(self.r)

    def tearDown(self):
        self.r.quit()
        self.r.destroy()

    def test_getdirec(self):
        dirs_inp = ['/home', 10, None, '']
        dirs_out = ['/home', '10', 'None', '']
        for di, do in zip(dirs_inp, dirs_out):
            with self.subTest((di, do)):
                self.ds.direc.set(di)
                result = self.ds.getdirec()
                self.assertEqual(result, do)

    def test_setdirec(self):
        dirs_inp = ['/home', 10, None]
        dirs_out = ['/home', '10', 'None']
        for di, do in zip(dirs_inp, dirs_out):
            with self.subTest((di, do)):
                self.ds.setdirec(di)
                result = self.ds.direc.get()
                self.assertEqual(result, do)

    def test_opendirec_0(self):
        """Scenario 0: Directory is selected."""
        d = '/home'
        v = mock.Mock()
        v.get.return_value=d
        view.tk.filedialog.askdirectory = mock.Mock(return_value=d)
        self.ds.setdirec = mock.Mock()
        self.ds.opendirec(v)
        view.tk.filedialog.askdirectory.assert_called_once_with(initialdir='/home')
        d = os.path.normpath(d)
        self.ds.setdirec.assert_called_once_with(d)

    def test_opendirec_1(self):
        """Scenario 1: Directory is not selected."""
        d = ''
        v = mock.Mock()
        v.get.return_value=d
        view.tk.filedialog.askdirectory = mock.Mock(return_value=d)
        self.ds.setdirec = mock.Mock()
        self.ds.opendirec(v)
        view.tk.filedialog.askdirectory.assert_called_once_with(initialdir='')
        self.assertFalse(self.ds.setdirec.called)

    def test_validate(self):
        self.ds.getdirec = mock.Mock()
        view.os.path.isdir = mock.Mock(return_value=True)
        result0 = self.ds.validate()
        self.assertTrue(result0)
        view.os.path.isdir = mock.Mock(return_value=False)
        result1 = self.ds.validate()
        self.assertTrue(self.ds.getdirec.call_count == 2)
        self.assertFalse(result1)

    def test_invalid(self):
        path = '/wrong/path'
        self.ds.getdirec = mock.Mock(return_value=path)
        self.ds.showerror = mock.Mock()
        self.ds.invalid()
        msg = self.ds.err['invalid'].format(path)
        self.ds.showerror.assert_called_once_with(msg)
        self.assertTrue(self.ds.getdirec.call_count == 1)

    def test_create_widgets(self):
        view.ttk.Style = mock.Mock()
        view.ttk.Button = mock.Mock()
        view.ttk.Entry = mock.Mock()
        calls_style = [mock.call().map('C.TEntry',
                                       foreground=[('invalid', 'red'),
                                                   ('disabled', '#a3a3a3')])]
        calls_button = [mock.call(mock.ANY, command=mock.ANY,
                                  text=self.ds.txt['browse'], width=self.ds.UNIT),
                        mock.call().pack(side='left')]
        calls_entry = [mock.call(mock.ANY, invalidcommand=mock.ANY,
                                 textvariable=self.ds.direc,
                                 style='C.TEntry',
                                 validate='focusout',
                                 validatecommand=mock.ANY,
                                 width=5*self.ds.UNIT),
                       mock.call().pack(self.ds.ENTR)]
        self.ds.create_widgets()
        view.ttk.Style.assert_has_calls(calls_style)
        self.assertTrue(view.ttk.Style.call_count == 1)
        view.ttk.Button.assert_has_calls(calls_button)
        self.assertTrue(view.ttk.Button.call_count == 1)
        view.ttk.Entry.assert_has_calls(calls_entry)
        self.assertTrue(view.ttk.Entry.call_count == 1)


class TestMainApp(unittest.TestCase):

    def setUp(self):
        # self.r = tk.Tk()
        view.tk.Tk = mock.Mock()
        view.MainApp.create_widgets = mock.Mock()
        self.mw = view.MainApp()
        # self.mw = view.MainWindow()
        # self.ma.root = mock.Mock()
        # self.ma.create_widgets = mock.Mock()

    # def tearDown(self):
        # self.r.quit()
        # self.r.destroy()

    def test_add_spaces(self):
        inp = [' aaa', 'bb', 'ccccc', 'd', ' ']
        out = ['   aaa   ', '   bb    ', '  ccccc  ', '    d    ', '         ']
        result = self.mw.add_spaces(inp)
        self.assertEqual(result, out)

    def test_create_tabs(self):
        tabsname = ['aa', 'bbb', 'c ']
        tabsname_spaces = [' aa ', ' bbb ', ' c ']
        self.mw.root = mock.Mock()
        tw_patch = mock.patch('view.TabWidget')
        tw_patch.start()
        # https://docs.python.org/3/library/unittest.mock.html#where-to-patch
        view.ttk.Frame = mock.Mock(name='view.ttk.Frame')
        view.ttk.Notebook = mock.Mock(name='view.ttk.Notebook')
        # view.TabWidget = mock.Mock(name='view.TabWidget')
        view.BasicFrame = mock.Mock(name='view.BasicFrame', FRM=5)
        self.mw.add_spaces = mock.Mock(side_effect=[tabsname_spaces])
        counter = len(tabsname)
        notecalls = [mock.call(mock.ANY),
                     mock.call().add(mock.ANY, compound='center',
                                     padding=5, text=tabsname_spaces[0]),
                     mock.call().add(mock.ANY, compound='center',
                                     padding=5, text=tabsname_spaces[1]),
                     mock.call().add(mock.ANY, compound='center',
                                     padding=5, text=tabsname_spaces[2]),
                     mock.call().pack(5)]
        tabcalls = [mock.call().add(mock.ANY,
                                    tabsname_spaces[0].strip()),
                    mock.call().add(mock.ANY,
                                    tabsname_spaces[1].strip()),
                    mock.call().add(mock.ANY,
                                    tabsname_spaces[2].strip())]
        self.mw.create_tabs(tabsname)
        self.assertTrue(view.ttk.Frame.call_count == counter + 1)
        self.assertTrue(view.TabWidget.call_count == counter)
        self.assertTrue(len(view.ttk.Notebook.mock_calls) == counter + 2)
        self.assertTrue(len(self.mw.tablist) == counter)
        self.assertTrue(self.mw.add_spaces.call_count == 1)
        view.ttk.Notebook.assert_has_calls(notecalls, any_order=True)
        view.TabWidget.assert_has_calls(tabcalls, any_order=True)
        tw_patch.stop()

    def test_create_bottom_bar(self):
        self.mw.root = mock.Mock()
        view.tk.StringVar = mock.Mock(side_effect=io.StringIO)
        view.ttk.Frame = mock.Mock(name='view.ttk.Frame')
        view.ttk.Button = mock.Mock(name='view.ttk.Button')
        view.ttk.Label = mock.Mock(name='view.ttk.Label')
        buttoncalls = [mock.call(mock.ANY, command=mock.ANY,
                                 text=self.mw.txt['cancel'], 
                                 width=view.BasicFrame.UNIT),
                       mock.call(mock.ANY, command=mock.ANY,
                                 text=self.mw.txt['ok'],
                                 width=view.BasicFrame.UNIT),
                       mock.call().pack(self.mw.BTN),
                       mock.call().pack(self.mw.BTN)]
        labelcalls = [mock.call(mock.ANY, borderwidth=1, justify='left',
                                padding=5, relief='sunken',
                                textvariable=mock.ANY),
                      mock.call(mock.ANY, cursor='hand2', foreground='blue', 
                                justify='left', padding=5, 
                                text=self.mw.txt['showlog']),
                      mock.call().pack(self.mw.LBL),
                      mock.call().pack(self.mw.BTN),
                      mock.call().bind('<Button-1>', mock.ANY)]
        self.mw.create_bottom_bar()
        self.assertTrue(view.ttk.Label.call_count == 2)
        self.assertTrue(view.ttk.Button.call_count == 2)
        self.assertTrue(view.ttk.Frame.call_count == 1)
        view.ttk.Button.assert_has_calls(buttoncalls, any_order=True)
        view.ttk.Label.assert_has_calls(labelcalls, any_order=True)

    def test_isdir_selected_0(self):
        """Scenario 0: Everything is OK. All requirements are met. 
        Function return True.
        """
        tw0_args = {'typeof': 'Spam0',
                    'get_tosearch.return_value': True,
                    'get_from_direc.return_value': ['/home'],
                    'get_dest_direc.return_value': ['/usr', '', '']
                    }
        tw1_args = {'typeof': 'Spam1',
                    'get_tosearch.return_value': True,
                    'get_from_direc.return_value': ['/home'],
                    'get_dest_direc.return_value': ['', '/test', '']
                    }
        tw0 = mock.Mock(**tw0_args)
        tw1 = mock.Mock(**tw1_args)
        self.mw.tablist = [tw0, tw1]
        result = self.mw.isdir_selected()
        self.assertTrue(result)

    def test_isdir_selected_1(self):
        """Scenario 1: One of the TabWidget (tw) object has no selected
        path. 
        Function return False.
        """
        self.mw.show_warning = mock.Mock()
        tw0_args = {'typeof': 'Spam2',
                    'get_tosearch.return_value': True,
                    'get_from_direc.return_value': ['/home'],
                    'get_dest_direc.return_value': ['/usr', '', '']
                    }
        tw1_args = {'typeof': 'Spam3',
                    'get_tosearch.return_value': True,
                    'get_from_direc.return_value': ['/home'],
                    'get_dest_direc.return_value': ['', '', '']
                    }
        tw0 = mock.Mock(**tw0_args)
        tw1 = mock.Mock(**tw1_args)
        self.mw.tablist = [tw0, tw1]
        result = self.mw.isdir_selected()
        msg = self.mw.err['noselect'].format('Spam3')
        self.mw.show_warning.assert_called_once_with(msg)
        self.assertFalse(result)

    def test_isdir_selected_2(self):
        """Scenario 2: One of the TabWidget (tw) object has no selected path.
        Function return False.
        """
        self.mw.show_warning = mock.Mock()
        tw0_args = {'typeof': 'Spam4',
                    'get_tosearch.return_value': True,
                    'get_from_direc.return_value': ['/home'],
                    'get_dest_direc.return_value': ['/usr', '/test0', '/test1']
                    }
        tw1_args = {'typeof': 'Spam5',
                    'get_tosearch.return_value': True,
                    'get_from_direc.return_value': [''],
                    'get_dest_direc.return_value': ['/usr', '/test0', '/test1']
                    }
        tw0 = mock.Mock(**tw0_args)
        tw1 = mock.Mock(**tw1_args)
        self.mw.tablist = [tw0, tw1]
        result = self.mw.isdir_selected()
        msg = self.mw.err['noselect'].format('Spam5')
        self.mw.show_warning.assert_called_once_with(msg)
        self.assertFalse(result)

    def test_isdir_selected_3(self):
        """Scenario 3: One of the TabWidget (tw) object is not for 
        searching. Function return True.
        """
        tw0_args = {'typeof': 'Spam6',
                    'get_tosearch.return_value': False,
                    'get_from_direc.return_value': ['/home'],
                    'get_dest_direc.return_value': ['/usr', '', '']
                    }
        tw1_args = {'typeof': 'Spam7',
                    'get_tosearch.return_value': True,
                    'get_from_direc.return_value': ['/home'],
                    'get_dest_direc.return_value': ['', '/test', '']
                    }
        tw0 = mock.Mock(**tw0_args)
        tw1 = mock.Mock(**tw1_args)
        self.mw.tablist = [tw0, tw1]
        result = self.mw.isdir_selected()
        self.assertTrue(result)
        
    def test_isany_active_0(self):
        """Scenrio 0: At least one of the TabWidget (tw) object meets
        the requirements - get_tosearch returns True."""
        tw0_args = {'typeof': 'Spam0',
                    'get_tosearch.return_value': False}
        tw1_args = {'typeof': 'Spam1',
                    'get_tosearch.return_value': False}
        tw2_args = {'typeof': 'Spam2',
                    'get_tosearch.return_value': True}
        tw0 = mock.Mock(**tw0_args)
        tw1 = mock.Mock(**tw1_args)
        tw2 = mock.Mock(**tw2_args)
        self.mw.tablist = [tw0, tw1, tw2]
        result = self.mw.isany_active()
        self.assertTrue(result)
        
    def test_isany_active_1(self):
        """Scenrio 1: At least one of the TabWidget (tw) object meets
        the requirements - get_tosearch returns True."""
        self.mw.show_warning = mock.Mock()
        tw0_args = {'typeof': 'Spam0',
                    'get_tosearch.return_value': False}
        tw1_args = {'typeof': 'Spam1',
                    'get_tosearch.return_value': False}
        tw2_args = {'typeof': 'Spam2',
                    'get_tosearch.return_value': False}
        tw0 = mock.Mock(**tw0_args)
        tw1 = mock.Mock(**tw1_args)
        tw2 = mock.Mock(**tw2_args)
        self.mw.tablist = [tw0, tw1, tw2]
        result = self.mw.isany_active()
        msg = self.mw.err['noactive']
        self.mw.show_warning.assert_called_once_with(msg)
        self.assertFalse(result)
        
    def test_run_0(self):
        """Scenario 0: Everything is OK. self.controller.run is
        called."""
        self.mw.isany_active = mock.Mock(return_value=True)
        self.mw.isdir_selected = mock.Mock(return_value=True)
        self.mw.controller = mock.Mock()
        self.mw.run()
        self.assertTrue(self.mw.controller.run.called)

    def test_run_1(self):
        """Scenario 1: self.controller.run is not called."""
        self.mw.isany_active = mock.Mock(return_value=True)
        self.mw.isdir_selected = mock.Mock(return_value=False)
        self.mw.controller = mock.Mock()
        self.mw.run()
        self.assertFalse(self.mw.controller.run.called)

    def test_run_2(self):
        """Scenario 2: self.controller.run is called, but exception is
        raised."""
        self.mw.isany_active = mock.Mock(return_value=True)
        self.mw.isdir_selected = mock.Mock(return_value=True)
        self.mw.run()
        with self.assertRaises(AttributeError):
            self.mw.controller.run()


if __name__ == '__main__':
    unittest.main()
