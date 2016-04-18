import unittest
import os
import sys
# import time
import logging


from escpos.USB import getUSBPrinter


@unittest.skipIf(type(os.environ.get('PYTHON_ESCPOS_TEST_VENDORID')) is not str or
                 type(os.environ.get('PYTHON_ESCPOS_TEST_PRODUCTID')) is not str,
                 'Skip USB hardware tests, unable to predict device configurations in test setups')
class genericTest(unittest.TestCase):
    """
    To run these tests for BIXOLON USB printer set

        export PYTHON_ESCPOS_TEST_VENDORID=1504;
        export PYTHON_ESCPOS_TEST_PRODUCTID=0006;
        pyb run_unit_tests
    """

    @classmethod
    def setUpClass(cls):
        log = logging.getLogger("generic.py tests")
        log.debug("Initializing printer object")
        cls.USBPrinterClass = getUSBPrinter()
        cls.printer = cls.USBPrinterClass(idVendor=int(os.environ.get('PYTHON_ESCPOS_TEST_VENDORID'), 16),
                                          idProduct=int(os.environ.get('PYTHON_ESCPOS_TEST_PRODUCTID'), 16))
        cls.printer.cutPaper()

    def setUp(self):
        pass

    def test_initialize(cls):
        cls.printer.text("Initializing Printer")
        cls.printer.initialize()
        cls.printer.lf()
        cls.printer.text("Initialized Printer")

    def test_align(cls):
        cls.printer.lf()
        cls.printer.align('right')
        cls.printer.text('This text is aligned right')
        cls.printer.lf()
        cls.printer.align('center')
        cls.printer.text('This text is aligned center')
        cls.printer.lf()
        cls.printer.align('left')
        cls.printer.text('This text is aligned left')

    def test_barcode(cls):
        cls.printer.barcode(text='Shantanu', textPosition='above')

    def test_bold(cls):
        cls.printer.lf()
        cls.printer.bold()
        cls.printer.text("bold text")
        cls.printer.bold(False)
        cls.printer.text(" not bold text")

    def test_charSpacing(cls):
        cls.printer.lf()
        cls.printer.charSpacing(20)
        cls.printer.text("Char spacing 20")
        cls.printer.lf()
        cls.printer.charSpacing(10)
        cls.printer.text("Char spacing 10")
        cls.printer.lf()
        cls.printer.charSpacing(5)
        cls.printer.text("Char spacing 5")
        cls.printer.lf()
        cls.printer.charSpacing(1)
        cls.printer.text("Char spacing 1")

    def test_color(cls):
        cls.printer.lf()
        cls.printer.color(1)
        cls.printer.text('This text is in color 1')
        cls.printer.lf()
        cls.printer.color(0)
        cls.printer.text('This text is in color 0')

    def test_cr(cls):
        cls.printer.lf()
        cls.printer.text("carriage return after this:")
        cls.printer.cr()
        cls.printer.text("did you see a carriage return?")

    def test_cutPaper(cls):
        cls.printer.lf()
        cls.printer.text("Partial cut on paper after feed")
        cls.printer.lf()
        cls.printer.cutPaper()
        cls.printer.text("Partial cut on paper without feed")
        cls.printer.lf()
        cls.printer.cutPaper(feed=False)

    def test_disable_enable(cls):
        cls.printer.lf()
        cls.printer.text('disabling printer after this command')
        cls.printer.disable()
        cls.printer.lf()
        cls.printer.text('disabled printer this should not print')
        cls.printer.enable()
        cls.printer.lf()
        cls.printer.text('enabled printer this should print')

    @unittest.skip("non recommended method")
    def test_doubleHeight(cls):
        cls.printer.lf()
        cls.printer.doubleHeight()
        cls.printer.text("This text is double height")
        cls.printer.lf()
        cls.printer.doubleHeight(False)
        cls.printer.text("This text is not double height")

    def test_doubleStrike(cls):
        cls.printer.lf()
        cls.printer.doubleStrike()
        cls.printer.text('This is double striked text')
        cls.printer.lf()
        cls.printer.doubleStrike(False)
        cls.printer.text('This is not double striked text')

    @unittest.skip("non recommended method")
    def test_doubleWidth(cls):
        cls.printer.lf()
        cls.printer.doubleWidth()
        cls.printer.text("This text is double width")
        cls.printer.lf()
        cls.printer.doubleWidth(False)
        cls.printer.text("This text is not double width")

    def test_drawerKickPulse(cls):
        cls.printer.lf()
        cls.printer.text("You should hear the drawer kick now")
        cls.printer.drawerKickPulse()

    def test_ff(cls):
        cls.printer.lf()
        cls.printer.text("Form feed after this line")
        cls.printer.lf()
        cls.printer.ff()
        cls.printer.text("Did you see the form feed?")

    def test_font(cls):
        cls.printer.lf()
        cls.printer.font('b')
        cls.printer.text("This is font 'b'")
        cls.printer.lf()
        cls.printer.font('a')
        cls.printer.text("This is font 'a'")

    def test_horizontalPosition(cls):
        cls.printer.lf()
        cls.printer.horizontalPosition(100)
        cls.printer.text("horizontal position 100 (10/6 inches)")
        cls.printer.lf()
        cls.printer.horizontalPosition()
        cls.printer.text("horizontal position to default (0 inches)")

    def test_image(cls):
        cls.printer.image('corpus/images/header.gif')

    def test_invert(cls):
        cls.printer.lf()
        cls.printer.invert()
        cls.printer.text("Inverted text")
        cls.printer.lf()
        cls.printer.invert(False)
        cls.printer.text("Non-Inverted text")

    def test_leftMargin(cls):
        cls.printer.lf()
        cls.printer.leftMargin(20)
        cls.printer.text("Left margin set to 20")
        cls.printer.lf()
        cls.printer.leftMargin()
        cls.printer.text("Left margin set to default 10")

    def test_lineSpacing(cls):
        cls.printer.lf()
        cls.printer.lineSpacing(250)
        cls.printer.text("Line spacing: 250(250/180 inch)")
        cls.printer.lf()
        cls.printer.text("Line spacing: 250(250/180 inch)")
        cls.printer.lf()
        cls.printer.lineSpacing(100)
        cls.printer.text("Line spacing: 100(100/180 inch)")
        cls.printer.lf()
        cls.printer.text("Line spacing: 100(100/180 inch)")
        cls.printer.lf()
        cls.printer.lineSpacing()
        cls.printer.lf()

    def test_printAreaWidth(cls):
        cls.printer.lf()
        cls.printer.printAreaWidth(200)
        cls.printer.text('Set print area width to 200')
        cls.printer.lf()
        cls.printer.text('1234567890123456789012345678901234567890123456789012345678901234567890')
        cls.printer.printAreaWidth()

    def test_qr(cls):
        cls.printer.qr('My name is Shantanu Bhadoria')

    def test_textSize(cls):
        cls.printer.lf()
        cls.printer.textSize(width=4, height=4)
        cls.printer.text('4x4 size')
        cls.printer.lf()
        cls.printer.textSize(width=2, height=2)
        cls.printer.text('2x2 size')
        cls.printer.lf()
        cls.printer.textSize()

    def tearDown(self):
        pass  # time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.printer.cutPaper()
        del cls.printer


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("generic.py tests").setLevel(logging.DEBUG)
    unittest.main()
