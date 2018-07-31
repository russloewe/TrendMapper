# coding=utf-8
"""Dialog test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'russloewe@gmai.com'
__date__ = '2018-07-28'
__copyright__ = 'Copyright 2018, Russell Loewe'

import unittest

from PyQt4.QtGui import QDialogButtonBox, QDialog

from trend_mapper_dialog import TrendMapperDialog

from utilities import get_qgis_app
QGIS_APP = get_qgis_app()


class TrendMapperDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        self.dialog = TrendMapperDialog(None)

    def tearDown(self):
        """Runs after each test."""
        self.dialog = None

    def test_dialog_ok(self):
        """Test we can click OK."""

        button = self.dialog.button_box.button(QDialogButtonBox.Ok)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Accepted)
        
    def test_setAttributeCombos(self):
        testList = ['one', 'two', 'three']
        self.dialog.setLayerAttributesCombos(testList)
        for n in range(3):
            self.assertEqual(self.dialog.CatagoryCombo.findText(testList[n]) >= 0, True)
        testList2 = ['four', 'five', 'six']
        for n in range(3):
            self.assertEqual(self.dialog.CatagoryCombo.findText(testList[n]) < 0, True)

    def test_dialog_cancel(self):
        """Test we can click cancel."""
        button = self.dialog.button_box.button(QDialogButtonBox.Cancel)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Rejected)

if __name__ == "__main__":
    suite = unittest.makeSuite(TrendMapperDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
