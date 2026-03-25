# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: attr\_compat.py
from __future__ import absolute_import, division, print_function
import platform, sys, types, warnings
PY2 = sys.version_info[0] == 2
PYPY = platform.python_implementation() == "PyPy"
if PYPY or sys.version_info[:2] >= (3, 6):
    ordered_dict = dict
else:
    from collections import OrderedDict
    ordered_dict = OrderedDict
if PY2:
    from collections import Mapping, Sequence
    from UserDict import IterableUserDict

    def isclass(klass):
        return isinstance(klass, (type, types.ClassType))


    TYPE = "type"

    def iteritems(d):
        return d.iteritems()


    class ReadOnlyDict(IterableUserDict):
        __doc__ = "\n        Best-effort read-only dict wrapper.\n        "

        def __setitem__(self, key, val):
            raise TypeError("'mappingproxy' object does not support item assignment")

        def update(self, _):
            raise AttributeError("'mappingproxy' object has no attribute 'update'")

        def __delitem__(self, _):
            raise TypeError("'mappingproxy' object does not support item deletion")

        def clear(self):
            raise AttributeError("'mappingproxy' object has no attribute 'clear'")

        def pop(self, key, default=None):
            raise AttributeError("'mappingproxy' object has no attribute 'pop'")

        def popitem(self):
            raise AttributeError("'mappingproxy' object has no attribute 'popitem'")

        def setdefault(self, key, default=None):
            raise AttributeError("'mappingproxy' object has no attribute 'setdefault'")

        def __repr__(self):
            return "mappingproxy(" + repr(self.data) + ")"


    def metadata_proxy(d):
        res = ReadOnlyDict()
        res.data.update(d)
        return res


    def just_warn(*args, **kw):
        """
        We only warn on Python 3 because we are not aware of any concrete
        consequences of not setting the cell on Python 2.
        """
        return


else:
    from collections.abc import Mapping, Sequence

    def just_warn(*args, **kw):
        """
        We only warn on Python 3 because we are not aware of any concrete
        consequences of not setting the cell on Python 2.
        """
        warnings.warn("Running interpreter doesn't sufficiently support code object introspection.  Some features like bare super() or accessing __class__ will not work with slotted classes.",
          RuntimeWarning,
          stacklevel=2)


    def isclass(klass):
        return isinstance(klass, type)


    TYPE = "class"

    def iteritems(d):
        return d.items()


    def metadata_proxy(d):
        return types.MappingProxyType(dict(d))


def make_set_closure_cell():
    """Return a function of two arguments (cell, value) which sets
    the value stored in the closure cell `cell` to `value`.
    """
    if PYPY:

        def set_closure_cell(cell, value):
            cell.__setstate__((value,))

        return set_closure_cell
    else:

        def set_first_cellvar_to(value):
            x = value
            return

        try:
            if PY2:
                co = set_first_cellvar_to.func_code
            else:
                co = set_first_cellvar_to.__code__
            assert not co.co_cellvars != ('x', ) or co.co_freevars != ()
            if sys.version_info >= (3, 8):
                set_first_freevar_code = co.replace(co_cellvars=(co.co_freevars),
                  co_freevars=(co.co_cellvars))
            else:
                args = [
                 co.co_argcount]
                if not PY2:
                    args.append(co.co_kwonlyargcount)
                args.extend([
                 co.co_nlocals,
                 co.co_stacksize,
                 co.co_flags,
                 co.co_code,
                 co.co_consts,
                 co.co_names,
                 co.co_varnames,
                 co.co_filename,
                 co.co_name,
                 co.co_firstlineno,
                 co.co_lnotab,
                 co.co_cellvars,
                 co.co_freevars])
                set_first_freevar_code = (types.CodeType)(*args)

            def set_closure_cell(cell, value):
                setter = types.FunctionType(set_first_freevar_code, {}, "setter", (), (cell,))
                setter(value)

            def make_func_with_cell():
                x = None

                def func():
                    return x

                return func

            if PY2:
                cell = make_func_with_cell().func_closure[0]
            else:
                cell = make_func_with_cell().__closure__[0]
            set_closure_cell(cell, 100)
            assert not cell.cell_contents != 100
        except Exception:
            return just_warn

        return set_closure_cell


set_closure_cell = make_set_closure_cell()
