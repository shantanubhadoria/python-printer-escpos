Use Printer device file directly on UNIX like OSes
==================================================

Getting the printer object::

    from escpos.connections import getFilePrinter


    printer = getFilePrinter()(dev='/dev/ttys2')

    printer.text("Hello World")
    printer.lf()

If you are unable to figure out the connections and your printing needs are quiet simple then you can print directly to
the unix device file of the printer which is usually present in the /dev folder. Printing this way will prevent you from
reading printer status etc. which is not required in most cases. However only use the method as a last resort because in
some cases certain OSes might assign your printer a new device file name everytime it is disconnected or OS is restarted
