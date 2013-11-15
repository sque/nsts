
from __future__ import absolute_import
import unittest
from nsts.utils import InHouseUnitsStatisticsArray, NumPyUnitsStatisticsArray
from nsts import units

class TestStatisticsArray(unittest.TestCase):
    
    def test_inhouse(self):
        Stat = InHouseUnitsStatisticsArray

        array = map(units.BitRateUnit, [1, 2, 3, 4])
        
        stats =Stat(array)
        self.assertEqual(stats.min(), units.BitRateUnit(1))
        self.assertEqual(stats.max(), units.BitRateUnit(4))
        self.assertEqual(stats.mean(), units.BitRateUnit(2.5))
        self.assertTrue(abs(stats.std().raw_value - 1.11803398875)< 0.000001)
        
    def test_numpy(self):
        Stat = NumPyUnitsStatisticsArray

        array = map(units.BitRateUnit, [1, 2, 3, 4])
        
        stats =Stat(array)
        self.assertEqual(stats.min(), units.BitRateUnit(1))
        self.assertEqual(stats.max(), units.BitRateUnit(4))
        self.assertEqual(stats.mean(), units.BitRateUnit(2.5))
        self.assertTrue(abs(stats.std().raw_value - 1.11803398875)< 0.000001)