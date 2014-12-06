#!/usr/bin/python
from __future__ import print_function, division
import unittest
from os.path import join
import pandas as pd
from datetime import timedelta
from .testingtools import data_dir, WarningTestMixin
from ..datastore import HDFDataStore
from ..elecmeter import ElecMeter, ElecMeterID
from ..stats.tests.test_totalenergy import check_energy_numbers

METER_ID = ElecMeterID(instance=1, building=1, dataset='REDD')
METER_ID2 = ElecMeterID(instance=2, building=1, dataset='REDD')
METER_ID3 = ElecMeterID(instance=3, building=1, dataset='REDD')

class TestElecMeter(WarningTestMixin, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        filename = join(data_dir(), 'energy.h5')
        cls.datastore = HDFDataStore(filename)
        ElecMeter.load_meter_devices(cls.datastore)
        cls.meter_meta = cls.datastore.load_metadata('building1')['elec_meters'][METER_ID.instance]

    @classmethod
    def tearDownClass(cls):
        cls.datastore.close()

    def test_load(self):
        meter = ElecMeter(store=self.datastore, metadata=self.meter_meta, 
                          meter_id=METER_ID)
        self.assertEqual(meter.metadata['device_model'], 'Energy Meter')
        self.assertEqual(meter.device['sample_period'], 10)

    def test_total_energy(self):
        meter = ElecMeter(meter_id=METER_ID)
        with self.assertRaises(RuntimeError):
            meter.total_energy()
        meter = ElecMeter(store=self.datastore, metadata=self.meter_meta, 
                          meter_id=METER_ID)
        energy = meter.total_energy()
        check_energy_numbers(self, energy)
        
    def test_upstream_meter(self):
        meter1 = ElecMeter(metadata={'site_meter': True}, meter_id=METER_ID)
        self.assertIsNone(meter1.upstream_meter())
        meter2 = ElecMeter(metadata={'submeter_of': 1}, meter_id=METER_ID2)
        self.assertEquals(meter2.upstream_meter(), meter1)
        meter3 = ElecMeter(metadata={'submeter_of': 2}, meter_id=METER_ID3)
        self.assertEquals(meter3.upstream_meter(), meter2)


    def test_correlation(self):
        meter1 = ElecMeter(store=self.datastore, metadata=self.meter_meta, meter_id=METER_ID)
        meter2 = ElecMeter(store=self.datastore, metadata=self.meter_meta, meter_id=METER_ID2)
        meter3 = ElecMeter(store=self.datastore, metadata=self.meter_meta, meter_id=METER_ID3)
        m1=self.datastore.store.get('/building1/elec/meter1')
        m2=self.datastore.store.get('/building1/elec/meter2')
        m3=self.datastore.store.get('/building1/elec/meter3')
    
    # Correlation using the pandas function
    
        cor_pandas_11=m1.corrwith(m1)
        cor_pandas_12=m1.corrwith(m2)
        cor_pandas_13=m1.corrwith(m3)
        cor_pandas_22=m2.corrwith(m2)
        cor_pandas_23=m2.corrwith(m3)
        cor_pandas_33=m3.corrwith(m3)
    
    #Correlation using NILMTK
    
    
        cor_nilm_11=meter1.correlation(meter1)
        cor_nilm_12=meter1.correlation(meter2)
        cor_nilm_13=meter1.correlation(meter3)
        cor_nilm_22=meter2.correlation(meter2)
        cor_nilm_23=meter2.correlation(meter3)
        cor_nilm_33=meter3.correlation(meter3)
    
        self.assertEqual(cor_nilm_11, cor_pandas_11)
        self.assertEqual(cor_nilm_12, cor_pandas_12)
        self.assertEqual(cor_nilm_13, cor_pandas_13)
        self.assertEqual(cor_nilm_22, cor_pandas_22)
        self.assertEqual(cor_nilm_23, cor_pandas_23)
        self.assertEqual(cor_nilm_33, cor_pandas_33)

if __name__ == '__main__':
    unittest.main()
