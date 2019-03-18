#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import controller


def main():
    c = controller.Controller()
    c.make_gui()
    c.create_appdir()
    c.create_log()
    c.init_config()
    c.show_view()


if __name__ == '__main__':
    main()
