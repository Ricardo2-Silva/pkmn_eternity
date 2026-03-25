# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: pyglet\libs\darwin\cocoapy\runtime.py
import sys, platform, struct
from ctypes import *
from ctypes import util
from .cocoatypes import *
__LP64__ = 8 * struct.calcsize("P") == 64
__i386__ = platform.machine() == "i386"
__arm64__ = platform.machine() == "arm64"
if sizeof(c_void_p) == 4:
    c_ptrdiff_t = c_int32
else:
    if sizeof(c_void_p) == 8:
        c_ptrdiff_t = c_int64
lib = util.find_library("objc")
if lib is None:
    lib = "/usr/lib/libobjc.dylib"
objc = cdll.LoadLibrary(lib)
objc.class_addIvar.restype = c_bool
objc.class_addIvar.argtypes = [c_void_p, c_char_p, c_size_t, c_uint8, c_char_p]
objc.class_addMethod.restype = c_bool
objc.class_addProtocol.restype = c_bool
objc.class_addProtocol.argtypes = [c_void_p, c_void_p]
objc.class_conformsToProtocol.restype = c_bool
objc.class_conformsToProtocol.argtypes = [c_void_p, c_void_p]
objc.class_copyIvarList.restype = POINTER(c_void_p)
objc.class_copyIvarList.argtypes = [c_void_p, POINTER(c_uint)]
objc.class_copyMethodList.restype = POINTER(c_void_p)
objc.class_copyMethodList.argtypes = [c_void_p, POINTER(c_uint)]
objc.class_copyPropertyList.restype = POINTER(c_void_p)
objc.class_copyPropertyList.argtypes = [c_void_p, POINTER(c_uint)]
objc.class_copyProtocolList.restype = POINTER(c_void_p)
objc.class_copyProtocolList.argtypes = [c_void_p, POINTER(c_uint)]
objc.class_createInstance.restype = c_void_p
objc.class_createInstance.argtypes = [c_void_p, c_size_t]
objc.class_getClassMethod.restype = c_void_p
objc.class_getClassMethod.argtypes = [c_void_p, c_void_p]
objc.class_getClassVariable.restype = c_void_p
objc.class_getClassVariable.argtypes = [c_void_p, c_char_p]
objc.class_getInstanceMethod.restype = c_void_p
objc.class_getInstanceMethod.argtypes = [c_void_p, c_void_p]
objc.class_getInstanceSize.restype = c_size_t
objc.class_getInstanceSize.argtypes = [c_void_p]
objc.class_getInstanceVariable.restype = c_void_p
objc.class_getInstanceVariable.argtypes = [c_void_p, c_char_p]
objc.class_getIvarLayout.restype = c_char_p
objc.class_getIvarLayout.argtypes = [c_void_p]
objc.class_getMethodImplementation.restype = c_void_p
objc.class_getMethodImplementation.argtypes = [c_void_p, c_void_p]
if not __arm64__:
    objc.class_getMethodImplementation_stret.restype = c_void_p
    objc.class_getMethodImplementation_stret.argtypes = [c_void_p, c_void_p]
objc.class_getName.restype = c_char_p
objc.class_getName.argtypes = [c_void_p]
objc.class_getProperty.restype = c_void_p
objc.class_getProperty.argtypes = [c_void_p, c_char_p]
objc.class_getSuperclass.restype = c_void_p
objc.class_getSuperclass.argtypes = [c_void_p]
objc.class_getVersion.restype = c_int
objc.class_getVersion.argtypes = [c_void_p]
objc.class_getWeakIvarLayout.restype = c_char_p
objc.class_getWeakIvarLayout.argtypes = [c_void_p]
objc.class_isMetaClass.restype = c_bool
objc.class_isMetaClass.argtypes = [c_void_p]
objc.class_replaceMethod.restype = c_void_p
objc.class_replaceMethod.argtypes = [c_void_p, c_void_p, c_void_p, c_char_p]
objc.class_respondsToSelector.restype = c_bool
objc.class_respondsToSelector.argtypes = [c_void_p, c_void_p]
objc.class_setIvarLayout.restype = None
objc.class_setIvarLayout.argtypes = [c_void_p, c_char_p]
objc.class_setSuperclass.restype = c_void_p
objc.class_setSuperclass.argtypes = [c_void_p, c_void_p]
objc.class_setVersion.restype = None
objc.class_setVersion.argtypes = [c_void_p, c_int]
objc.class_setWeakIvarLayout.restype = None
objc.class_setWeakIvarLayout.argtypes = [c_void_p, c_char_p]
objc.ivar_getName.restype = c_char_p
objc.ivar_getName.argtypes = [c_void_p]
objc.ivar_getOffset.restype = c_ptrdiff_t
objc.ivar_getOffset.argtypes = [c_void_p]
objc.ivar_getTypeEncoding.restype = c_char_p
objc.ivar_getTypeEncoding.argtypes = [c_void_p]
objc.method_copyArgumentType.restype = c_char_p
objc.method_copyArgumentType.argtypes = [c_void_p, c_uint]
objc.method_copyReturnType.restype = c_char_p
objc.method_copyReturnType.argtypes = [c_void_p]
objc.method_exchangeImplementations.restype = None
objc.method_exchangeImplementations.argtypes = [c_void_p, c_void_p]
objc.method_getArgumentType.restype = None
objc.method_getArgumentType.argtypes = [c_void_p, c_uint, c_char_p, c_size_t]
objc.method_getImplementation.restype = c_void_p
objc.method_getImplementation.argtypes = [c_void_p]
objc.method_getName.restype = c_void_p
objc.method_getName.argtypes = [c_void_p]
objc.method_getNumberOfArguments.restype = c_uint
objc.method_getNumberOfArguments.argtypes = [c_void_p]
objc.method_getReturnType.restype = None
objc.method_getReturnType.argtypes = [c_void_p, c_char_p, c_size_t]
objc.method_getTypeEncoding.restype = c_char_p
objc.method_getTypeEncoding.argtypes = [c_void_p]
objc.method_setImplementation.restype = c_void_p
objc.method_setImplementation.argtypes = [c_void_p, c_void_p]
objc.objc_allocateClassPair.restype = c_void_p
objc.objc_allocateClassPair.argtypes = [c_void_p, c_char_p, c_size_t]
objc.objc_copyProtocolList.restype = POINTER(c_void_p)
objc.objc_copyProtocolList.argtypes = [POINTER(c_int)]
objc.objc_getAssociatedObject.restype = c_void_p
objc.objc_getAssociatedObject.argtypes = [c_void_p, c_void_p]
objc.objc_getClass.restype = c_void_p
objc.objc_getClass.argtypes = [c_char_p]
objc.objc_getClassList.restype = c_int
objc.objc_getClassList.argtypes = [c_void_p, c_int]
objc.objc_getMetaClass.restype = c_void_p
objc.objc_getMetaClass.argtypes = [c_char_p]
objc.objc_getProtocol.restype = c_void_p
objc.objc_getProtocol.argtypes = [c_char_p]
if not __arm64__:
    objc.objc_msgSendSuper_stret.restype = None
if not __arm64__:
    objc.objc_msgSend_stret.restype = None
objc.objc_registerClassPair.restype = None
objc.objc_registerClassPair.argtypes = [c_void_p]
objc.objc_removeAssociatedObjects.restype = None
objc.objc_removeAssociatedObjects.argtypes = [c_void_p]
objc.objc_setAssociatedObject.restype = None
objc.objc_setAssociatedObject.argtypes = [c_void_p, c_void_p, c_void_p, c_int]
objc.object_copy.restype = c_void_p
objc.object_copy.argtypes = [c_void_p, c_size_t]
objc.object_dispose.restype = c_void_p
objc.object_dispose.argtypes = [c_void_p]
objc.object_getClass.restype = c_void_p
objc.object_getClass.argtypes = [c_void_p]
objc.object_getClassName.restype = c_char_p
objc.object_getClassName.argtypes = [c_void_p]
objc.object_getInstanceVariable.restype = c_void_p
objc.object_getInstanceVariable.argtypes = [c_void_p, c_char_p, c_void_p]
objc.object_getIvar.restype = c_void_p
objc.object_getIvar.argtypes = [c_void_p, c_void_p]
objc.object_setClass.restype = c_void_p
objc.object_setClass.argtypes = [c_void_p, c_void_p]
objc.object_setInstanceVariable.restype = c_void_p
objc.object_setIvar.restype = None
objc.object_setIvar.argtypes = [c_void_p, c_void_p, c_void_p]
objc.property_getAttributes.restype = c_char_p
objc.property_getAttributes.argtypes = [c_void_p]
objc.property_getName.restype = c_char_p
objc.property_getName.argtypes = [c_void_p]
objc.protocol_conformsToProtocol.restype = c_bool
objc.protocol_conformsToProtocol.argtypes = [c_void_p, c_void_p]

class OBJC_METHOD_DESCRIPTION(Structure):
    _fields_ = [
     (
      "name", c_void_p), ("types", c_char_p)]


objc.protocol_copyMethodDescriptionList.restype = POINTER(OBJC_METHOD_DESCRIPTION)
objc.protocol_copyMethodDescriptionList.argtypes = [c_void_p, c_bool, c_bool, POINTER(c_uint)]
objc.protocol_copyPropertyList.restype = c_void_p
objc.protocol_copyPropertyList.argtypes = [c_void_p, POINTER(c_uint)]
objc.protocol_copyProtocolList = POINTER(c_void_p)
objc.protocol_copyProtocolList.argtypes = [c_void_p, POINTER(c_uint)]
objc.protocol_getMethodDescription.restype = OBJC_METHOD_DESCRIPTION
objc.protocol_getMethodDescription.argtypes = [c_void_p, c_void_p, c_bool, c_bool]
objc.protocol_getName.restype = c_char_p
objc.protocol_getName.argtypes = [c_void_p]
objc.sel_getName.restype = c_char_p
objc.sel_getName.argtypes = [c_void_p]
objc.sel_isEqual.restype = c_bool
objc.sel_isEqual.argtypes = [c_void_p, c_void_p]
objc.sel_registerName.restype = c_void_p
objc.sel_registerName.argtypes = [c_char_p]

def ensure_bytes(x):
    if isinstance(x, bytes):
        return x
    else:
        return x.encode("ascii")


def get_selector(name):
    return c_void_p(objc.sel_registerName(ensure_bytes(name)))


def get_class(name):
    return c_void_p(objc.objc_getClass(ensure_bytes(name)))


def get_object_class(obj):
    return c_void_p(objc.object_getClass(obj))


def get_metaclass(name):
    return c_void_p(objc.objc_getMetaClass(ensure_bytes(name)))


def get_superclass_of_object(obj):
    cls = c_void_p(objc.object_getClass(obj))
    return c_void_p(objc.class_getSuperclass(cls))


def x86_should_use_stret(restype):
    """Try to figure out when a return type will be passed on stack."""
    if type(restype) != type(Structure):
        return False
    else:
        if not __LP64__:
            if sizeof(restype) <= 8:
                return False
        if __LP64__:
            if sizeof(restype) <= 16:
                return False
        return True


def should_use_fpret(restype):
    """Determine if objc_msgSend_fpret is required to return a floating point type."""
    if not __i386__:
        return False
    else:
        if __LP64__:
            if restype == c_longdouble:
                return True
        if not __LP64__:
            if restype in (c_float, c_double, c_longdouble):
                return True
        return False


def send_message(receiver, selName, *args, **kwargs):
    if isinstance(receiver, str):
        receiver = get_class(receiver)
    selector = get_selector(selName)
    restype = kwargs.get("restype", c_void_p)
    argtypes = kwargs.get("argtypes", [])
    if should_use_fpret(restype):
        objc.objc_msgSend_fpret.restype = restype
        objc.objc_msgSend_fpret.argtypes = [c_void_p, c_void_p] + argtypes
        result = (objc.objc_msgSend_fpret)(receiver, selector, *args)
    elif x86_should_use_stret(restype):
        objc.objc_msgSend_stret.argtypes = [
         POINTER(restype), c_void_p, c_void_p] + argtypes
        result = restype()
        (objc.objc_msgSend_stret)(byref(result), receiver, selector, *args)
    else:
        objc.objc_msgSend.restype = restype
        objc.objc_msgSend.argtypes = [c_void_p, c_void_p] + argtypes
        result = (objc.objc_msgSend)(receiver, selector, *args)
    if restype == c_void_p:
        result = c_void_p(result)
    return result


class OBJC_SUPER(Structure):
    _fields_ = [
     (
      "receiver", c_void_p), ("class", c_void_p)]


OBJC_SUPER_PTR = POINTER(OBJC_SUPER)

def send_super(receiver, selName, *args, superclass_name=None, **kwargs):
    if hasattr(receiver, "_as_parameter_"):
        receiver = receiver._as_parameter_
    elif superclass_name is None:
        superclass = get_superclass_of_object(receiver)
    else:
        superclass = get_class(superclass_name)
    super_struct = OBJC_SUPER(receiver, superclass)
    selector = get_selector(selName)
    restype = kwargs.get("restype", c_void_p)
    argtypes = kwargs.get("argtypes", None)
    objc.objc_msgSendSuper.restype = restype
    if argtypes:
        objc.objc_msgSendSuper.argtypes = [
         OBJC_SUPER_PTR, c_void_p] + argtypes
    else:
        objc.objc_msgSendSuper.argtypes = None
    result = (objc.objc_msgSendSuper)(byref(super_struct), selector, *args)
    if restype == c_void_p:
        result = c_void_p(result)
    return result


cfunctype_table = {}

def parse_type_encoding(encoding):
    """Takes a type encoding string and outputs a list of the separated type codes.
    Currently does not handle unions or bitfields and strips out any field width
    specifiers or type specifiers from the encoding.  For Python 3.2+, encoding is
    assumed to be a bytes object and not unicode.

    Examples:
    parse_type_encoding('^v16@0:8') --> ['^v', '@', ':']
    parse_type_encoding('{CGSize=dd}40@0:8{CGSize=dd}16Q32') --> ['{CGSize=dd}', '@', ':', '{CGSize=dd}', 'Q']
    """
    type_encodings = []
    brace_count = 0
    bracket_count = 0
    typecode = b''
    for c in encoding:
        if isinstance(c, int):
            c = bytes([c])
        if c == b'{':
            if typecode:
                if typecode[-1:] != b'^':
                    if brace_count == 0:
                        if bracket_count == 0:
                            type_encodings.append(typecode)
                            typecode = b''
                typecode += c
                brace_count += 1
        if c == b'}':
            typecode += c
            brace_count -= 1
            if not brace_count >= 0:
                raise AssertionError
        elif c == b'[':
            if typecode:
                if typecode[-1:] != b'^':
                    if brace_count == 0:
                        if bracket_count == 0:
                            type_encodings.append(typecode)
                            typecode = b''
            typecode += c
            bracket_count += 1
        elif c == b']':
            pass
        typecode += c
        bracket_count -= 1
        if not bracket_count >= 0:
            raise AssertionError
        elif brace_count or bracket_count:
            typecode += c
        elif c in b'0123456789':
            pass
        else:
            if c in b'rnNoORV':
                continue
                if c in b'^cislqCISLQfdBv*@#:b?':
                    if typecode:
                        if typecode[-1:] == b'^':
                            typecode += c
                    if typecode:
                        type_encodings.append(typecode)
                    typecode = c

    if typecode:
        type_encodings.append(typecode)
    return type_encodings


def cfunctype_for_encoding(encoding):
    if encoding in cfunctype_table:
        return cfunctype_table[encoding]
    else:
        typecodes = {b'c': c_char, b'i': c_int, b's': c_short, b'l': c_long, b'q': c_longlong, 
         b'C': c_ubyte, b'I': c_uint, b'S': c_ushort, b'L': c_ulong, b'Q': c_ulonglong, 
         b'f': c_float, b'd': c_double, b'B': c_bool, b'v': None, b'*': c_char_p, 
         b'@': c_void_p, b'#': c_void_p, b':': c_void_p, NSPointEncoding: NSPoint, 
         NSSizeEncoding: NSSize, NSRectEncoding: NSRect, NSRangeEncoding: NSRange, 
         PyObjectEncoding: py_object}
        argtypes = []
        for code in parse_type_encoding(encoding):
            if code in typecodes:
                argtypes.append(typecodes[code])
            elif code[0:1] == b'^' and code[1:] in typecodes:
                argtypes.append(POINTER(typecodes[code[1:]]))
            else:
                raise Exception("unknown type encoding: " + code)

        cfunctype = CFUNCTYPE(*argtypes)
        cfunctype_table[encoding] = cfunctype
        return cfunctype


def create_subclass(superclass, name):
    if isinstance(superclass, str):
        superclass = get_class(superclass)
    return c_void_p(objc.objc_allocateClassPair(superclass, ensure_bytes(name), 0))


def register_subclass(subclass):
    objc.objc_registerClassPair(subclass)


def add_method(cls, selName, method, types):
    type_encodings = parse_type_encoding(types)
    if not type_encodings[1] == b'@':
        raise AssertionError
    elif not type_encodings[2] == b':':
        raise AssertionError
    selector = get_selector(selName)
    cfunctype = cfunctype_for_encoding(types)
    imp = cfunctype(method)
    objc.class_addMethod.argtypes = [c_void_p, c_void_p, cfunctype, c_char_p]
    objc.class_addMethod(cls, selector, imp, types)
    return imp


def add_ivar(cls, name, vartype):
    return objc.class_addIvar(cls, ensure_bytes(name), sizeof(vartype), alignment(vartype), encoding_for_ctype(vartype))


def set_instance_variable(obj, varname, value, vartype):
    objc.object_setInstanceVariable.argtypes = [
     c_void_p, c_char_p, vartype]
    objc.object_setInstanceVariable(obj, ensure_bytes(varname), value)


def get_instance_variable(obj, varname, vartype):
    variable = vartype()
    objc.object_getInstanceVariable(obj, ensure_bytes(varname), byref(variable))
    return variable.value


class ObjCMethod:
    __doc__ = "This represents an unbound Objective-C method (really an IMP)."
    typecodes = {b'c': c_byte, b'i': c_int, b's': c_short, b'l': c_long, b'q': c_longlong, 
     b'C': c_ubyte, b'I': c_uint, b'S': c_ushort, b'L': c_ulong, b'Q': c_ulonglong, 
     b'f': c_float, b'd': c_double, b'B': c_bool, b'v': None, b'Vv': None, b'*': c_char_p, 
     b'@': c_void_p, b'#': c_void_p, b':': c_void_p, b'^v': c_void_p, b'?': c_void_p, 
     NSPointEncoding: NSPoint, NSSizeEncoding: NSSize, NSRectEncoding: NSRect, 
     NSRangeEncoding: NSRange, 
     PyObjectEncoding: py_object}
    cfunctype_table = {}

    def __init__(self, method):
        """Initialize with an Objective-C Method pointer.  We then determine
        the return type and argument type information of the method."""
        self.selector = c_void_p(objc.method_getName(method))
        self.name = objc.sel_getName(self.selector)
        self.pyname = self.name.replace(b':', b'_')
        self.encoding = objc.method_getTypeEncoding(method)
        self.return_type = objc.method_copyReturnType(method)
        self.nargs = objc.method_getNumberOfArguments(method)
        self.imp = c_void_p(objc.method_getImplementation(method))
        self.argument_types = []
        for i in range(self.nargs):
            buffer = c_buffer(512)
            objc.method_getArgumentType(method, i, buffer, len(buffer))
            self.argument_types.append(buffer.value)

        try:
            self.argtypes = [self.ctype_for_encoding(t) for t in self.argument_types]
        except:
            self.argtypes = None

        try:
            if self.return_type == b'@':
                self.restype = ObjCInstance
            elif self.return_type == b'#':
                self.restype = ObjCClass
            else:
                self.restype = self.ctype_for_encoding(self.return_type)
        except:
            self.restype = None

        self.func = None

    def ctype_for_encoding(self, encoding):
        """Return ctypes type for an encoded Objective-C type."""
        if encoding in self.typecodes:
            return self.typecodes[encoding]
        elif encoding[0:1] == b'^':
            if encoding[1:] in self.typecodes:
                return POINTER(self.typecodes[encoding[1:]])
            if encoding[0:1] == b'^':
                if encoding[1:] in [CGImageEncoding, NSZoneEncoding]:
                    return c_void_p
        else:
            if encoding[0:1] == b'r':
                if encoding[1:] in self.typecodes:
                    return self.typecodes[encoding[1:]]
            if encoding[0:2] == b'r^':
                if encoding[2:] in self.typecodes:
                    return POINTER(self.typecodes[encoding[2:]])
        raise Exception("unknown encoding for %s: %s" % (self.name, encoding))

    def get_prototype(self):
        """Returns a ctypes CFUNCTYPE for the method."""
        if self.restype == ObjCInstance or self.restype == ObjCClass:
            self.prototype = CFUNCTYPE(c_void_p, *self.argtypes)
        else:
            self.prototype = CFUNCTYPE(self.restype, *self.argtypes)
        return self.prototype

    def __repr__(self):
        return "<ObjCMethod: %s %s>" % (self.name, self.encoding)

    def get_callable(self):
        """Returns a python-callable version of the method's IMP."""
        if not self.func:
            prototype = self.get_prototype()
            self.func = cast(self.imp, prototype)
            if self.restype == ObjCInstance or self.restype == ObjCClass:
                self.func.restype = c_void_p
            else:
                self.func.restype = self.restype
            self.func.argtypes = self.argtypes
        return self.func

    def __call__(self, objc_id, *args):
        """Call the method with the given id and arguments.  You do not need
        to pass in the selector as an argument since it will be automatically
        provided."""
        f = self.get_callable()
        try:
            result = f(objc_id, self.selector, *args)
            if self.restype == ObjCInstance:
                result = ObjCInstance(result)
            else:
                if self.restype == ObjCClass:
                    result = ObjCClass(result)
            return result
        except ArgumentError as error:
            error.args += ("selector = " + str(self.name),
             "argtypes =" + str(self.argtypes),
             "encoding = " + str(self.encoding))
            raise


class ObjCBoundMethod:
    __doc__ = "This represents an Objective-C method (an IMP) which has been bound\n    to some id which will be passed as the first parameter to the method."

    def __init__(self, method, objc_id):
        """Initialize with a method and ObjCInstance or ObjCClass object."""
        self.method = method
        self.objc_id = objc_id

    def __repr__(self):
        return "<ObjCBoundMethod %s (%s)>" % (self.method.name, self.objc_id)

    def __call__(self, *args):
        """Call the method with the given arguments."""
        return (self.method)(self.objc_id, *args)


class ObjCClass:
    __doc__ = "Python wrapper for an Objective-C class."
    _registered_classes = {}

    def __new__(cls, class_name_or_ptr):
        """Create a new ObjCClass instance or return a previously created
        instance for the given Objective-C class.  The argument may be either
        the name of the class to retrieve, or a pointer to the class."""
        if isinstance(class_name_or_ptr, str):
            name = class_name_or_ptr
            ptr = get_class(name)
        else:
            ptr = class_name_or_ptr
            if not isinstance(ptr, c_void_p):
                ptr = c_void_p(ptr)
            name = objc.class_getName(ptr)
        if name in cls._registered_classes:
            return cls._registered_classes[name]
        else:
            objc_class = super(ObjCClass, cls).__new__(cls)
            objc_class.ptr = ptr
            objc_class.name = name
            objc_class.instance_methods = {}
            objc_class.class_methods = {}
            objc_class._as_parameter_ = ptr
            cls._registered_classes[name] = objc_class
            objc_class.cache_instance_methods()
            objc_class.cache_class_methods()
            return objc_class

    def __repr__(self):
        return "<ObjCClass: %s at %s>" % (self.name, str(self.ptr.value))

    def cache_instance_methods(self):
        """Create and store python representations of all instance methods
        implemented by this class (but does not find methods of superclass)."""
        count = c_uint()
        method_array = objc.class_copyMethodList(self.ptr, byref(count))
        for i in range(count.value):
            method = c_void_p(method_array[i])
            objc_method = ObjCMethod(method)
            self.instance_methods[objc_method.pyname] = objc_method

    def cache_class_methods(self):
        """Create and store python representations of all class methods
        implemented by this class (but does not find methods of superclass)."""
        count = c_uint()
        method_array = objc.class_copyMethodList(objc.object_getClass(self.ptr), byref(count))
        for i in range(count.value):
            method = c_void_p(method_array[i])
            objc_method = ObjCMethod(method)
            self.class_methods[objc_method.pyname] = objc_method

    def get_instance_method(self, name):
        """Returns a python representation of the named instance method,
        either by looking it up in the cached list of methods or by searching
        for and creating a new method object."""
        if name in self.instance_methods:
            return self.instance_methods[name]
        else:
            selector = get_selector(name.replace(b'_', b':'))
            method = c_void_p(objc.class_getInstanceMethod(self.ptr, selector))
            if method.value:
                objc_method = ObjCMethod(method)
                self.instance_methods[name] = objc_method
                return objc_method
            return

    def get_class_method(self, name):
        """Returns a python representation of the named class method,
        either by looking it up in the cached list of methods or by searching
        for and creating a new method object."""
        if name in self.class_methods:
            return self.class_methods[name]
        else:
            selector = get_selector(name.replace(b'_', b':'))
            method = c_void_p(objc.class_getClassMethod(self.ptr, selector))
            if method.value:
                objc_method = ObjCMethod(method)
                self.class_methods[name] = objc_method
                return objc_method
            return

    def __getattr__(self, name):
        """Returns a callable method object with the given name."""
        name = ensure_bytes(name)
        method = self.get_class_method(name)
        if method:
            return ObjCBoundMethod(method, self.ptr)
        method = self.get_instance_method(name)
        if method:
            return method
        raise AttributeError("ObjCClass %s has no attribute %s" % (self.name, name))


class ObjCInstance:
    __doc__ = "Python wrapper for an Objective-C instance."
    _cached_objects = {}

    def __new__(cls, object_ptr):
        """Create a new ObjCInstance or return a previously created one
        for the given object_ptr which should be an Objective-C id."""
        if not isinstance(object_ptr, c_void_p):
            object_ptr = c_void_p(object_ptr)
        if not object_ptr.value:
            return
        else:
            if object_ptr.value in cls._cached_objects:
                return cls._cached_objects[object_ptr.value]
            objc_instance = super(ObjCInstance, cls).__new__(cls)
            objc_instance.ptr = object_ptr
            objc_instance._as_parameter_ = object_ptr
            class_ptr = c_void_p(objc.object_getClass(object_ptr))
            objc_instance.objc_class = ObjCClass(class_ptr)
            cls._cached_objects[object_ptr.value] = objc_instance
            observer = send_message(send_message("DeallocationObserver", "alloc"), "initWithObject:", objc_instance)
            objc.objc_setAssociatedObject(objc_instance, observer, observer, 769)
            send_message(observer, "release")
            return objc_instance

    def __repr__(self):
        if self.objc_class.name == b'NSCFString':
            from .cocoalibs import cfstring_to_string
            string = cfstring_to_string(self)
            return "<ObjCInstance %#x: %s (%s) at %s>" % (id(self), self.objc_class.name, string, str(self.ptr.value))
        else:
            return "<ObjCInstance %#x: %s at %s>" % (id(self), self.objc_class.name, str(self.ptr.value))

    def __getattr__(self, name):
        """Returns a callable method object with the given name."""
        name = ensure_bytes(name)
        method = self.objc_class.get_instance_method(name)
        if method:
            return ObjCBoundMethod(method, self)
        method = self.objc_class.get_class_method(name)
        if method:
            return ObjCBoundMethod(method, self.objc_class.ptr)
        raise AttributeError("ObjCInstance %s has no attribute %s" % (self.objc_class.name, name))


def convert_method_arguments(encoding, args):
    """Used by ObjCSubclass to convert Objective-C method arguments to
    Python values before passing them on to the Python-defined method."""
    new_args = []
    arg_encodings = parse_type_encoding(encoding)[3:]
    for e, a in zip(arg_encodings, args):
        if e == b'@':
            new_args.append(ObjCInstance(a))
        elif e == b'#':
            new_args.append(ObjCClass(a))
        else:
            new_args.append(a)

    return new_args


class ObjCSubclass:
    __doc__ = "Use this to create a subclass of an existing Objective-C class.\n    It consists primarily of function decorators which you use to add methods\n    to the subclass."

    def __init__(self, superclass, name, register=True):
        self._imp_table = {}
        self.name = name
        self.objc_cls = create_subclass(superclass, name)
        self._as_parameter_ = self.objc_cls
        if register:
            self.register()

    def register(self):
        """Register the new class with the Objective-C runtime."""
        objc.objc_registerClassPair(self.objc_cls)
        self.objc_metaclass = get_metaclass(self.name)

    def add_ivar(self, varname, vartype):
        """Add instance variable named varname to the subclass.
        varname should be a string.
        vartype is a ctypes type.
        The class must be registered AFTER adding instance variables."""
        return add_ivar(self.objc_cls, varname, vartype)

    def add_method(self, method, name, encoding):
        imp = add_method(self.objc_cls, name, method, encoding)
        self._imp_table[name] = imp

    def add_class_method(self, method, name, encoding):
        imp = add_method(self.objc_metaclass, name, method, encoding)
        self._imp_table[name] = imp

    def rawmethod(self, encoding):
        """Decorator for instance methods without any fancy shenanigans.
        The function must have the signature f(self, cmd, *args)
        where both self and cmd are just pointers to objc objects."""
        encoding = ensure_bytes(encoding)
        typecodes = parse_type_encoding(encoding)
        typecodes.insert(1, b'@:')
        encoding = (b'').join(typecodes)

        def decorator(f):
            name = f.__name__.replace("_", ":")
            self.add_method(f, name, encoding)
            return f

        return decorator

    def method(self, encoding):
        """Function decorator for instance methods."""
        encoding = ensure_bytes(encoding)
        typecodes = parse_type_encoding(encoding)
        typecodes.insert(1, b'@:')
        encoding = (b'').join(typecodes)

        def decorator(f):

            def objc_method(objc_self, objc_cmd, *args):
                py_self = ObjCInstance(objc_self)
                py_self.objc_cmd = objc_cmd
                args = convert_method_arguments(encoding, args)
                result = f(py_self, *args)
                if isinstance(result, ObjCClass):
                    result = result.ptr.value
                else:
                    if isinstance(result, ObjCInstance):
                        result = result.ptr.value
                return result

            name = f.__name__.replace("_", ":")
            self.add_method(objc_method, name, encoding)
            return objc_method

        return decorator

    def classmethod(self, encoding):
        """Function decorator for class methods."""
        encoding = ensure_bytes(encoding)
        typecodes = parse_type_encoding(encoding)
        typecodes.insert(1, b'@:')
        encoding = (b'').join(typecodes)

        def decorator(f):

            def objc_class_method(objc_cls, objc_cmd, *args):
                py_cls = ObjCClass(objc_cls)
                py_cls.objc_cmd = objc_cmd
                args = convert_method_arguments(encoding, args)
                result = f(py_cls, *args)
                if isinstance(result, ObjCClass):
                    result = result.ptr.value
                else:
                    if isinstance(result, ObjCInstance):
                        result = result.ptr.value
                return result

            name = f.__name__.replace("_", ":")
            self.add_class_method(objc_class_method, name, encoding)
            return objc_class_method

        return decorator


class DeallocationObserver_Implementation:
    DeallocationObserver = ObjCSubclass("NSObject", "DeallocationObserver", register=False)
    DeallocationObserver.add_ivar("observed_object", c_void_p)
    DeallocationObserver.register()

    @DeallocationObserver.rawmethod("@@")
    def initWithObject_(self, cmd, anObject):
        self = send_super(self, "init")
        self = self.value
        set_instance_variable(self, "observed_object", anObject, c_void_p)
        return self

    @DeallocationObserver.rawmethod("v")
    def dealloc(self, cmd):
        anObject = get_instance_variable(self, "observed_object", c_void_p)
        ObjCInstance._cached_objects.pop(anObject, None)
        send_super(self, "dealloc")

    @DeallocationObserver.rawmethod("v")
    def finalize(self, cmd):
        anObject = get_instance_variable(self, "observed_object", c_void_p)
        ObjCInstance._cached_objects.pop(anObject, None)
        send_super(self, "finalize")
