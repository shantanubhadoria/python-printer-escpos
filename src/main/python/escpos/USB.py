"""
@author: Shantanu Bhadoria <shantanu@cpan.org>
@copyright: Copyright (c) Shantanu Bhadoria
@license: GPL

Synopsis
--------

    from escpos.USB import getUSBPrinter

    printer = printer = getUSBPrinter()(idVendor=0x1504, idProduct=0x0006)

    printer.text("Hello World\n")

To see the full range of commands available for Generic commandset see escpos.commandset.generic
"""

import usb.core
import usb.util
import importlib


def getUSBPrinter(commandSet='Generic'):
    """
    Return USB Printer Object while loading the specified command set.

    Synopsis
    --------
    printer = getUSBPrinter(commandSet='Generic')(idVendor=0x1504, idProduct=0x0006)

    Parameters
    ----------
    commandSet : str
                 Command set to load(default: 'Generic')
    Returns
    -------
    USBPrinter Class
        Returns USB Printer Class inheriting commands from the specified commandset


    USBPrinter Class Parameters
    ---------------------------
    idVendor       : 2 byte int(Can be provided in hex representation like 0x1504)
                     Vendor Id for the USB Device. Use lsusb on unix like OSes to get the hex value for this
    idProduct      : 2 byte int(Can be provided in hex representation like 0x1504)
                     Product Id for the USB Device. Use lsusb on unix like OSes to get the hex value for this
    interface      : number(hex), optional
                     USB device interface (default: 0)
                        lsusb -vvv -d <vendorId in hex>:<productId in hex> | grep iInterface
    inputEndPoint  : 1 byte int(Can be provided in hex representation like 0x82), optional
                     USB Input end point (default: 0x82)
                        lsusb -vvv -d <vendorId in hex>:<productId in hex> | grep bEndpointAddress | grep IN
    outputEndPoint : 1 byte int(Can be provided in hex representation like 0x01), optional
                     USB Output end point (default: 0x01)
                        lsusb -vvv -d <vendorId in hex>:<productId in hex> | grep bEndpointAddress | grep OUT
    initialize     : bool, optional
                     Initialize printer(call initialize()), default True
    """
    commandSetModule = importlib.import_module('..commandset.' + commandSet.lower(), __name__)
    commandSetClass = getattr(commandSetModule, commandSet)

    class USBPrinter(commandSetClass):
        """
        USB printer object

        Inherits dynamically from printer model commandSets based on available commandSets in escpos.commandset.*
        namespace by default Generic command set is loaded

        Attributes
        ----------
        device : USB device object
                 device object on which all the write and read operations are performed


        """
        device = None

        def __init__(self, idVendor, idProduct, interface=0, inputEndPoint=0x82, outputEndPoint=0x01, initialize=True):
            self.idVendor = idVendor
            self.idProduct = idProduct
            self.interface = interface
            self.inputEndPoint = inputEndPoint
            self.outputEndPoint = outputEndPoint

            self._open()
            if initialize:
                self.initialize()

        def text(self, text):
            """
            Essentially the same as _write(), Prints text to printer
            """
            self._write(text)

        def _open(self):
            """ Search device on USB tree and set it as escpos device """
            self.device = usb.core.find(idVendor=self.idVendor, idProduct=self.idProduct)

            if self.device is None:
                print "Cable isn't plugged in"

            if self.device.is_kernel_driver_active(0):
                try:
                    self.device.detach_kernel_driver(0)
                except usb.core.USBError as e:
                    print "Could not detach kernel driver: %s" % str(e)

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
