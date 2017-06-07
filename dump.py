from redis import Redis

from json import dumps, loads, JSONEncoder, JSONDecoder
import pickle

class PythonObjectEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, unicode, int, float, bool, type(None))):
            return JSONEncoder.default(self, obj)
        return {'_python_object': pickle.dumps(obj)}

def as_python_object(dct):
    if '_python_object' in dct:
        return pickle.loads(str(dct['_python_object']))
    return dct

r = Redis(host='localhost')

output = {}

for key in r.keys():

    if r.type(key) == 'string':
        output[key] = {'type': 'string', 'value': r.get(key)}
    elif r.type(key) == 'hash':
        output[key] = {'type': 'hash', 'value': r.hgetall(key)}
    elif r.type(key) == 'set':
        output[key] = {'type': 'set', 'value': r.smembers(key)}
    elif r.type(key) == 'zset':
        output[key] = {'type': 'zset', 'value': r.zrange(key, 0, -1)}
    elif r.type(key) == 'list':
        output[key] = {'type': 'list', 'value': r.lrange(key, 0, -1)}
    elif r.type(key) == 'none':
        output[key] = {'type': 'none', 'value': None}
    else:
        print 'Found unknown type: %s' % r.type(key)
print dumps(output, cls=PythonObjectEncoder)
