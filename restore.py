from redis import Redis

from json import load, dumps, loads, JSONEncoder, JSONDecoder
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

dump_fh = open('dump.txt', 'r')
import_data = load(dump_fh, object_hook=as_python_object)
close(dump_fh)

for key in import_data.keys():
    if import_data[key]['type'] == 'string':
        r.set(key, import_data[key]['value'])
    elif import_data[key]['type'] == 'hash':
        for h_key in import_data[key]['value'].keys():
            r.hset(key, h_key, import_data[key]['value'][h_key])
    elif import_data[key]['type'] == 'set':
        r.sinterstore(key, import_data[key]['value'])
    elif import_data[key]['type'] == 'zset':
        r.zinterstore(key, import_data[key]['value'])
    elif import_data[key]['type'] == 'list':
        for item in import_data[key]['value']:
            r.lpush(key, item)
    elif import_data[key]['type'] == 'none':
        next
    else:
        print 'Found unknown type: %s' % r.type(key)

