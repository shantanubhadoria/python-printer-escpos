"""
@author: Shantanu Bhadoria <shantanu@cpan.org>
@copyright: Copyright (c) Shantanu Bhadoria
@license: GPL

Generic ESCPOS command set for escpos module. You can override Generic command set by writing a module specific to your
printer model in the escpos.commandset.* namespace as escpos.commandset.examplecommands and putting a class named
ExampleCommands in that package and define the special commands in methods of ExampleCommands class. Then when
initializing your printer pass commandSet='ExampleCommands' to getXXXPrinter function:

printer = new getUSBPrinter(commandSet='ExampleCommands')(idVendor=0x1504, idProduct=0x0006)
"""


try:
    import Image
except ImportError:
    from PIL import Image


import qrcode


class Generic():
    # ESCPOS Codes
    _ESC = '\x1b'
    _GS = '\x1d'
    _DLE = '\x10'
    _FS = '\x1c'

    # Level 2 ESCPOS Codes
    _FF = '\x0c'
    _SP = '\x20'
    _EOT = '\x04'
    _DC4 = '\x14'

    # Barcode Codes
    _barcode_textPositionCode = {'none': chr(0), 'above': chr(1), 'below': chr(2), 'aboveandbelow': chr(3)}
    _barcode_fontCode = {'a': chr(0), 'b': chr(1)}
    _barcode_systemCode = {
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

    # Image resize codes
    _image_size = {
        '1x1': '\x1d\x76\x30\x00',
        '2w': '\x1d\x76\x30\x01',
        '2h': '\x1d\x76\x30\x02',
        '2x2': '\x1d\x76\x30\x03'
    }

    def initialize(self):
        """
        Initializes the Printer. Clears the data in print buffer and resets the printer to the mode that was in effect
        when the power was turned on. This function is automatically called on creation of printer object.

        * Any macro definitions are not cleared.
        * Offline response selection is not cleared.
        * Contents of user NV memory are not cleared.
        * NV graphics (NV bit image) and NV user memory are not cleared.
        * The maintenance counter value is not affected by this command.
        * The specifying of offline response isn't cleared.
        """
        self._write(self._ESC + '@')

    def enable(self):
        """
        Enable the printer after a disable command
        """
        self._write(self._ESC + '=' + chr(1))

    def disable(self):
        """
        Disable the printer. After a disable command the printer ignores all commands except enable() or other real-time
        commands.
        """
        self._write(self._ESC + '=' + chr(1))

    def setPrintAreaWidth(self, nL=65, nH=2):
        """
        Set Print area width for the thermal printer, In Standard mode, sets the print area width to

            (nL + (nH x 256)) x (horizontal motion unit)

        Printable area width setting is effective until init is executed, the printer is reset, or the power is turned
        off.

        @param nL          : lower 4 bits value, range between 0 to 255
        @param nH          : higher 4 bits value, range between 0 to 255
        """
        self.lf()
        self.write(self._GS + 'W' + chr(nL) + chr(nH))

    def setTabPositions(self, positions=[8, 16, 24, 32, 40]):
        """
        Set tab positions for printer. Each tab() will move the cursor to the next tab position. This is useful when
        printing receipts and bills as this allows you to set one tab position for the prices. so after printing the plu
        name, add a tab to immediately move to the tab position to print the price. e.g.

            printer.tabPositions([5, 32])
            for plu in plus:
                printer.text(plu.quantity)
                printer.text(' x ' + plu.name)
                printer.tab()
                printer.text('$' + plu.price)

        This would print a well aligned receipt like so:

            2  x Guiness Beer              $24.00
            23 x Pizza                     $500.50
            1  x Tandoori Chicken          $50.20

        @param positions : a list of numbers specifying tab positions e.g. [8,16,24,32,40]
        """
        chrPositions = ''
        for position in positions:
            chrPositions += chr(position)
        self.write(self._ESC + 'D' + chrPositions + chr(0))

    def tab(self):
        """
        Moves the cursor to next horizontal tab position like a '\\t'. This command is ignored unless the next
        horizontal tab position has been set. You may substitute this command with a printer.text('\\t') as well. See
        tabPositions() to understand the best way to use tabs to print out beautiul receipts.
        """
        self._write('\t')

    def lf(self):
        """
        Line feed. Moves to the next line. You can substitute this method with printer.text('\\n')
        """
        self.write('\n')

    def ff(self):
        """
        Form feed. When in page mode, print data in the buffer and return back to standard mode
        """
        self._write('\x0c')

    def cr(self):
        """
        Print and carriage return. When automatic line feed is enabled this method works the same as lf , else it is
        ignored.
        """
        self._write('\x0d')

    def cancel(self):
        """
        Cancel (delete) page data when in page mode
        """
        self._write('\x18')

    def font(self, font='a'):
        """
        Set printer font. Most printers support two fonts i.e. 'a' or 'b', some may support a third font 'c'

        @param font : Font for the printer, default 'a'. font may be either 'a', 'b' or 'c'
        """
        fontMap = {'a': '\x00', 'b': '\x01', 'c': '\x02'}
        if font in fontMap.keys():
            self._write(self._ESC + 'M' + fontMap[font])
        else:
            raise ValueError('font must be \'a\', \'b\', \'c\'')

    def bold(self, bold=True):
        """
        Makes text emphasized or unemphasized (bold=False)

        @param bold : Boolean
        """

    def image(self, path):
        """
        Print a image from a file

        @param path : path to the image file to be printed
        """
        im = Image.open(path).convert("RGB")
        # Convert the RGB image in printable image
        self._convert_and_print_image(im)

    def qr(self, text):
        """
        Print QR Code for the provided string

        @param text : Text to be printed to the QR code
        """
        qr_code = qrcode.QRCode(version=4, box_size=4, border=1)
        qr_code.add_data(text)
        qr_code.make(fit=True)
        im = qr_code.make_image()._img.convert("RGB")
        # Convert the RGB image in printable image
        self._convert_and_print_image(im)

    def barcode(self, text="shantanu", textPosition='below', font='b', height=50, width=2, system='CODE93'):
        """
        Print barcode

        @param text          : Text to be printed as barcode
        @param textPosition  : Position of Human readable text for the barcode - 'none', 'above', 'below',
                               'aboveandbelow'
        @param font          : font for the Human readable text - 'a' or 'b'
        @param height        : Barcode height no of dots in vertical direction
        @param width         : Width of barcode - 2  => 0.25mm, 3 => 0.375mm, 4 => 0.5mm, 5 => 0.625mm, 6 => 0.75mm
        @param system        : Barcode system - 'UPC-A', 'UPC-E', 'JAN13', 'JAN8', 'CODE39', 'ITF', 'CODABAR', 'CODE93',
                               'CODE128'
        """
        # Setting position of HRI text relative to the barcode
        if textPosition.lower() in self._barcode_textPositionCode.keys():
            self._write(self._GS + 'H' + self._barcode_textPositionCode[textPosition.lower()])
        else:
            raise ValueError('Barcode text position must be \'none\', \'above\', \'below\' or \'aboveandbelow\'')

        # Setting the font
        if font.lower() in self._barcode_fontCode.keys():
            self._write(self._GS + 'f' + self._barcode_fontCode[font.lower()])
        else:
            raise ValueError('Barcode font must be \'a\' or \'b\'')

        # Setting the height
        if height >= 2:
            self._write(self._GS + 'h' + chr(height))
        else:
            raise ValueError('Barcode height %c not within range 2 to infinity' % (height,))

        # Setting the width
        if width >= 2 and width <= 6:
            self._write(self._GS + 'w' + chr(width))
        else:
            raise ValueError('Barcode width %c not within range 2 to 6' % (width,))

        # Setting barcode format/system
        if system.upper() in self._barcode_systemCode.keys():
            self._write(self._GS + 'k' + chr(self._barcode_systemCode[system.upper()] + 65))
        else:
            raise ValueError('Barcode system must be \'UPC-A\', \'UPC-E\', \'JAN13\', \'JAN8\', \'CODE39\', \'ITF\', \
            \'CODABAR\', \'CODE93\', \'CODE128\'')

        # Print the barcode
        self._write(chr(len(text)) + text)

    def _check_image_size(self, size):
        """
        Check and fix the size of the image to 32 bits, you should not call this method directly
        """
        if size % 32 == 0:
            return (0, 0)
        else:
            image_border = 32 - (size % 32)
            if (image_border % 2) == 0:
                return (image_border / 2, image_border / 2)
            else:
                return (image_border / 2, (image_border / 2) + 1)

    def _print_image(self, line, size):
        """
        Print formatted image to the printer, you should not call this method directly
        """
        i = 0
        cont = 0
        buffer = ""

        self._write(self._image_size['1x1'])
        buffer = "%02X%02X%02X%02X" % (((size[0] / size[1]) / 8), 0, size[1], 0)
        self._write(buffer.decode('hex'))
        buffer = ""

        while i < len(line):
            hex_string = int(line[i:i + 8], 2)
            buffer += "%02X" % hex_string
            i += 8
            cont += 1
            if cont % 4 == 0:
                self._write(buffer.decode("hex"))
                buffer = ""
                cont = 0

    def _convert_and_print_image(self, im):
        """
        Parse image and prepare it to a printable format
        """
        pix_line = ""
        im_left = ""
        im_right = ""
        switch = 0
        img_size = [0, 0]

        if im.size[0] > 512:
            print ("WARNING: Image is wider than 512 and could be truncated at print time ")
        if im.size[1] > 255:
            raise ValueError("Image Height larger than 255")

        im_border = self._check_image_size(im.size[0])
        for i in range(im_border[0]):
            im_left += "0"
        for i in range(im_border[1]):
            im_right += "0"

        for y in range(im.size[1]):
            img_size[1] += 1
            pix_line += im_left
            img_size[0] += im_border[0]
            for x in range(im.size[0]):
                img_size[0] += 1
                RGB = im.getpixel((x, y))
                im_color = (RGB[0] + RGB[1] + RGB[2])
                im_pattern = "1X0"
                pattern_len = len(im_pattern)
                switch = (switch - 1) * (-1)
                for x in range(pattern_len):
                    if im_color <= (255 * 3 / pattern_len * (x + 1)):
                        if im_pattern[x] == "X":
                            pix_line += "%d" % switch
                        else:
                            pix_line += im_pattern[x]
                        break
                    elif im_color > (255 * 3 / pattern_len * pattern_len) and im_color <= (255 * 3):
                        pix_line += im_pattern[-1]
                        break
            pix_line += im_right
            img_size[0] += im_border[1]

        self._print_image(pix_line, img_size)
