from microbit import *
import radio
from decoder import Decoder

radio.config(group=83, channel=17, address=0x75626974, length=32, queue=12)
radio.on()
decoder = Decoder()
display.show('R')
last = 0

def encode(value):
    if value is None:
        return 'null'
    if value is True:
        return 'true'
    if value is False:
        return 'false'
    if isinstance(value, str):
        return '"'+value.replace('\\', '\\\\').replace('"', '\\"')+'"'
    if isinstance(value, dict):
        return '{'+','.join(encode(k)+':'+encode(v) for k,v in value.items())+'}'
    if isinstance(value, (list, tuple)):
        return '['+','.join(encode(v) for v in value)+']'
    return str(value)

print('MAQUEEN RECEIVER 1.0.0 / GROUP 83 / CHANNEL 17')
while True:
    item = radio.receive_full()
    if item:
        raw, rssi, stamp = item
        try:
            packet = decoder.decode(raw, running_time())
            if packet:
                print('R '+str(rssi)+' '+encode(packet))
                last = running_time()
                display.set_pixel(packet[1]-1, 4, 9)
        except Exception:
            pass
    if running_time()-last > 2000:
        for x in range(4):
            display.set_pixel(x, 4, 0)
    sleep(2)

