"""
@author: Shantanu Bhadoria <shantanu@cpan.org>
@copyright: Copyright (c) Shantanu Bhadoria
@license: GPL
"""

import usb.core
import usb.util

from escpos.commands import Commands

class Printer(Commands):
    """ Define USB printer """

    def __init__(self, idVendor, idProduct, interface=0, inputEndPoint=0x82, outputEndPoint=0x01):
        """
        @param idVendor  : Vendor ID
        @param idProduct : Product ID
        @param interface : USB device interface
        @param inputEndPoint     : Input end point
        @param outputEndPoint    : Output end point
        """
        self.idVendor  = idVendor
        self.idProduct = idProduct
        self.interface = interface
        self.inputEndPoint     = inputEndPoint
        self.outputEndPoint    = outputEndPoint
        self.open()


    def open(self):
        """ Search device on USB tree and set is as escpos device """
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


    def _read(self, length):
        """ Read raw data from the USB device """
        self.device.read(self.inputEndPoint, msg, self.interface)


    def __del__(self):
        """ Release USB interface """
        if self.device:
            usb.util.dispose_resources(self.device)
        self.device = None
