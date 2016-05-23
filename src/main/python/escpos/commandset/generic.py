"""
Generic ESCPOS command set for escpos module. You can override Generic command set by writing a module specific to your
printer model in the **escpos.commandset.*** namespace as **escpos.commandset.examplecommands** and putting a class
named **ExampleCommands** in that package and define the special commands in methods of **ExampleCommands** class. Then
when initializing your printer pass ``commandSet='ExampleCommands'`` to getXXXPrinter function. For example to use
Generic commandset on a USB printer::

    printer = new getUSBPrinter(commandSet='Generic')(idVendor=0x1504, idProduct=0x0006)

"""


try:
    import Image
except ImportError:
    from PIL import Image


import qrcode


class Generic():
    """
    This is a generic(and default) commandset that works for most of the ESCPOS compliant printers.
    """

    # ESCPOS Codes
    __ESC = '\x1b'
    __GS = '\x1d'
    __DLE = '\x10'
    __FS = '\x1c'

    # Level 2 ESCPOS Codes
    __FF = '\x0c'
    __SP = '\x20'
    __EOT = '\x04'
    __DC4 = '\x14'

    # Barcode Codes
    __barcode_textPositionCode = {'none': chr(0), 'above': chr(1), 'below': chr(2), 'aboveandbelow': chr(3)}
    __barcode_fontCode = {'a': chr(0), 'b': chr(1)}
    __barcode_systemCode = {
        'UPC-A': 0,
        'UPC-E': 1,
        'JAN13': 2,
        'JAN8': 3,
        'CODE39': 4,
        'ITF': 5,
        'CODABAR': 6,
        'CODE93': 7,
        'CODE128': 8
    }

    # Text maps
    __fontMap = {'a': '\x00', 'b': '\x01', 'c': '\x02'}
    __alignMap = {'left': '\x00', 'center': '\x01', 'right': '\x02', 'full': '\x03'}

    # Image resize codes
    __imageSize = {
        '1x1': '\x1d\x76\x30\x00',
        '2w': '\x1d\x76\x30\x01',
        '2h': '\x1d\x76\x30\x02',
        '2x2': '\x1d\x76\x30\x03'
    }

    def __init__(self):
        # Command code configurations
        self.__usePrintMode = False
        self.__textFont = 'a'
        self.__textBold = False
        self.__textUnderline = False
        self.__textDoubleHeight = False
        self.__textDoubleWidth = False

    def align(self, align='left'):
        """
        Align printing to left, center, right or full justification. Some printers require a line feed before
        justification change for it to have effect. Always set justification at the beginning of a line.

        :param str align: Possible values 'left', 'center', 'right' or 'full' (default: 'left')

        **Example**::

            printer.lf()
            printer.align('center')
            printer.text('This text is center aligned')
            printer.lf()
            printer.align('right')
            printer.text('This text is right aligned')
            printer.lf()
            printer.align('left')
            printer.text('This text is left aligned')
            printer.lf()
            printer.align('full')
            printer.text('This text is full justified') # Only available in select models

        """
        if align not in ['left', 'center', 'right', 'full']:
            raise ValueError('align must be \'left\', \'center\', \'right\' or \'full\'')
        else:
            self.__write(self.__class__.__ESC + 'a' + self.__class__.__alignMap[align])

    def barcode(self, text="shantanu", textPosition='below', font='b', height=50, width=2, system='CODE93'):
        """
        Prints barcode to the Printer

        :param str text: Text to be printed as barcode
        :param str textPosition: Position of Human readable text for the barcode - 'none', 'above', 'below', \
        'aboveandbelow'
        :param str font: font for the Human readable text - 'a' or 'b'
        :param int height: Barcode height no of dots in vertical direction
        :param int width: Width of barcode - 2  => 0.25mm, 3 => 0.375mm, 4 => 0.5mm, 5 => 0.625mm, 6 => 0.75mm
        :param int system: Barcode system - 'UPC-A', 'UPC-E', 'JAN13', 'JAN8', 'CODE39', 'ITF', 'CODABAR', 'CODE93', \
        'CODE128'

        **Example**::

            printer.barcode(text='Shantanu', textPosition='below', font='b', height=100, width=2, system='CODE93')

        """
        # Setting position of HRI text relative to the barcode
        if textPosition.lower() in self.__class__.__barcode_textPositionCode.keys():
            self.__write(self.__class__.__GS + 'H' + self.__class__.__barcode_textPositionCode[textPosition.lower()])
        else:
            raise ValueError('Barcode text position must be \'none\', \'above\', \'below\' or \'aboveandbelow\'')

        # Setting the font
        if font.lower() in self.__class__.__barcode_fontCode.keys():
            self.__write(self.__class__.__GS + 'f' + self.__class__.__barcode_fontCode[font.lower()])
        else:
            raise ValueError('Barcode font must be \'a\' or \'b\'')

        # Setting the height
        if height >= 2:
            self.__write(self.__class__.__GS + 'h' + chr(height))
        else:
            raise ValueError('Barcode height %c not within range 2 to infinity' % (height,))

        # Setting the width
        if width >= 2 and width <= 6:
            self.__write(self.__class__.__GS + 'w' + chr(width))
        else:
            raise ValueError('Barcode width %c not within range 2 to 6' % (width,))

        # Setting barcode format/system
        if system.upper() in self.__class__.__barcode_systemCode.keys():
            self.__write(self.__class__.__GS + 'k' + chr(self.__class__.__barcode_systemCode[system.upper()] + 65))
        else:
            raise ValueError('Barcode system must be \'UPC-A\', \'UPC-E\', \'JAN13\', \'JAN8\', \'CODE39\', \'ITF\', \
            \'CODABAR\', \'CODE93\', \'CODE128\'')

        # Print the barcode
        self.__write(chr(len(text)) + text)

    def beep(self):
        """
        Make the printer make a beep, this is supported on almost all printers with beepers

        **Example**::

            printer.beep()

        """
        self.__write('\x07')

    def bold(self, bold=True):
        """
        Makes text emphasized or unemphasized (bold=False)

        :param bool bold: True for turning on bold font, False for switching to normal font weight (default: True)

        **Example**::

            printer.bold()
            printer.text('This text is bold text')
            printer.lf()
            printer.bold(False)
            printer.text('This text is not bold')
            printer.lf()

        """
        if type(bold) is not bool:
            raise ValueError('bold must be True or False')
        elif self.__usePrintMode:
            self.__textBold = bold
            self._updatePrintMode()
        elif bold:
            self.__write(self.__class__.__ESC + 'E\x01')
        else:
            self.__write(self.__class__.__ESC + 'E\x00')

    def charSpacing(self, charSpacing=0):
        """
        Set right-side character spacing

        :param int charSpacing: Char spacing, range from 1 to 256 (default: 0)

        **Example**::

            printer.charSpacing(1)
            printer.text('This text has normal right char spacing')
            printer.lf()
            printer.charSpacing(5)
            printer.text('This text has 5 right char spacing')
            printer.lf()

        """
        if not(0 < charSpacing < 257) or type(charSpacing) is not int:
            raise ValueError('charSpacing must be a int between 1 and 256')
        else:
            self.__write(self.__class__.__ESC + self.__class__.__SP + chr(charSpacing - 1))

    def color(self, color=0):
        """
        Most thermal printers support just one color, black. Some ESCPOS printers(especially dot matrix) also support a
        second color(usually red). A few rarer models also support upto 7 different colors. Do note that in many printer
        models, this command only works when the color is set at the beginning of a new line before any text is printed.

        :param int color: 0 for switching to primary color, a positive integer for switching to a secondary color \
        (default: 0)

        **Example**::

            printer.color()
            printer.text('This text is in primary color')
            printer.lf()
            printer.color(1)
            printer.text('This text is not in color 2')
            printer.lf()
            printer.color(3)
            printer.text('This text is not in color 3')
            printer.lf()

        """
        if color not in [0, 1, 2, 3, 4, 5, 6, 7]:
            raise ValueError('color must be a positive integer less than and 8 or 0')
        else:
            self.__write(self.__class__.__ESC + 'r' + chr(color))

    def cr(self):
        """
        Print and carriage return. When automatic line feed is enabled this method works the same as lf , else it is
        ignored.

        **Example**::

            printer.cr()

        """
        self.__write('\x0d')

    def cutPaper(self, cut='partial', feed=True):
        """
        Cuts the paper in escpos printers that support this function

        :param str cut: 'partial' or 'full' cut (default: 'partial')
        :param bool feed: True for feeding paper to cutting position before executing cut, false for cutting paper at \
        current position (default: True)

        **Example**::

            printer.cutPaper()

        """
        if cut not in ['partial', 'full']:
            raise ValueError('cut must be \'partial\' or \'full\'')
        elif type(feed) is not bool:
            raise ValueError('feed must be True or False')
        else:
            value = 0 if cut == 'full' else 1
            value += 65 if feed else 0
            self.__write(self.__class__.__GS + 'V' + chr(value))

    def disable(self):
        """
        Disable the printer. After a :meth:`disable` command the printer ignores all commands except :meth:`enable` or
        other real-time commands.

        **Example**::

            printer.disable()
            printer.ensable()

        """
        self.__write(self.__class__.__ESC + '=' + chr(2))

    def doubleHeight(self, doubleHeight=True):
        """
        Makes text double height, its recommended to use :meth:`textSize` for supported printers

        :param bool doubleHeight: True for turning on double height text, False for switching to normal height text \
        (default: True)

        **Example**::

            printer.doubleHeight()
            printer.text('This text is double height text')
            printer.lf()
            printer.doubleHeight(False)
            printer.text('This text is not double height')
            printer.lf()

        """
        if type(doubleHeight) is not bool:
            raise ValueError('doubleHeight must be True or False')
        elif self.__usePrintMode:
            self.__textDoubleHeight = doubleHeight
            self._updatePrintMode()

    def doubleStrike(self, doubleStrike=True):
        """
        Puts a double strike on the text

        :param bool doubleStrike: True for turning on font double strike, False for switching off font double strike \
        (default: True)

        **Example**::

            printer.doubleStrike()
            printer.text('This text is double strike text')
            printer.lf()
            printer.doubleStrike(False)
            printer.text('This text is not double strike')
            printer.lf()

        """
        if type(doubleStrike) is not bool:
            raise ValueError('doubleStrike must be True or False')
        elif doubleStrike:
            self.__write(self.__class__.__ESC + 'G' + '\x01')
        else:
            self.__write(self.__class__.__ESC + 'G' + '\x00')

    def doubleWidth(self, doubleWidth=True):
        """
        Makes text double width, its recommended to use :meth:`textSize` for supported printers

        :param bool doubleWidth: True for turning on double width text, False for switching to normal width text \
        (default: True)

        **Example**::

            printer.doubleWidth()
            printer.text('This text is double width text')
            printer.lf()
            printer.doubleWidth(False)
            printer.text('This text is not double width')
            printer.lf()

        """
        if type(doubleWidth) is not bool:
            raise ValueError('doubleWidth must be True or False')
        elif self.__usePrintMode:
            self.__textDoubleWidth = doubleWidth
            self._updatePrintMode()

    def drawerKickPulse(self, pin=0, time=8):
        """
        Generate pulse in real-time on one of the connectors, this is often connected to the cash drawer attached to
        cashier terminals.

        :param int pin: Pin to which the pulse must be sent this must be either 0 or 1 for pins 2 or 5 respectively \
        (default: 0)
        :param int time: Duration of the pulse in units of 100 ms (range: 1 - 8) (default: 8)

        **Example**::

            printer.drawerKickPulse()

        """
        self.__write(self.__class__.__DLE + self.__class__.__DC4 + '\x01' + chr(pin) + chr(time))

    def enable(self):
        """
        Enable the printer after a :meth:`disable` command

        **Example**::

            printer.disable()
            printer.enable()

        """
        self.__write(self.__class__.__ESC + '=' + chr(1))

    def font(self, font='a'):
        """
        Set printer font. Most printers support two fonts i.e. 'a' or 'b', some may support a third font 'c'

        :param str font: Font for the printer, default 'a'. The font may be either 'a', 'b' or 'c' (default:'a')

        **Example**::

            printer.font('b')
            printer.text('This text is in font b')
            printer.lf()
            printer.font('a')
            printer.text('This text is in font a')
            printer.lf()

        """
        if font not in self.__class__.__fontMap.keys():
            raise ValueError('font must be \'a\', \'b\', \'c\'')
        elif self.__usePrintMode:
            self.__textFont = font
            self._updatePrintMode()
        else:
            self.__write(self.__class__.__ESC + 'M' + self.__class__.__fontMap[font])

    def horizontalPosition(self, horizontalPosition=0):
        """
        Moves the horizontal print position relative to the left margin in 1/60th of inches. The printer ignores this
        command if the specified position is to the right of the right margin.

        :param int horizontalPosition: horizontal position from left margin in 1/60th of inches (default: 0)

        **Example**::

            printer.lf()
            printer.horizontalPosition(100)
            printer.text('This text starts at 1/6inches from left margin')

        """
        if not(0 <= horizontalPosition <= 4095) or type(horizontalPosition) is not int:
            raise ValueError('horizontalPosition must be a int between 0 and 4095 and not ' + str(horizontalPosition))
        else:
            nH = horizontalPosition >> 8
            nL = horizontalPosition - (nH << 8)
            self.__write(self.__class__.__ESC + '$' + chr(nL) + chr(nH))

    def image(self, path):
        """
        Print a image from a file

        :param str path: Path to the image file to be printed

        **Example**::

            printer.image('/home/shantanu/companylogo.gif')

        """
        im = Image.open(path).convert("RGB")
        # Convert the RGB image in printable image
        self._convert_and_print_image(im)

    def initialize(self):
        """
        Initializes the Printer. Clears the data in print buffer and resets the printer to the mode that was in effect
        when the power was turned on. This function is automatically called on creation of printer object unless
        specifically disabled.

        * Any macro definitions are not cleared.
        * Offline response selection is not cleared.
        * Contents of user NV memory are not cleared.
        * NV graphics (NV bit image) and NV user memory are not cleared.
        * The maintenance counter value is not affected by this command.
        * The specifying of offline response isn't cleared.

        **Example**::

            printer.initialize()

        """
        self.__write(self.__class__.__ESC + '@')

    def invert(self, invert=True):
        """
        Invert text colors printing, switches from black on white background to white on black background

        :param bool invert: True for turning on inverted colors, False for switching off inverted colors (default: True)

        **Example**::

            printer.invert()
            printer.text('This text is in inverted colors')
            printer.lf()
            printer.invert(False)
            printer.text('This text is not in inverted colors')
            printer.lf()

        """
        if type(invert) is not bool:
            raise ValueError('invert must be True or False')
        elif invert:
            self.__write(self.__class__.__GS + 'B' + '\x01')
        else:
            self.__write(self.__class__.__GS + 'B' + '\x00')

    def leftMargin(self, leftMargin=10):
        """
        Sets the left margin for printing. Set the left margin at the beginning of a line. The printer ignores any data
        preceding this command on the same line in the buffer.

        In page mode sets the left margin to leftMargin x (horizontal motion unit) from the left edge of the printable
        area

        :param int leftMargin: Left Margin, range: 0 to 65535. If the margin exceeds the printable area, the left \
        margin is automatically set to the maximum value of the printable area.

        **Example**::

            printer.lf()
            printer.leftMargin(30)
            printer.text('This text has left Margin of 30')

        """
        if not(0 <= leftMargin <= 65535) or type(leftMargin) is not int:
            raise ValueError('leftMargin must be a int between 0 and 65535')
        else:
            nH = leftMargin >> 8
            nL = leftMargin - (nH << 8)
            self.__write(self.__class__.__GS + 'L' + chr(nL) + chr(nH))

    def lf(self):
        """
        Line feed. Moves to the next line. You can substitute this method with printer.text('\\n')

        **Example**::

            printer.lf()

        """
        self.__write('\n')

    def lineSpacing(self, lineSpacing=30, commandSet='3'):
        """
        Set line character spacing, note that some printers may not support all commandsets for setting a line spacing.
        The most commonly available commandSet('3') is chosen by default.

        :param int lineSpacing: Line spacing, range from 0 to 255 when commandSet is '+' or '3', sets line spacing to \
        lineSpacing/360 of an inch if commandSet is '+', lineSpacing/180 of an inch if commandSet is '3' and \
        lineSpacing/60 of an inch if commandSet is 'A'  (default: 30)
        :param str commandSet: ESCPOS provides three aternate commands for setting line spacing i.e. '+', '3', 'A' \
        (default : '3').

        #. When commandSet is '+' lineSpacing is set to lineSpacing/360 of an inch, 0 <= lineSpacing <= 255
        #. when commandSet is '3' lineSpacing is set to lineSpacing/180 of an inch, 0 <= lineSpacing <= 255
        #. when commandSet is 'A' lineSpacing is set to lineSpacing/60 of an inch, 0 <= lineSpacing <= 85

        **Example**::

            printer.lineSpacing()
            printer.text('This text has 1/6 inch line spacing')
            printer.lf()
            printer.lineSpacing(5)
            printer.text('This text has 5/60 inch line spacing')
            printer.lf()

        """
        if commandSet not in ['+', '3', 'A']:
            raise ValueError('commandSet must be either \'+\', \'3\' or \'A\'')
        elif (commandSet == '+' or commandSet == '3') \
                and (not(0 <= lineSpacing <= 255) or type(lineSpacing) is not int):
            raise ValueError('lineSpacing must be a int between 0 and 255 when commandSet is \'+\' or \'3\'')
        elif commandSet == 'A' and (not(0 <= lineSpacing <= 85) or type(lineSpacing) is not int):
            raise ValueError('lineSpacing must be a int between 0 and 85 when commandSet is \'A\'')
        else:
            self.__write(self.__class__.__ESC + commandSet + chr(lineSpacing))

    def printAreaWidth(self, width=65535):
        """
        Set Print area width for the thermal printer, In Standard mode, sets the print area width to

            *width x basic calculated pitch*

        :param int width: 16 bits value range, i.e. int between 0 to 65535 specifying print area width in basic \
        calculated pitch

        This command is effective only when processed at the beginning of the line when standard mode is being used.
        Printable area width setting is effective until initialize is executed, the printer is reset, or the power is
        turned off.

        **Example**::

            printer.lf()
            printer.printAreaWidth(200)
            printer.text('Set print area width to 200')
            printer.lf()
            printer.text('1234567890123456789012345678901234567890123456789012345678901234567890')
            printer.printAreaWidth()

        """
        if type(width) is not int:
            raise ValueError("width must be a int")
        else:
            nH = width >> 8
            nL = width - (nH << 8)
            self.__write(self.__class__.__GS + 'W' + chr(nL) + chr(nH))

    def qr(self, text):
        """
        Print QR Code for the provided string

        :param str text: Text to be printed to the QR code

        **Example**::

            printer.qr('My name is Shantanu Bhadoria')
            printer.qr('WIFI:T:WPA;S:ShantanusWifi;P:wifipasswordhere;;')  # Create a QR code for connecting to a Wifi

        """
        qr_code = qrcode.QRCode(version=4, box_size=4, border=1)
        qr_code.add_data(text)
        qr_code.make(fit=True)
        im = qr_code.make_image()._img.convert("RGB")
        # Convert the RGB image in printable image
        self._convert_and_print_image(im)

    def rotate90(self, rotate=True):
        """
        Rotates printing by 90 degrees

        :param bool rotate: Rotate by 90 degrees if True, else set to normal style (default: True)

        **Example**::

            printer.lf()
            printer.rotate90(100)
            printer.text('This text is rotated 90 degrees')

        """
        self.__write(self.__class__.__ESC + 'V' + ('\x01' if rotate else '\x00'))

    def tab(self):
        """
        Moves the cursor to next horizontal tab position like a '\\t'. This command is ignored unless the next
        horizontal tab position has been set. You may substitute this command with a printer.text('\\t') as well. See
        tabPositions() to understand the best way to use tabs to print out beautiul receipts.

        **Example**::

            printer.tab()

        """
        self.__write('\t')

    def tabPositions(self, positions=[8, 16, 24, 32, 40]):
        """
        Set tab positions for printer. Each tab() will move the cursor to the next tab position. This is useful when
        printing receipts and bills as this allows you to set one tab position for the prices. so after printing the plu
        name, add a tab to immediately move to the tab position to print the price. e.g.

        :param list positions: A list of **int(s)** specifying tab positions e.g. [8,16,24,32,40]

        **Example**::

            printer.tabPositions([3, 32])
            for plu in plus:
                printer.text(plu.quantity)
                printer.tab()
                printer.text(' x ' + plu.name)
                printer.tab()
                printer.text('$' + plu.price)

        This would print a well aligned receipt like so::

            10 x Guiness Beer              $24.00
            2  x Pizza                     $500.50
            1  x Tandoori Chicken          $50.20

        """
        chrPositions = ''
        for position in positions:
            chrPositions += chr(position)
        self.write(self.__class__.__ESC + 'D' + chrPositions + chr(0))

    def textSize(self, height=1, width=1):
        """
        Sets font text Size. Note that many printers will not support the full range of text heights and widths, e.g.
        many models may only support a maximum height and width of 8

        :param int height: Text height, range from 1 to 16 (default: 0)
        :param int width: Text width, range from 1 to 16 (default: 0)

        **Example**::

            printer.textSize(2,3)
            printer.text('This text is double height and thrice the width')
            printer.lf()
            printer.textSize(1,4)
            printer.text('This text is normal height and quadruple width')
            printer.lf()

        """
        if not(0 < height < 17) or type(height) is not int:
            raise ValueError('height must be a int between 1 and 16')
        if not(0 < width < 17) or type(width) is not int:
            raise ValueError('textWidth must be a int between 1 and 16')
        else:
            size = (width - 1) << 4 | (height - 1)
            self.__write(self.__class__.__GS + '!' + chr(size))

    def underline(self, underline=True, doubleDot=False):
        """
        Puts a underline under the text

        :param bool underline: True for turning on font underline, False for switching off font underline (default: \
        True)
        :param bool doubleDot: True for double dot width underline, False for single dot width underline (default : \
        False).

        **Example**::

            printer.underline()
            printer.text('This text is underlined text')
            printer.lf()
            printer.underline(True,True)
            printer.text('This text is double dot width underlined text')
            printer.lf()
            printer.underline(False)
            printer.text('This text is not underlined')
            printer.lf()

        """
        if type(underline) is not bool:
            raise ValueError('underline must be True or False')
        elif type(doubleDot) is not bool:
            raise ValueError('doubleDot must be True or False')
        elif self.__usePrintMode:
            self.__textUnderline = underline
            self._updatePrintMode()
        elif underline and doubleDot:
            self.__write(self.__class__.__ESC + '-\x02')
        elif underline:
            self.__write(self.__class__.__ESC + '-\x01')
        else:
            self.__write(self.__class__.__ESC + '-\x00')

    def upsideDown(self, upsideDown=True):
        """
        Upside down text printing

        :param bool upsideDown: True for turning on upside down printing, False for switching off upside down printing \
        (default: True)

        **Example**::

            printer.upsideDown()
            printer.text('This text is upside down')
            printer.lf()
            printer.upsideDown(False)
            printer.text('This text is not upside down')
            printer.lf()

        """
        if type(upsideDown) is not bool:
            raise ValueError('upsideDown must be True or False')
        else:
            self.__write(self.__class__.__ESC + '{' + ('\x01' if upsideDown else '\x00'))

    def _updatePrintMode(self):
        value = ('1' if self.__textFont == 'b' else '0') + '00' + ('1' if self.__textBold else '0') + \
                ('1' if self.__textDoubleHeight else '0') + ('1' if self.__textDoubleWidth else '0') + \
                ('1' if self.__textUnderline else '0')
        self.__write(self.__class__.__ESC + '!' + chr(int(value, 2)))

    def _check_image_size(self, size):
        """
        Check and fix the size of the image to 32 bits, you should not call this method directly
        """
        if size % 32 == 0:
            return (0, 0)
        else:
            imageBorder = 32 - (size % 32)
            if (imageBorder % 2) == 0:
                return (imageBorder / 2, imageBorder / 2)
            else:
                return (imageBorder / 2, (imageBorder / 2) + 1)

    def _print_image(self, line, size):
        """
        Print formatted image to the printer, you should not call this method directly
        """
        i = 0
        cont = 0
        buffer = ""

        self.__write(self.__class__.__imageSize['1x1'])
        buffer = "%02X%02X%02X%02X" % (((size[0] / size[1]) / 8), 0, size[1], 0)
        self.__write(buffer.decode('hex'))
        buffer = ""

        while i < len(line):
            hex_string = int(line[i:i + 8], 2)
            buffer += "%02X" % hex_string
            i += 8
            cont += 1
            if cont % 4 == 0:
                self.__write(buffer.decode("hex"))
                buffer = ""
                cont = 0

    def _convert_and_print_image(self, im):
        """
        Parse image and prepare it to a printable format
        """
        pixLine = ""
        imLeft = ""
        imRight = ""
        switch = 0
        imgSize = [0, 0]

        if im.size[0] > 512:
            print ("WARNING: Image is wider than 512 and could be truncated at print time ")
        if im.size[1] > 255:
            raise ValueError("Image Height larger than 255")

        imBorder = self._check_image_size(im.size[0])
        for i in range(imBorder[0]):
            imLeft += "0"
        for i in range(imBorder[1]):
            imRight += "0"

        for y in range(im.size[1]):
            imgSize[1] += 1
            pixLine += imLeft
            imgSize[0] += imBorder[0]
            for x in range(im.size[0]):
                imgSize[0] += 1
                RGB = im.getpixel((x, y))
                imColor = (RGB[0] + RGB[1] + RGB[2])
                imPattern = "1X0"
                patternLen = len(imPattern)
                switch = (switch - 1) * (-1)
                for x in range(patternLen):
                    if imColor <= (255 * 3 / patternLen * (x + 1)):
                        if imPattern[x] == "X":
                            pixLine += "%d" % switch
                        else:
                            pixLine += imPattern[x]
                        break
                    elif imColor > (255 * 3 / patternLen * patternLen) and imColor <= (255 * 3):
                        pixLine += imPattern[-1]
                        break
            pixLine += imRight
            imgSize[0] += imBorder[1]

        self._print_image(pixLine, imgSize)
