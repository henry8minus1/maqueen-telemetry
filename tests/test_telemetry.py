import importlib.util
import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class TelemetryTests(unittest.TestCase):
    def setUp(self):
        self.sent = []
        self.scheduled = []
        self.reads = []
        self.clock = 1000
        self.mb = types.ModuleType('microbit')
        self.mb.run_every = lambda fn, **kw: self.scheduled.append(fn)
        self.mb.running_time = lambda: self.clock
        self.mb.button_a = self.mb.button_b = types.SimpleNamespace(is_pressed=lambda: False)
        self.mb.accelerometer = types.SimpleNamespace(get_x=lambda: -1024, get_y=lambda: 1024, get_z=lambda: 0)
        self.mb.temperature = lambda: 22
        self.mb.display = types.SimpleNamespace(get_pixel=lambda x,y: (x+y)%10)
        self.mb.i2c = types.SimpleNamespace(write=lambda *a: self.reads.append(a), read=lambda addr,n: bytes([1]*n))
        radio = types.ModuleType('radio')
        radio.config = lambda **kw: None
        radio.on = lambda: None
        radio.send_bytes = self.sent.append
        sys.modules['microbit'], sys.modules['radio'] = self.mb, radio
        self.t = load('telemetry_test', ROOT/'python/telemetry.py')
        self.decoder = load('decoder_test', ROOT/'receiver/decoder.py').Decoder()

    def test_background_idempotent_and_noninterfering(self):
        self.assertEqual(self.t.start(2,'lesson1-v1'), 'background')
        self.t.start(2,'lesson1-v1')
        self.assertEqual(len(self.scheduled),1)
        for _ in range(24):
            self.scheduled[0]()
        self.assertEqual(self.reads,[])
        self.assertTrue(all(len(packet)<=19 for packet in self.sent))
        results=[self.decoder.decode(p, i*200) for i,p in enumerate(self.sent)]
        data={k:v for p in results if p for k,v in p[5].items()}
        self.assertEqual(data['program_tag'],'lesson1-v1')
        self.assertEqual(data['runtime'],'python')
        self.assertEqual(data['leds'],''.join(str((x+y)%10) for y in range(5) for x in range(5)))
        self.t.stop()
        count=len(self.sent)
        self.scheduled[0]()
        self.assertEqual(len(self.sent),count)

    def test_manual_fallback(self):
        del self.mb.run_every
        self.assertEqual(self.t.start(1,'demo'), 'manual')
        self.t.poll()
        self.assertEqual(len(self.sent),1)
        self.t.poll()
        self.assertEqual(len(self.sent),1)
        self.clock+=250
        self.t.poll()
        self.assertEqual(len(self.sent),2)

    def test_optional_polling_and_error_survival(self):
        self.t.start()
        self.t.poll_maqueen(True)
        for _ in range(12):self.t._tick()
        self.assertGreater(len(self.reads),0)
        self.mb.i2c.read=lambda *args: (_ for _ in ()).throw(OSError())
        for _ in range(12):self.t._tick()
        self.assertGreater(self.t.errors(),0)
        self.assertTrue(self.t._enabled)

    def test_makecode_envelope_and_led_pair_loss(self):
        raw=b'MT1N01lesson1-v1'
        wrapped=bytes([2])+bytes(8)+bytes([len(raw)])+raw
        for value in (raw,wrapped,b'\x01\x00\x01'+wrapped):
            self.assertEqual(self.decoder.decode(value,1)[5]['program_tag'],'lesson1-v1')
        self.decoder.decode(b'MT1U020123456789012',1)
        result=self.decoder.decode(b'MT1V04345678901234',2)
        self.assertNotIn('leds',result[5])
        self.decoder.decode(b'MT1Uff0123456789012',3)
        self.assertEqual(len(self.decoder.decode(b'MT1V00345678901234',4)[5]['leds']),25)

    def test_four_robots_remain_separate(self):
        for robot in range(1,5):
            p=self.decoder.decode(('MT%dN01robot%d'%(robot,robot)).encode(),10)
            self.assertEqual(p[1],robot)
            self.assertEqual(p[5]['program_tag'],'robot%d'%robot)
        self.assertEqual(len(self.decoder.count),4)

    def test_demo_fields(self):
        for payload,key,value in [('o123456','light_commands','123456'),('s255','sound',255),('t1','logo',1),('i42','ir_activity',42),('h-1','heading',None),('h240','heading',240),('m51','magnetic_uT',51),('l30','microbit_light',30)]:
            self.assertEqual(self.decoder.decode(('MT1X01'+payload).encode(),1)[5][key],value)
        for payload in ('o123','o123459','sno'):
            with self.assertRaises(ValueError):self.decoder.decode(('MT1X01'+payload).encode(),1)

    def test_bad_frames(self):
        for value in (b'noise',b'MT',b'junkMT1N01bad'):
            self.assertIsNone(self.decoder.decode(value,1))
        for value in (b'MT5N01bad',b'MT1B01xx',b'MT1L019',b'MT1U01x'):
            with self.assertRaises(ValueError):self.decoder.decode(value,1)

if __name__=='__main__':unittest.main()
