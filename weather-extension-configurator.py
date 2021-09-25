#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Mode: Python; py-indent-offset: 4 -*-
# vim: tabstop=4 shiftwidth=4 expandtab

# weather-extension-configurator: 
# configures gnome-shell-extension-weather by simon04
# Copyright (C) 2011 Igor Ingultsov aka inv, aka invy
#
# based on a configurator for system-monitor-extension by Florian Mounier aka paradoxxxzero

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Author: Igor Ingultsov aka inv, aka invy

"""
gnome-shell-weather-extension-config
Tool for editing gnome-shell-weather-extension-config preference as
an alternative of dconf-editor

"""

from gi.repository import Gtk, Gio, Gdk


def up_first(string):
    return string[0].upper() + string[1:]


class IntSelect:
    def __init__(self, name, value, minv, maxv, incre, page):
        self.label = Gtk.Label(name + ":")
        self.spin = Gtk.SpinButton()
        self.actor = Gtk.HBox()
        self.actor.add(self.label)
        self.actor.add(self.spin)
        self.spin.set_range(minv, maxv)
        self.spin.set_increments(incre, page)
        self.spin.set_numeric(True)
        self.spin.set_value(value)


class TextSelect:
    def __init__(self, name, value):
        self.label = Gtk.Label(name + ":")
        self.entry = Gtk.Entry()
        self.actor = Gtk.HBox()
        self.actor.add(self.label)
        self.actor.add(self.entry)
        self.entry.set_text(value)



class Select:
    def __init__(self, name, value, items):
        self.label = Gtk.Label(name + ":")
        self.selector = Gtk.ComboBoxText()
        self.actor = Gtk.HBox()
        for item in items:
            self.selector.append_text(item)
        self.selector.set_active(value)
        self.actor.add(self.label)
        self.actor.add(self.selector)


def set_boolean(check, schema, name):
    schema.set_boolean(name, check.get_active())


def set_int(spin, schema, name):
    schema.set_int(name, spin.get_value_as_int())
    return False

def set_text(tb, schema, name):
    schema.set_text(name, tb.get_text())

def set_enum(combo, schema, name):
    schema.set_enum(name, combo.get_active())


def set_color(cb, schema, name):
    schema.set_string(name, color_to_hex(cb.get_rgba()))


class SettingFrame:
    def __init__(self, name, schema):
        self.schema = schema
        self.label = Gtk.Label(name)
        self.frame = Gtk.Frame()
        self.frame.set_border_width(10)
        self.vbox = Gtk.VBox(spacing=20)
        self.hbox0 = Gtk.HBox(spacing=20)
        self.hbox1 = Gtk.HBox(spacing=20)
        self.hbox2 = Gtk.HBox(spacing=20)
        self.frame.add(self.vbox)
        self.vbox.add(self.hbox0)
        self.vbox.add(self.hbox1)
        self.vbox.add(self.hbox2)
        self.items = []

    def add(self, key):
            if key == 'city':
                item = TextSelect('City',
                              self.schema.get_string(key))
                self.items.append(item)
                self.hbox1.add(item.actor)
                item.entry.connect('insert-at-cursor', set_text, self.schema, key)
            elif key == 'woeid':
                item = TextSelect('Enter WOEID',
                              self.schema.get_string(key))
                self.items.append(item)
                self.hbox1.add(item.actor)
                item.entry.connect('insert-at-cursor', set_text, self.schema, key)

            elif key == 'position-in-panel':
                item = Select('Position in Panel',
                          self.schema.get_enum(key),
                          ('Center', 'Right'))
	        self.items.append(item)
            	self.hbox0.add(item.actor)
 	        item.selector.connect('changed', set_enum, self.schema, key)
            elif key == 'unit':
                item = Select('Units',
                          self.schema.get_enum(key),
                          ('c', 'f'))
	        self.items.append(item)
            	self.hbox0.add(item.actor)
 	        item.selector.connect('changed', set_enum, self.schema, key)

            elif key == 'show-comment-in-panel':
                item = Gtk.CheckButton(label='Show comment in Panel')
		item.set_active(self.schema.get_boolean(key))
		self.items.append(item)
		self.hbox1.add(item)
		item.connect('toggled', set_boolean, self.schema, key)
            elif key == 'show-text-in-panel':
                item = Gtk.CheckButton(label='Show text in Panel')
		item.set_active(self.schema.get_boolean(key))
		self.items.append(item)
		self.hbox1.add(item)
		item.connect('toggled', set_boolean, self.schema, key)
            elif key == 'translate-condition':
                item = Gtk.CheckButton(label='Translate Conditions')
		item.set_active(self.schema.get_boolean(key))
		self.items.append(item)
		self.hbox1.add(item)
		item.connect('toggled', set_boolean, self.schema, key)
            elif key == 'use-symbolic-icons':
                item = Gtk.CheckButton(label='Use symbolic icons')
		item.set_active(self.schema.get_boolean(key))
		self.items.append(item)
		self.hbox1.add(item)
		item.connect('toggled', set_boolean, self.schema, key)



class App:
    opt = {}
    setting_items = ('location', 'appearences')

    def __init__(self):
        self.schema = Gio.Settings('org.gnome.shell.extensions.weather')
        keys = self.schema.keys()
        self.window = Gtk.Window(title='Weather Extension Configurator')
        self.window.connect('destroy', Gtk.main_quit)
        self.window.set_border_width(10)
        self.items = []
        self.settings = {}
        for setting in self.setting_items:
            self.settings[setting] = SettingFrame(
                up_first(setting), self.schema)

        self.main_vbox = Gtk.VBox(spacing=10)
        self.main_vbox.set_border_width(10)
        self.hbox1 = Gtk.HBox(spacing=20)
        self.hbox1.set_border_width(10)
        self.main_vbox.add(self.hbox1)
        self.window.add(self.main_vbox)

        for key in keys:
                sections = key.split('-')
                if sections[0] == 'city' or sections[0] == 'woeid':
                    self.settings['location'].add(key)
                else:
                    self.settings['appearences'].add(key)

        self.notebook = Gtk.Notebook()
        for setting in self.setting_items:
            self.notebook.append_page(
                self.settings[setting].frame, self.settings[setting].label)
        self.main_vbox.add(self.notebook)
        self.window.show_all()


def main():
    App()
    Gtk.main()

if __name__ == '__main__':
    main()
