import datetime as datetime_module
from datetime import datetime
from unittest import TestCase
from simplejson.compat import StringIO, reload_module

import simplejson as json


# TODO:
# Write test of `parse_float=simplejson.decode_datetime` argument
# Implement `simplejson.decode_datetime()` which progressively falls back from:
#  1. ISO strings with unambiguous TZ name
#  2. ISO strings with ambiguous TZ abbreviations (e.g. 'PST' or 'EST')
#  3. ISO strings without TZ info (assume GMT?)
#  4. Unix timestamps (assume GMT)
#  5. dateutil.parser

class TestDatetime(TestCase):
    DTS = datetime(2014, 1, 4), datetime(2014, 1, 4, 8, 0, 0)
    def dumps(self, obj, **kw):
        sio = StringIO()
        json.dump(obj, sio, **kw)
        res = json.dumps(obj, **kw)
        self.assertEqual(res, sio.getvalue())
        return res

    def loads(self, s, **kw):
        sio = StringIO(s)
        res = json.loads(s, **kw)
        self.assertEqual(res, json.load(sio, **kw))
        return res

    def test_datetime_encode(self):
        for d in self.DTs:
            self.assertEqual(self.dumps(d, use_datetime=True), str(d))

    # FAIL: This test should fail
    def test_datetime_decode(self):
        for s in self.DTS:
            self.assertEqual(self.loads(s), json.decode_datetime(s))

    def test_stringify_key(self):
        for d in map(json.decode_datetime, self.DTS):
            v = {d: d}
            self.assertEqual(
                self.loads(
                    self.dumps(v, use_datetime=True)),
                {str(d): d})

    # FAIL: This test should fail
    def test_datetime_roundtrip(self):
        for d in self.DTS:
            for v in [d, [d], {'': d}]:
                self.assertEqual(
                    self.loads(
                        self.dumps(v, use_datetime=True)),
                    v)

    def test_datetime_defaults(self):
        d = datetime(2014, 1, 4)
        # use_datetime=True is the default
        self.assertRaises(TypeError, json.dumps, d, use_datetime=False)
        self.assertEqual('"2014-01-04 00:00:00"', json.dumps(d))
        self.assertEqual('"2014-01-04 00:00:00"', json.dumps(d, use_datetime=True))
        self.assertRaises(TypeError, json.dump, d, StringIO(),
                          use_datetime=False)
        sio = StringIO()
        json.dump(d, sio)
        self.assertEqual('"2014-01-04 00:00:00"', sio.getvalue())
        sio = StringIO()
        json.dump(d, sio, use_datetime=True)
        self.assertEqual('"2014-01-04 00:00:00"', sio.getvalue())

    def test_datetime_reload(self):
        # Simulate a subinterpreter that reloads the Python modules but not
        # the C code https://github.com/simplejson/simplejson/issues/34
        global datetime_module
        datetime = reload_module(datetime_module).datetime
        import simplejson.encoder
        simplejson.encoder.datetime = datetime
        self.test_datetime_roundtrip()
