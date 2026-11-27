"""Decode raw MicroPython and official MakeCode sendString radio payloads."""
class Decoder:
    def __init__(self):
        self.partial = {}
        self.count = {}

    def decode(self, raw, now):
        # MakeCode string packet: type=2,time[4],serial[4],len[1],text.
        # Some DAL stacks retain the 01 00 01 datagram prefix.
        if raw.startswith(b'\x01\x00\x01'):
            raw = raw[3:]
        if raw.startswith(b'MT'):
            text = raw.decode('ascii')
        elif len(raw) >= 10 and raw[0] == 2 and 6 <= raw[9] <= 19:
            size = raw[9]
            if len(raw) < 10 + size:
                raise ValueError('truncated MakeCode string')
            text = raw[10:10+size].decode('ascii')
        else:
            return None
        if len(text) < 6 or len(text) > 19 or text[:2] != 'MT':
            return None
        rid, kind, seq = int(text[2]), text[3], int(text[4:6], 16)
        if rid not in (1, 2, 3, 4):
            raise ValueError('invalid robot ID')
        value = text[6:]
        data = {'wire_seq': seq}
        state = self.partial.setdefault(rid, {})
        if kind == 'H':
            version, runtime = value.split('|')
            data.update({'library_version': version, 'runtime': 'makecode' if runtime == 'pxt' else runtime})
        elif kind == 'N':
            data['program_tag'] = value
        elif kind == 'B':
            if value not in ('00', '01', '10', '11'):
                raise ValueError('invalid buttons')
            data.update({'a': value[0] == '1', 'b': value[1] == '1'})
        elif kind in ('U', 'V'):
            size = 13 if kind == 'U' else 12
            if len(value) != size or any(c not in '0123456789' for c in value):
                raise ValueError('invalid LEDs')
            if kind == 'U':
                state['led_first'] = (value, seq, now)
            else:
                first = state.pop('led_first', None)
                if first and (seq-first[1]) % 256 == 1 and now-first[2] < 2000:
                    data['leds'] = first[0] + value
        elif kind in ('A', 'E', 'I', 'C'):
            parts = [int(v) for v in value.split(',')]
            if len(parts) != 2:
                raise ValueError('invalid pair')
            if kind == 'A':
                state['acc_xy'] = (parts, now)
            elif kind == 'E':
                state['adc_lc'] = (parts, now)
            elif kind == 'I':
                data['light'] = parts
            else:
                data['cmd'] = parts
        elif kind in ('Z', 'F'):
            key = 'acc_xy' if kind == 'Z' else 'adc_lc'
            first = state.pop(key, None)
            if first and now-first[1] < 2000:
                data['acc' if kind == 'Z' else 'adc'] = first[0]+[int(value)]
        elif kind == 'T':
            data['temp'] = int(value)
        elif kind == 'M':
            data['mode'] = value
        elif kind == 'D':
            data['cm'] = None if int(value) < 0 else int(value)
        elif kind == 'L':
            bits = int(value)
            if not 0 <= bits <= 7:
                raise ValueError('invalid line mask')
            data['line'] = bits
        elif kind == 'K':
            data['battery'] = int(value)
        elif kind == 'X':
            keys = {'s':'sound', 't':'logo', 'i':'ir_activity', 'h':'heading', 'm':'magnetic_uT', 'l':'microbit_light'}
            if value[:1] == 'o':
                codes = value[1:]
                if len(codes) != 6 or any(c not in '01234567' for c in codes):
                    raise ValueError('invalid light colors')
                data['light_commands'] = codes
            elif value[:1] in keys:
                number = int(value[1:])
                data[keys[value[0]]] = None if value[0] == 'h' and number < 0 else number
            else:
                return None
        elif kind == 'Q':
            data['sensor_polling'] = value == '1'
        else:
            return None
        # Sequence counts forwarded frames; wire_seq exposes original byte counter.
        self.count[rid] = self.count.get(rid, 0)+1
        return [2, rid, self.count[rid], now, 'state', data]

