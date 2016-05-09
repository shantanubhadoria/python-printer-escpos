Network Printers
================

Getting the printer object::

    from escpos.connections import getNetworkPrinter


    printer = getNetworkPrinter()(host='192.168.0.20', port=9100)

    printer.text("Hello World")
    printer.lf()

Connecting to escpos printer on a network is ridiculously simple. Just provide the IP address and port(default 9100
mostly works) and you are set!
