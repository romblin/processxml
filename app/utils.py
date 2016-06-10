# -*- encoding: utf8 -*-

import hashlib


def digest(value):
    return hashlib.sha1(value).hexdigest()
