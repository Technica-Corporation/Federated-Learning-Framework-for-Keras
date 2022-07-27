import json

def decode_bytestr_to_json(value, bytetype='utf8'):
    unicode_str = value.decode(bytetype).replace("'", '"')
    data = json.loads(unicode_str)
    return data