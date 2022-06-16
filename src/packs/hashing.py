from hashlib import sha256

import os


def tag_generator(model=None):
    tag = sha256(os.urandom(64)).hexdigest()[0:8]

    if model is not None:
        while model.objects.filter(tag=tag).exists():
            tag = sha256(os.urandom(64)).hexdigest()[0:8]

    return tag
