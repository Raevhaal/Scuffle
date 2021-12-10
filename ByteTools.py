import ctypes as c
from ctypes import wintypes as w
import struct


k32 = c.windll.kernel32

OpenProcess = k32.OpenProcess
OpenProcess.argtypes = [w.DWORD,w.BOOL,w.DWORD]
OpenProcess.restype = w.HANDLE

ReadProcessMemory = k32.ReadProcessMemory
ReadProcessMemory.argtypes = [w.HANDLE, w.LPCVOID, w.LPVOID, c.c_size_t, c.POINTER(c.c_size_t)]
ReadProcessMemory.restype = w.BOOL

WriteProcessMemory = k32.WriteProcessMemory
WriteProcessMemory.argtypes = [w.HANDLE, w.LPVOID, w.LPCVOID, c.c_size_t, c.POINTER(c.c_size_t)]
WriteProcessMemory.restype = w.BOOL

GetLastError = k32.GetLastError
GetLastError.argtypes = None
GetLastError.restype = w.DWORD

CloseHandle = k32.CloseHandle
CloseHandle.argtypes = [w.HANDLE]
CloseHandle.restype = w.BOOL


def GetValueFromAddress(processHandle, address, isFloat=False, is64bit=False, isString=False, is_short=False):
    error_code = -1

    if isString:
        data = c.create_string_buffer(16)
        bytesRead = c.c_ulonglong(16)
    elif is64bit:
        data = c.c_ulonglong()
        bytesRead = c.c_ulonglong()
    elif is_short:
        data = c.c_ushort()
        bytesRead = c.c_ulonglong(2)
    else:
        data = c.c_ulong()
        bytesRead = c.c_ulonglong(4)
        
    
    # Debug code
    # import PIDSearcher
    # address = 0
    # daValues = []
    # pid = PIDSearcher.GetPIDByName(b'SoulcaliburVI.exe')
    # while True:
        
    #     process_handle = OpenProcess(0x10 | 0x20 | 0x08, False, pid)
    #     successful = ReadProcessMemory(process_handle, address, c.byref(data), c.sizeof(data), c.byref(bytesRead))

    #     if successful:
    #         daValues.append(address)
            
    #     if(address > 7950032800):
    #         print("yay")
            
    #     address += 1
    
    successful = ReadProcessMemory(processHandle, address, c.byref(data), c.sizeof(data), c.byref(bytesRead))
    if not successful:
        e = GetLastError()
        print("ReadProcessMemory Error: Code " + str(e))
        error_code = e

    value = data.value

    if isFloat:
        return struct.unpack("!f", struct.pack('!I', data.value))[0]
    if is_short:
        return int(data.value)
    elif isString:
        try:
            return value.decode('utf-8')
        except:
            print("ERROR: Couldn't decode string from memory")
            return "ERROR"
    else:
        return int(value)


def GetBlockOfData(processHandle, address, size_of_block):
    data = c.create_string_buffer(size_of_block)
    bytesRead = c.c_ulonglong(size_of_block)
    successful = ReadProcessMemory(processHandle, address, c.byref(data), c.sizeof(data), c.byref(bytesRead))
    if not successful:
        e = GetLastError()
        print("Getting Block of Data Error: Code " + str(e))
    # print('{} : {}'.format(address, self.GetValueFromFrame(data, PlayerDataAddress.simple_move_state)))
    return data


def WriteBlockOfData(processHandle, address, block):
    data = block
    successful = WriteProcessMemory(processHandle, address, data, len(data), None)
    if not successful:
        e = GetLastError()
        print("Writing Block of Data Error: Code " + str(e))


def GetValueFromDataBlock(block, offset, is_float=False, is_short=False, is_byte=False, debug_print_raw=False):
    address = offset

    num_of_bytes = 4
    if is_short:
        num_of_bytes = 2
    if is_byte:
        num_of_bytes = 1

    bytes = block[address: address + num_of_bytes]
    if debug_print_raw:
        print(bytes)
    if not is_float and not is_short and not is_byte:
        return struct.unpack("<I", bytes)[0]
    if is_short:
        return struct.unpack("<H", bytes)[0]
    if is_float:
        return struct.unpack("<f", bytes)[0]
    if is_byte:
        return struct.unpack('>H', b'\x00' + bytes)[0]


def GetDataBlockAtEndOfPointerOffsetList(process_handle, starting_pointer, offsets, size_of_block):
    current_pointer = starting_pointer
    for i in range(len(offsets)):
        if i < len(offsets):
            current_pointer = GetValueFromAddress(process_handle, current_pointer + offsets[i], is64bit=True)
    return GetBlockOfData(process_handle, current_pointer, size_of_block)


