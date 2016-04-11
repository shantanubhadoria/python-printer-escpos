from mockito import mock, verify
import unittest
import os


from escpos.USB import getUSBPrinter


""" To run these tests for BIXOLON USB printer set
    export BIXOLON_USB_TESTS=1;pyb
"""
@unittest.skipIf(os.environ.get('BIXOLON_USB_TESTS') != '1', 'Skip USB hardware tests, unable to predict device configurations in test setups')
class USBTest(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.USBPrinterClass = getUSBPrinter()
        cls.printer = cls.USBPrinterClass(idVendor=0x1504, idProduct=0x0006)


    def test__objIsInstance(cls):
        cls.assertIsInstance(cls.printer, cls.USBPrinterClass)

    def test__open(cls):
        cls.printer.open()


    def test__write(cls):
        cls.printer._write(msg="TEST\n")


    def test__image(cls):
        cls.printer.image('corpus/images/cbpm.gif')


    def test__qr(cls):
        cls.printer.qr('My name is Shantanu Bhadoria')


    def test_barcode(cls):
        cls.printer.barcode(text='Shantanu', textPosition='above')


    @classmethod
    def tearDown(cls):
        cls.printer.__del__
