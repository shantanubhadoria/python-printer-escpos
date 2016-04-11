"""
@author: Shantanu Bhadoria <shantanu@cpan.org>
@copyright: Copyright (c) Shantanu Bhadoria
@license: GPL
"""


try:
    import Image
except ImportError:
    from PIL import Image


import qrcode



class Generic():
    # ESCPOS Codes
    _ESC = '\x1b'
    _GS  = '\x1d'
    _DLE = '\x10'
    _FS  = '\x1c'

    # Level 2 ESCPOS Codes
    _FF  = '\x0c'
    _SP  = '\x20'
    _EOT = '\x04'
    _DC4 = '\x14'

    # Text format

    # Barcode Codes
    _barcode_textPositionCode = {'none': chr(0), 'above': chr(1), 'below': chr(2), 'aboveandbelow': chr(3)}
    _barcode_fontCode         = {'a': chr(0), 'b': chr(1)}
    _barcode_systemCode       = {'UPC-A': 0, 'UPC-E': 1,'JAN13': 2, 'JAN8': 3, 'CODE39': 4, 'ITF': 5, 'CODABAR': 6, 'CODE93': 7, 'CODE128': 8}

    # Image resize codes
    _image_size = {'1x1': '\x1d\x76\x30\x00', '2w': '\x1d\x76\x30\x01', '2h': '\x1d\x76\x30\x02', '2x2': '\x1d\x76\x30\x03'}

    blah = 'blah'



    def __getattr__(self, key):
        try:
            value = getattr(self, key)
            print value
        except AttributeError as f:
            raise f



    def image(self,path_img):
        """ Open image file """
        im = Image.open(path_img).convert("RGB")
        # Convert the RGB image in printable image
        self._convert_and_print_image(im)



    def qr(self,text):
        """ Print QR Code for the provided string """
        qr_code = qrcode.QRCode(version=4, box_size=4, border=1)
        qr_code.add_data(text)
        qr_code.make(fit=True)
        im = qr_code.make_image()._img.convert("RGB")
        # Convert the RGB image in printable image
        self._convert_and_print_image(im)



    def barcode(self, text="shantanu", textPosition='below', font='b', height=50, width=2, system='CODE93'):
        """ Print Barcode
        @param text          : Text to be printed as barcode
        @param textPosition  : Position of Human readable text for the barcode - 'none', 'above', 'below', 'aboveandbelow'
        @param font          : font for the Human readable text - 'a' or 'b'
        @param height        : Barcode height no of dots in vertical direction
        @param width         : Width of barcode - 2  => 0.25mm, 3 => 0.375mm, 4 => 0.5mm, 5 => 0.625mm, 6 => 0.75mm
        @param system        : Barcode system - 'UPC-A', 'UPC-E', 'JAN13', 'JAN8', 'CODE39', 'ITF', 'CODABAR', 'CODE93', 'CODE128'
        """
        # Setting position of HRI text relative to the barcode
        if textPosition.lower() in self._barcode_textPositionCode.keys():
            self._write(self._GS + 'H' + self._barcode_textPositionCode[textPosition.lower()])
        else:
            raise ValueError('Barcode text position must be "none", "above", "below" or "aboveandbelow"')

        # Setting the font
        if font.lower() in self._barcode_fontCode.keys():
            self._write(self._GS + 'f' + self._barcode_fontCode[font.lower()])
        else:
            raise ValueError('Barcode font must be "a" or "b"')

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
            raise ValueError('Barcode system must be "UPC-A", "UPC-E", "JAN13", "JAN8", "CODE39", "ITF", "CODABAR", "CODE93", "CODE128"')

        # Print the barcode
        self._write(chr(len(text)) + text)



    def _check_image_size(self, size):
        """ Check and fix the size of the image to 32 bits """
        if size % 32 == 0:
            return (0, 0)
        else:
            image_border = 32 - (size % 32)
            if (image_border % 2) == 0:
                return (image_border / 2, image_border / 2)
            else:
                return (image_border / 2, (image_border / 2) + 1)



    def _print_image(self, line, size):
        """ Print formatted image """
        i = 0
        cont = 0
        buffer = ""

        self._write(self._image_size['1x1'])
        buffer = "%02X%02X%02X%02X" % (((size[0]/size[1])/8), 0, size[1], 0)
        self._write(buffer.decode('hex'))
        buffer = ""

        while i < len(line):
            hex_string = int(line[i:i+8],2)
            buffer += "%02X" % hex_string
            i += 8
            cont += 1
            if cont % 4 == 0:
                self._write(buffer.decode("hex"))
                buffer = ""
                cont = 0



    def _convert_and_print_image(self, im):
        """ Parse image and prepare it to a printable format """
        pixels   = []
        pix_line = ""
        im_left  = ""
        im_right = ""
        switch   = 0
        img_size = [ 0, 0 ]

        if im.size[0] > 512:
            print  ("WARNING: Image is wider than 512 and could be truncated at print time ")
        if im.size[1] > 255:
            raise ImageSizeError()

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
                switch = (switch - 1 ) * (-1)
                for x in range(pattern_len):
                    if im_color <= (255 * 3 / pattern_len * (x+1)):
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
