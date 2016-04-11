"""
@author: Shantanu Bhadoria <shantanu@cpan.org>
@copyright: Copyright (c) Shantanu Bhadoria
@license: GPL
"""

import os
import usb.core
import usb.util
import importlib

def getUSBPrinter(commandSet='Generic'):

    # This is same as
    #
    #     from ..commandset.generic import Generic as commandSetClass
    #
    # when commandSet='Generic'
    commandSetModule = importlib.import_module('..commandset.' + commandSet.lower(), __name__)
    commandSetClass  = getattr(commandSetModule, commandSet)

    class USBPrinter(commandSetClass):
        """
        USB printer object

        inherits dynamically from printer model commandSets based on available commandSets in escpos.commandset.* namespace
        by default Generic command set is loaded
        """
        device     = None

        def __init__(self, idVendor, idProduct, interface=0, inputEndPoint=0x82, outputEndPoint=0x01):
            """
            @param idVendor       : Vendor ID
            @param idProduct      : Product ID
            @param interface      : USB device interface
            @param inputEndPoint  : Input end point
            @param outputEndPoint : Output end point
            """
            self.idVendor       = idVendor
            self.idProduct      = idProduct
            self.interface      = interface
            self.inputEndPoint  = inputEndPoint
            self.outputEndPoint = outputEndPoint

            self.open()


        def open(self):
            """ Search device on USB tree and set it as escpos device """
            self.device = usb.core.find(idVendor=self.idVendor, idProduct=self.idProduct)

            if self.device is None:
                print "Cable isn't plugged in"

            if self.device.is_kernel_driver_active(0):
                try:
                    self.device.detach_kernel_driver(0)
                except usb.core.USBError as e:
                    print "Could not detatch kernel driver: %s" % str(e)

            try:
                self.device.set_configuration()
                self.device.reset()
            except usb.core.USBError as e:
                print "Could not set configuration: %s" % str(e)


        def _write(self, msg):
            """ Print any command sent in raw format """
            self.device.write(self.outputEndPoint, msg, self.interface)


        def _raw(self, msg):
            """ Print any command sent in raw format """
            self.device.write(self.outputEndPoint, msg, self.interface)


        def _read(self, length):
            """ Read raw data from the USB device """
            self.device.read(self.inputEndPoint, length, self.interface)


        def __del__(self):
            """ Release USB interface """
            if self.device:
                usb.util.dispose_resources(self.device)
            self.device = None


    return USBPrinter
