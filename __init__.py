#!/usr/bin/env python3
#########################################################################
#  Copyright 2016 Raoul Thill                       raoul.thill@gmail.com
#########################################################################
#  This file is part of SmartHome.py.    http://mknx.github.io/smarthome/
#
#  SmartHome.py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHome.py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHome.py. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging
import requests
from lxml import etree
from io import StringIO

logger = logging.getLogger('')


class Yamaha:
    def __init__(self, smarthome):
        logger.warn('Init Yamaha')
        self._sh = smarthome
        self._yamaha_cmds = ['state', 'power', 'input', 'volume', 'mute']
        self._yamaha_rxv = {}

    def run(self):
        logger.info("Yamaha items loaded, now initializing.")
        for yamaha_host in self._yamaha_rxv.keys():
            self._update_state(yamaha_host)
        for yamaha_host, yamaha_cmd in self._yamaha_rxv.items():
            logger.info("Initializing items for host: {}".format(yamaha_host))
            state = self._yamaha_rxv[yamaha_host]['state']
            logger.debug(state())
            for yamaha_cmd, item in yamaha_cmd.items():
                if yamaha_cmd != 'state':
                    logger.info("Initializing cmd {} for item {}".format(yamaha_cmd, item))
                    value = self._return_value(state(), yamaha_cmd)
                    item(value, "Yamaha")
        self.alive = True

    def stop(self):
        self.alive = False

    def _return_document(self, doc):
        return etree.tostring(doc, xml_declaration=True, encoding='UTF-8', pretty_print=False)

    def _power(self, value):
        root = etree.Element('YAMAHA_AV')
        root.set('cmd', 'PUT')
        system = etree.SubElement(root, 'Main_Zone')
        power_control = etree.SubElement(system, 'Power_Control')
        power = etree.SubElement(power_control, 'Power')
        if value:
            power.text = 'On'
        else:
            power.text = 'Standby'
        tree = etree.ElementTree(root)
        return self._return_document(tree)

    def _select_input(self, value):
        root = etree.Element('YAMAHA_AV')
        root.set('cmd', 'PUT')
        system = etree.SubElement(root, 'Main_Zone')
        input = etree.SubElement(system, 'Input')
        input_sel = etree.SubElement(input, 'Input_Sel')
        input_sel.text = value
        tree = etree.ElementTree(root)
        return self._return_document(tree)

    def _set_volume(self, value):
        root = etree.Element('YAMAHA_AV')
        root.set('cmd', 'PUT')
        system = etree.SubElement(root, 'Main_Zone')
        volume = etree.SubElement(system, 'Volume')
        level = etree.SubElement(volume, 'Lvl')
        value = etree.SubElement(level, 'Val')
        value.text = str(value)
        exponent = etree.SubElement(level, 'Exp')
        exponent.text = '1'
        unit = etree.SubElement(level, 'Unit')
        unit.text = 'dB'
        tree = etree.ElementTree(root)
        return self._return_document(tree)

    def _mute(self, value):
        root = etree.Element('YAMAHA_AV')
        root.set('cmd', 'PUT')
        system = etree.SubElement(root, 'Main_Zone')
        volume = etree.SubElement(system, 'Volume')
        mute = etree.SubElement(volume, 'Mute')
        if value:
            mute.text = 'On'
        else:
            mute.text = 'Off'
        tree = etree.ElementTree(root)
        return self._return_document(tree)

    def _get_state(self):
        root = etree.Element('YAMAHA_AV')
        root.set('cmd', 'GET')
        system = etree.SubElement(root, 'Main_Zone')
        state = etree.SubElement(system, 'Basic_Status')
        state.text = 'GetParam'
        tree = etree.ElementTree(root)
        return self._return_document(tree)

    def _return_value(self, state, cmd):
        tree = etree.parse(StringIO(state))
        if cmd == 'input':
            value = tree.find('Main_Zone/Basic_Status/Input/Input_Sel')
            return value.text
        elif cmd == 'volume':
            value = tree.find('Main_Zone/Basic_Status/Volume/Lvl/Val')
            return int(value.text)
        elif cmd == 'mute':
            value = tree.find('Main_Zone/Basic_Status/Volume/Mute')
            if value.text == 'On':
                return True
            elif value.text == 'Off':
                return False
            return value.text
        elif cmd == 'power':
            value = tree.find('Main_Zone/Basic_Status/Power_Control/Power')
            if value.text == 'Standby':
                return False
            elif value.text == 'On':
                return True

    def _submit_payload(self, host, payload):
        logger.debug("Sending payload {}".format(payload))
        res = requests.post("http://%s/YamahaRemoteControl/ctrl" % host,
                            headers={
                                "Accept": "text/xml",
                                "User-Agent": "sh.py"
                            },
                            timeout=4,
                            data=payload)
        response = res.text
        del res
        return response

    def _lookup_host(self, item):
        parent = item.return_parent()
        yamaha_host = parent.conf['yamaha_host']
        return yamaha_host

    def parse_item(self, item):
        if 'yamaha_cmd' in item.conf:
            yamaha_host = self._lookup_host(item)
            yamaha_cmd = item.conf['yamaha_cmd'].lower()
            if not yamaha_cmd in self._yamaha_cmds:
                logger.warning("{} not in valid commands: {}".format(yamaha_cmd, self._yamaha_cmds))
                return None
            else:
                try:
                    self._yamaha_rxv[yamaha_host][yamaha_cmd] = item
                except KeyError:
                    self._yamaha_rxv[yamaha_host] = {}
                    self._yamaha_rxv[yamaha_host][yamaha_cmd] = item
            return self.update_item

    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != "Yamaha":
            yamaha_cmd = item.conf['yamaha_cmd']
            yamaha_host = self._lookup_host(item)
            yamaha_payload = None

            if yamaha_cmd == 'power':
                yamaha_payload = self._power(item())
            elif yamaha_cmd == 'volume':
                yamaha_payload = self._set_volume(item())
            elif yamaha_cmd == 'mute':
                yamaha_payload = self._mute(item())
            elif yamaha_cmd == 'input':
                yamaha_payload = self._select_input(item())

            self._submit_payload(yamaha_host, yamaha_payload)
            self._update_state(yamaha_host)
            return None

    def _update_state(self, yamaha_host):
        state = self._submit_payload(yamaha_host, self._get_state())
        item = self._yamaha_rxv[yamaha_host]['state']
        item(state, "Yamaha")
        return None
