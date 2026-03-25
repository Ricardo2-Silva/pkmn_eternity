# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: hyperlink\_socket.py
try:
    from socket import inet_pton
except ImportError:
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        pass
    else:
        import ctypes, socket

        class SockAddr(ctypes.Structure):
            _fields_ = [
             (
              "sa_family", ctypes.c_short),
             (
              "__pad1", ctypes.c_ushort),
             (
              "ipv4_addr", ctypes.c_byte * 4),
             (
              "ipv6_addr", ctypes.c_byte * 16),
             (
              "__pad2", ctypes.c_ulong)]


        WSAStringToAddressA = ctypes.windll.ws2_32.WSAStringToAddressA
        WSAAddressToStringA = ctypes.windll.ws2_32.WSAAddressToStringA

        def inet_pton(address_family, ip_string):
            addr = SockAddr()
            ip_string_bytes = ip_string.encode("ascii")
            addr.sa_family = address_family
            addr_size = ctypes.c_int(ctypes.sizeof(addr))
            try:
                attribute, size = {(socket.AF_INET): ('ipv4_addr', 4), 
                 (socket.AF_INET6): ('ipv6_addr', 16)}[address_family]
            except KeyError:
                raise socket.error("unknown address family")

            if WSAStringToAddressA(ip_string_bytes, address_family, None, ctypes.byref(addr), ctypes.byref(addr_size)) != 0:
                raise socket.error(ctypes.FormatError())
            return ctypes.string_at(getattr(addr, attribute), size)
