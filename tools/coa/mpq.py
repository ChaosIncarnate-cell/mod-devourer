"""Tiny StormLib wrapper: list and extract files from MPQ archives."""
import ctypes, sys
from ctypes import c_void_p, c_char_p, c_uint32, byref, create_string_buffer, Structure, c_char

L = ctypes.CDLL('/tmp/StormLib/b/libstorm.so')

class FIND(Structure):
    _fields_ = [('cFileName', c_char * 1024), ('szPlainName', c_char_p), ('dwHashIndex', c_uint32),
                ('dwBlockIndex', c_uint32), ('dwFileSize', c_uint32), ('dwFileFlags', c_uint32),
                ('dwCompSize', c_uint32), ('dwFileTimeLo', c_uint32), ('dwFileTimeHi', c_uint32), ('lcLocale', c_uint32)]

L.SFileOpenArchive.argtypes = [c_char_p, c_uint32, c_uint32, ctypes.POINTER(c_void_p)]
L.SFileFindFirstFile.argtypes = [c_void_p, c_char_p, ctypes.POINTER(FIND), c_char_p]
L.SFileFindFirstFile.restype = c_void_p
L.SFileFindNextFile.argtypes = [c_void_p, ctypes.POINTER(FIND)]
L.SFileFindClose.argtypes = [c_void_p]
L.SFileOpenFileEx.argtypes = [c_void_p, c_char_p, c_uint32, ctypes.POINTER(c_void_p)]
L.SFileGetFileSize.argtypes = [c_void_p, ctypes.POINTER(c_uint32)]
L.SFileReadFile.argtypes = [c_void_p, c_void_p, c_uint32, ctypes.POINTER(c_uint32), c_void_p]
L.SFileCloseFile.argtypes = [c_void_p]

STREAM_FLAG_READ_ONLY = 0x100

def open_archive(path):
    h = c_void_p()
    if not L.SFileOpenArchive(path.encode(), 0, STREAM_FLAG_READ_ONLY, byref(h)):
        raise OSError(f'cannot open {path}')
    return h

def listing(h, mask='*'):
    fd = FIND()
    f = L.SFileFindFirstFile(h, mask.encode(), byref(fd), None)
    out = []
    if not f:
        return out
    while True:
        out.append((fd.cFileName.decode('latin1'), fd.dwFileSize))
        if not L.SFileFindNextFile(f, byref(fd)):
            break
    L.SFileFindClose(f)
    return out

def read(h, name):
    fh = c_void_p()
    if not L.SFileOpenFileEx(h, name.encode('latin1'), 0, byref(fh)):
        return None
    hi = c_uint32()
    size = L.SFileGetFileSize(fh, byref(hi))
    buf = create_string_buffer(size)
    got = c_uint32()
    L.SFileReadFile(fh, buf, size, byref(got), None)
    L.SFileCloseFile(fh)
    return buf.raw[:got.value]
