import json
import re


class MyEncoder(json.JSONEncoder):

    def encode(self, o):
        return re.sub('\s+([\d\]]+)','\g<1>',super(MyEncoder, self).encode(o))
