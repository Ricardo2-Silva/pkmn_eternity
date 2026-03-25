# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: lxml\__init__.py


def get_include():
    """
    Returns a list of header include paths (for lxml itself, libxml2
    and libxslt) needed to compile C code against lxml if it was built
    with statically linked libraries.
    """
    import os
    lxml_path = __path__[0]
    include_path = os.path.join(lxml_path, "includes")
    includes = [include_path, lxml_path]
    for name in os.listdir(include_path):
        path = os.path.join(include_path, name)
        if os.path.isdir(path):
            includes.append(path)

    return includes
