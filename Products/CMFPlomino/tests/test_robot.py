import unittest

import robotsuite
from Products.CMFPlomino.testing import PLOMINO_ROBOT_TESTING
from plone.testing import layered


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite('test_plomino.robot'),
                layer=PLOMINO_ROBOT_TESTING),
    ])
    return suite
