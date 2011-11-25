#encoding:utf-8
#       client.py
#
#       Copyright 2011 nicolas <nicolas@jombi.fr>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
import xmlrpclib
import socket
from datetime import date

import tvrage.api
from canape.object import Serie, Episode

from console import ConsoleApp, command, option, make_option


def prepare_serie(name, snum, enum, subtitle=None, quality=None):
    show = tvrage.api.Show(name)
    ep = Episode(snum=str(snum), enum=str(enum))
    started = show.started
    ended = show.ended or date.today().year
    datesstr = "%s-%s" % (started, ended)
    serie = Serie(name=show.name, id_=show.showid, episodes=[ep], quality=quality, subtitle=subtitle, datesstr=datesstr )
    return serie

class CanapeClient(ConsoleApp):

    prompt = "\x1b[1m\x1b[35mCanape>\x1b[0m "

    def __init__(self):
        ConsoleApp.__init__(self)
        self.server = xmlrpclib.ServerProxy('http://localhost:8080', allow_none=True)

    @command('ls','list')
    def get_series(self, arg):
        """ List series from database """
        try:
            results = self.server.get_series()
        except socket.error:
            print "Network error check your config"
            return True
        for r in results:
            print r

        return False

    @command('add')
    @option([make_option("-n", "--name", action="store", type="string", dest="name"),
             make_option("-s", "--snum", action="store", type="int", dest="snum"),
             make_option("-e", "--enum", action="store", type="int", dest="enum"),
             make_option("--subtitle", action="store", type="string", dest="subtitle", default=None),
             make_option("--quality", action="store", type="string", dest="quality", default=None)
            ])
    def add_serie(self, arg, opts):
        """ Add a serie to the database, you must specify serie's name,
        and episode's number and season from wich you want to start download """
        if None in (opts.name, opts.snum, opts.enum):
            print "You need specify  name snum and enum"
            return False
        serie = prepare_serie(opts.name, opts.snum, opts.enum, opts.subtitle, opts.quality)
        try:
            results = self.server.add_serie(serie)
        except socket.error:
            print "Network error check your config"
            return True
        return False

    @command('rm')
    @option([make_option("-n", "--name", action="store", type="string", dest="name"),
            ])
    def rm_serie(self, arg, opts):
        """ Remove a serie from the database, you must specify serie's name"""
        serie = Serie(opts.name)
        try:
            results = self.server.del_serie(serie)
        except socket.error:
            print "Network error check your config"
            return True
        return False


    @command('q', 'quit', 'bye')
    def quit(self, *ignored): return True

if __name__ == '__main__':
    app = CanapeClient()
    app.cmdloop()
