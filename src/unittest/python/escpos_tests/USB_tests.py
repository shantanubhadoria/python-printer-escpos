import unittest
import os
import sys
# import time
import logging


from escpos.USB import getUSBPrinter


@unittest.skipIf(type(os.environ.get('PYTHON_ESCPOS_TEST_VENDORID')) is not str or
                 type(os.environ.get('PYTHON_ESCPOS_TEST_PRODUCTID')) is not str,
                 'Skip USB hardware tests, unable to predict device configurations in test setups')
class USBTest(unittest.TestCase):
    """
    To run these tests for BIXOLON USB printer set

        export PYTHON_ESCPOS_TEST_VENDORID=1504;
        export PYTHON_ESCPOS_TEST_PRODUCTID=0006;
        pyb run_unit_tests
    """

    @classmethod
    def setUpClass(cls):
        cls.log = logging.getLogger("USB.py tests")
        cls.log.debug("Initializing printer object")
        cls.USBPrinterClass = getUSBPrinter()
        cls.printer = cls.USBPrinterClass(idVendor=int(os.environ.get('PYTHON_ESCPOS_TEST_VENDORID'), 16),
                                          idProduct=int(os.environ.get('PYTHON_ESCPOS_TEST_PRODUCTID'), 16))

    def setUp(self):
        pass

    def test__objIsInstance(cls):
        cls.assertIsInstance(cls.printer, cls.USBPrinterClass)

    def test_text(cls):
        cls.printer.text("TEST\n")

    def tearDown(self):
        pass  # time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        del cls.printer


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("USB.py tests").setLevel(logging.DEBUG)
    unittest.main()
