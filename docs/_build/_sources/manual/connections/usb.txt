USB Printers
============

.. image:: usb.jpeg
   :width: 400px

Getting the printer object::

    from escpos.connections import getUSBPrinter


    printer = getUSBPrinter()(idVendor=0x1504,  # USB vendor and product Ids for Bixolon SRP-350plus
                              idProduct=0x0006  # printer
                              inputEndPoint=0x82,
                              outputEndPoint=0x01)

    printer.text("Hello World")
    printer.lf()

As you might have noticed there are a few parameters used above for connecting to your USB escpos printer that you might
not be aware of. USB Printers require USB vendorID, productID, interface number, input endpoint id, output endpoint id
to create a connection. Read on to see how to get these values for your printer and create a printer object for a USB
printer

Getting vendor id and product id
--------------------------------

On Unix like OSes, make sure your printer is switched off and run lsusb command to see a list of devices with their
product id and vendor id::

    $ lsusb
    Bus 004 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
    Bus 003 Device 008: ID 0cf3:0036 Atheros Communications, Inc.

Now switch on your printer and run lsusb again::

    $ lsusb
    Bus 004 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
    Bus 003 Device 003: ID 1504:0006
    Bus 003 Device 008: ID 0cf3:0036 Atheros Communications, Inc.

The second device in this list is the thermal printer. I know this because if I switch off the printer and run lsusb
again that line will disappear. The vendor id and product id are in base16 format. That means the vendor id for my
printer is 0x1504 and product id is 0x0006

Getting interface id
--------------------

Following this you can get the interface number for your printer with the following command (Note
that I used the vendorid 1504 and productid 0006 for my printer that I discovered in the previous section)::

    $ lsusb -vvv -d 1504:0006 | grep iInterface
          iInterface              0

So the  interface number for my printer is 0, since the module uses a default interface number 0, I do not need to
specify this value in my constructor

Getting input endpoint
----------------------

Again you can use the lsusb to get the input endpoint as follows::

    $ lsusb -vvv -d 1504:0006 | grep bEndpointAddress | grep IN
    bEndpointAddress     0x81  EP 1 IN

That gives me the input endpoint number 0x81, this is also the default for the module.

Getting output endpoint
-----------------------

You can now use the lsusb to get the output endpoint as follows::

    $ lsusb -vvv -d 1504:0006 | grep bEndpointAddress | grep OUT
    bEndpointAddress     0x01  EP 1 OUT

That gives me the output endpoint number 0x01, this is also the default for the module.

Creating the printer object
---------------------------

Using the above values we can now create a printer object and start talking to our printer::

    from escpos.connections import getUSBPrinter


    printer = getUSBPrinter()(idVendor=0x1504,  # USB vendor and product Ids for Bixolon SRP-350plus
                              idProduct=0x0006  # printer
                              inputEndPoint=0x82,
                              outputEndPoint=0x01)

    printer.text("Hello World")
    printer.lf()
