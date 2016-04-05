from mockito import mock, verify
import unittest


from escpos.USB import Printer


@unittest.skip('Skip USB hardware tests, unable to predict device configurations in test setups')
class USBTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.printer = Printer(idVendor=0x1504, idProduct=0x0006)


    def test_open(cls):
        cls.printer.open()


    def test__write(cls):
        cls.printer._write(msg='aa')


    def test__read(cls):
        cls.printer._read(length=8)


    @classmethod
    def tearDownClass(cls):
        cls.printer.__del__
