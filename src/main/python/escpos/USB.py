import usb.core
import usb.util
import importlib


def getUSBPrinter(commandSet='Generic'):
    """

    :param str commandSet: Command set to load from **escpos.commandset.*** namespace (default: 'Generic')


    :returns: USBPrinter Class

    .. py:class:: USBPrinter

        :param int idVendor: 2 byte int(Can be provided in hex representation like 0x1504). Vendor Id for the USB \
        Device.
        :param int idProduct: 2 byte int(Can be provided in hex representation like 0x0006). Product Id for the USB \
        Device.
        :param int interface: number(hex), USB Input end point \
            Retrieve this value with the following command on UNIX like OSes (default: 0)

            ``lsusb -vvv -d <vendorId in hex>:<productId in hex> | grep iInterface``
        :param int inputEndPoint: 1 byte int(Can be provided in hex representation like 0x82), USB Input \
        end point. Retrieve this value with the following command on UNIX like OSes (default: 0x82)

            ``lsusb -vvv -d <vendorId in hex>:<productId in hex> | grep bEndpointAddress | grep IN``
        :param int outputEndPoint: 1 byte int(Can be provided in hex representation like 0x01), USB Output \
        end point. Retrieve this value with the following command on UNIX like OSes (default: 0x01)

            ``lsusb -vvv -d <vendorId in hex>:<productId in hex> | grep bEndpointAddress | grep OUT``
        :param bool initialize: Call initialize() function to reset the printer to default status.(default: True)
        :returns: USBPrinter object


    Return USB Printer Class with the specified command set in the **escpos.commandset.*** namespace.

    **Usage**
    ::

        printer = getUSBPrinter(commandSet='Generic')(idVendor=0x1504, idProduct=0x0006)

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
