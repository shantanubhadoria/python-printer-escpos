import usb.core
import usb.util
import serial
import socket

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


    Return USBPrinter Class with the specified command set in the **escpos.commandset.*** namespace.

    **Usage**
    ::

        printer = getUSBPrinter(commandSet='Generic')(idVendor=0x1504, idProduct=0x0006)
        printer.text('Hello World')
        printer.lf()

    """
    commandSetModule = importlib.import_module('..commandset.' + commandSet.lower(), __name__)
    commandSetClass = getattr(commandSetModule, commandSet)

    class USBPrinter(commandSetClass):
        """
        USB printer class

        Inherits dynamically from printer model commandSets based on available commandSets in escpos.commandset.*
        namespace by default Generic command set is loaded

        """

        def __init__(self, idVendor, idProduct, interface=0, inputEndPoint=0x82, outputEndPoint=0x01, initialize=True):
            """
            :param int idVendor: 2 byte int(Can be provided in hex representation like 0x1504). Vendor Id for the USB \
            Device.
            :param int idProduct: 2 byte int(Can be provided in hex representation like 0x0006). Product Id for the \
            USB Device.
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
            """
            self.idVendor = idVendor
            self.idProduct = idProduct
            self.interface = interface
            self.inputEndPoint = inputEndPoint
            self.outputEndPoint = outputEndPoint

            self.__open()
            if initialize:
                self.initialize()

        def text(self, text):
            """
            Prints text to printer
            """
            self.__write(text)

        def __open(self):
            """
            Search device on USB tree and set it as escpos device
            """
            self._device = usb.core.find(idVendor=self.idVendor, idProduct=self.idProduct)

            if self._device is None:
                raise RuntimeError("Cable isn't plugged in")

            if self._device.is_kernel_driver_active(0):
                try:
                    self._device.detach_kernel_driver(0)
                except usb.core.USBError as e:
                    raise RuntimeError("Could not detach kernel driver: %s" % str(e))

            try:
                self._device.set_configuration()
                self._device.reset()
            except usb.core.USBError as e:
                raise RuntimeError("Could not set configuration: %s" % str(e))

        def __write(self, msg):
            """
            Print any command sent in raw format
            """
            self._device.write(self.outputEndPoint, msg, self.interface)

        def __read(self, length):
            """
            Read raw data from the USB device
            """
            self._device.read(self.inputEndPoint, length, self.interface)

        def __del__(self):
            """
            Release USB interface
            """
            if self._device:
                usb.util.dispose_resources(self._device)
            self._device = None

    return USBPrinter


def getSerialPrinter(commandSet='Generic'):
    """

    :param str commandSet: Command set to load from **escpos.commandset.*** namespace (default: 'Generic')


    :returns: SerialPrinter Class

    .. py:class:: SerialPrinter

        :param str dev: A string representing the device. For Unix like systems this would be a devicefile pointing \
        to the printer like `/dev/ttyS0`. For windows systems this would be a windows serial port address like `COM1`, \
        `COM2`, `COM3`. (default: /dev/ttyS0)
        :param int baudrate: Baudrate for your printer's serial port.(default: 9600)
        :param int bytesize: bytesize for each chunk of data sent over the serial port.
        :param int timeout: Timeout for the serial port.
        :param bool initialize: Call initialize() function to reset the printer to default status.(default: True)
        :returns: SerialPrinter object


    Return SerialPrinter Class with the specified command set in the **escpos.commandset.*** namespace.

    **Usage**
    ::

        printer = getSerialPrinter(commandSet='Generic')(dev='/dev/ttys2', baudrate=19200)
        printer.text('Hello World')
        printer.lf()

    """
    commandSetModule = importlib.import_module('..commandset.' + commandSet.lower(), __name__)
    commandSetClass = getattr(commandSetModule, commandSet)

    class SerialPrinter(commandSetClass):
        """
        Serial printer class

        Inherits dynamically from printer model commandSets based on available commandSets in escpos.commandset.*
        namespace by default Generic command set is loaded

        """

        def __init__(self, dev='/dev/ttyS0', baudrate=9600, bytesize=8, parity=serial.PARITY_NONE,
                     stopbits=serial.STOPBITS_ONE, timeout=1.00, dsrdtr=True, initialize=True):
            """
            :param str dev: A string representing the device. For Unix like systems this would be a devicefile \
            pointing to the printer like `/dev/ttyS0`. For windows systems this would be a windows serial port address \
            like `COM1`, `COM2`, `COM3`. (default: /dev/ttyS0)
            :param int baudrate: Baudrate for your printer's serial port.(default: 9600)
            :param int bytesize: buts of data sent in each chunk over the serial port. Possible values 5,6,7,8 \
            (default:8).
            :param int parity: serial device parity. Possible values serial.PARITY_NONE, serial.PARITY_EVEN, \
            serial.PARITY_ODD, serial.PARITY_MARK, serial.PARITY_SPACE (default: serial.PARITY_NONE)
            :param int stopbits: number of stopbits. Possible values serial.STOPBITS_ONE, \
            serial.STOPBITS_ONE_POINT_FIVE, serial.STOPBITS_TWO(default: serial.STOPBITS_ONE)
            :param float timeout: Timeout for the serial port(default: 1.00).
            :param bool dsrdtr: Enable hardware (DSR/DTR) flow control(default: True)
            :param bool initialize: Call initialize() function to reset the printer to default status.(default: True)
            """
            self.dev = dev
            self.baudrate = baudrate
            self.bytesize = bytesize
            self.parity = parity
            self.timeout = timeout
            self.dsrdtr = dsrdtr

            self.__open()
            if initialize:
                self.initialize()

        def text(self, text):
            """
            Prints text to printer
            """
            self.__write(text)

        def __open(self):
            """
            Setup serial device and set it as escpos device
            """
            self._device = serial.Serial(port=self.dev,
                                         baudrate=self.baudrate,
                                         bytesize=self.bytesize,
                                         parity=self.parity,
                                         stopbits=self.stopbits,
                                         timeout=self.timeout,
                                         dsrdtr=self.dsrdtr)

            if self._device is None:
                raise RuntimeError("Unable to open serial printer on %s" % self.dev)

        def __write(self, msg):
            """
            Print any command sent in raw format
            """
            self._device.write(msg)

        def __read(self, length):
            """
            Read raw data from the serial device
            """
            self._device.read(length)

        def __del__(self):
            """
            Release serial interface
            """
            if self._device is not None:
                self._device.close()
            self._device = None

    return SerialPrinter


def getNetworkPrinter(commandSet='Generic'):
    """

    :param str commandSet: Command set to load from **escpos.commandset.*** namespace (default: 'Generic')


    :returns: NetworkPrinter Class

    .. py:class:: NetworkPrinter

        :param str host: IP address or FQDN for the network escpos printer.
        :param str port: Network port number for your network escpos printer.(default: 9100)
        :param bool initialize: Call initialize() function to reset the printer to default status.(default: True)
        :returns: NetworkPrinter object


    Return NetworkPrinter Class with the specified command set in the **escpos.commandset.*** namespace.

    **Usage**
    ::

        printer = getNetworkPrinter(commandSet='Generic')(host='192.168.168.20', port=9200)
        printer.text('Hello World')
        printer.lf()

    """
    commandSetModule = importlib.import_module('..commandset.' + commandSet.lower(), __name__)
    commandSetClass = getattr(commandSetModule, commandSet)

    class NetworkPrinter(commandSetClass):
        """
        Network printer class

        Inherits dynamically from printer model commandSets based on available commandSets in escpos.commandset.*
        namespace by default Generic command set is loaded

        """

        def __init__(self, host, port=9100, initialize=True):
            """
            :param str host: ip address or fqdn for your printer.
            :param int port: Network port number for your printer.(default: 9100)
            :param bool initialize: Call initialize() function to reset the printer to default status.(default: True)
            """
            self.host = host
            self.port = port

            self.__open()
            if initialize:
                self.initialize()

        def text(self, text):
            """
            Prints text to printer
            """
            self.__write(text)

        def __open(self):
            """
            Setup network printer and set it as escpos printer
            """
            self._device = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._device.connect((self.host, self.port))

            if self._device is None:
                raise RuntimeError("Unable to connect to network printer on %s" % self.host)

        def __write(self, msg):
            """
            Print any command sent in raw format
            """
            self._device.send(msg)

        def __read(self, length):
            """
            Read raw data from the network printer
            """
            self._device.recv(length)

        def __del__(self):
            """
            Release network interface
            """
            if self._device is not None:
                self._device.close()
            self._device = None

    return NetworkPrinter


def getFilePrinter(commandSet='Generic'):
    """
    This method does not allow two way communication with the printer and status retiieval and read commands will not
    be available when using this connection format, so only use FilePrinter class if you are unable to use other printer
    conection classes.

    :param str commandSet: Command set to load from **escpos.commandset.*** namespace (default: 'Generic')


    :returns: FilePrinter Class

    .. py:class:: FilePrinter

        :param str dev: A string representing the device. For Unix like systems this would be a serial or USB devicefile
        pointing to the printer like `/dev/ttyS0`. (default: /dev/ttyS0)
        :param bool initialize: Call initialize() function to reset the printer to default status.(default: True)
        :returns: FilePrinter object

    Return FilePrinter Class with the specified command set in the **escpos.commandset.*** namespace.

    **Usage**
    ::

        printer = getFilePrinter(commandSet='Generic')(dev='/dev/ttys2')
        printer.text('Hello World')
        printer.lf()

    """
    commandSetModule = importlib.import_module('..commandset.' + commandSet.lower(), __name__)
    commandSetClass = getattr(commandSetModule, commandSet)

    class FilePrinter(commandSetClass):
        """
        File printer class

        Inherits dynamically from printer model commandSets based on available commandSets in escpos.commandset.*
        namespace by default Generic command set is loaded

        """

        def __init__(self, dev='/dev/ttyS0', initialize=True):
            """
            :param str dev: A string representing the device. For Unix like systems this would be a serial or USB \
            devicefile pointing to the printer like `/dev/ttyS0`. (default: /dev/ttyS0)
            :param bool initialize: Call initialize() function to reset the printer to default status.(default: True)
            """
            self.dev = dev

            self.__open()
            if initialize:
                self.initialize()

        def text(self, text):
            """
            Prints text to printer
            """
            self.__write(text)

        def __open(self):
            """
            Setup file handle and set it as escpos device
            """
            self._device = open(self.dev, "wb")

            if self._device is None:
                raise RuntimeError("Unable to open  printer file at %s" % self.dev)

        def __write(self, msg):
            """
            Print any command sent in raw format
            """
            self._device.write(msg)

        def __del__(self):
            """
            Release file handle
            """
            if self._device is not None:
                self._device.close()
            self._device = None

    return FilePrinter
