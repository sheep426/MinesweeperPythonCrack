import sys
import psutil
import ctypes 
import win32api
import struct
from ctypes.wintypes import *

OpenProcess = ctypes.windll.kernel32.OpenProcess
OpenProcess.restype = HANDLE
OpenProcess.argtypes = (DWORD, BOOL, DWORD)


ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
ReadProcessMemory.restype = BOOL
ReadProcessMemory.argtypes = (HANDLE, LPCVOID, LPVOID, DWORD, DWORD)

WriteProcessMemory = ctypes.windll.kernel32.WriteProcessMemory
WriteProcessMemory.restype = BOOL
WriteProcessMemory.argtypes = (HANDLE, LPVOID, LPCVOID, DWORD, DWORD)

VirtualAllocEx = ctypes.windll.kernel32.VirtualAllocEx
VirtualAllocEx.restype = LPVOID
VirtualAllocEx.argtypes = (HANDLE, LPVOID, DWORD, DWORD, DWORD)

PROCESS_ALL_ACCESS =  (0x000F0000|0x00100000|0xFFF)
VIRTUAL_MEM = (0x1000|0x2000)
PAGE_READWRITE = 0x00000040

class mine_obj():
    def __init__(self,pid):
        self.row_address = 0x1005338
        self.col_address = 0x1005334
        self.game_time_address = 0x100579C
        self.bome_count_address = 0x1005194
        self.pid = pid

        self.handle =OpenProcess(PROCESS_ALL_ACCESS,False,int(pid))
        if not self.handle:
            print ("error get handle of pid %s" % pid)
            exit(1)

    def read_memory(self,handle,address,size):
        #buffer = (c_byte * getlenght(type))()
        ##dwNumberOfBytesRead = ReadProcessMemory.argtypes[-1](0)
        numberOfBytesRead = 0
        buffer = ctypes.c_int()
        result  = ReadProcessMemory(handle, address, ctypes.byref(buffer), size,numberOfBytesRead)
        if result is None or result == 0:
            raise Exception("error %s" % ctypes.GetLastError() )
        '''
        暂时不知道要传入什么进去才能得到
        if numberOfBytesRead != size:
            raise Exception(" read len error get " % numberOfBytesRead )
        '''
        return buffer.value

    def get_row_data(self):
        return self.read_memory(self.handle,self.row_address,4)

    def get_col_data(self):
        return self.read_memory(self.handle,self.col_address,4)

    def get_game_time_data(self):
        return self.read_memory(self.handle,self.bome_count_address,4)

    def get_bome_count_data(self):
        return self.read_memory(self.handle,self.game_time_address,4)

    def refresh_data(self):
        return 0

    def allocate(self,hProcess, lpAddress, dwSize, flAllocationType, flProtect):
        lpBuffer = VirtualAllocEx(hProcess, lpAddress, dwSize, flAllocationType, flProtect)
        if lpBuffer is None or lpBuffer == 0:
            raise Exception('Error: %s' %ctypes.GetLastError())

        return lpBuffer


    def write_buffer(self,hProcess, lpBaseAddress, lpBuffer, nSize):
        dwNumberOfBytesWritten = WriteProcessMemory.argtypes[-1]()
        #result = WriteProcessMemory(hProcess, lpBaseAddress, lpBuffer, nSize, ctypes.addressof(dwNumberOfBytesWritten))
        result = WriteProcessMemory(hProcess, lpBaseAddress, lpBuffer, nSize, 0)
        if result is None or result == 0:
            raise Exception('Error: %s' % GetLastError())

    def stop_time(self):
        #6bytes
        shellcode = "\x90\x90\x90\x90\x90\x90"
        shellcode_length = 6
        game_time_add_asm_address = 0x1002FF5
        arg_address = self.allocate(self.handle,game_time_add_asm_address,shellcode_length,VIRTUAL_MEM,PAGE_READWRITE)
        whhh=self.write_buffer(self.handle,arg_address,shellcode,shellcode_length)


def injectDll(app_name=None):
    PAGE_READWRITE = 0x04
    PROCESS_ALL_ACCESS =  (0x000F0000|0x00100000|0xFFF)
    VIRTUAL_MEM = (0x1000 | 0x2000)

    #dll_path  = "bin/CheatTools.dll".encode("ascii",'ignore')
    #dll_len = len(dll_path)

    pid_list = psutil.pids()
    found = False

    for pid  in pid_list:
        process_data = psutil.Process(pid)
        if process_data.name() == app_name:
            found = True
            break
    print ('pid',pid)

    if found:
        mine_data = mine_obj(pid)
        print (mine_data.get_row_data() )
        print (mine_data.get_col_data() )
        print (mine_data.get_bome_count_data() )
        mine_data.stop_time()
    else:
        print ("%s not found" % app_name)

    #先测试时间不增加。inc替换为nop

    '''
    arg_address = kernel32.VirtualAllocEx(handle_process,None,dll_len,VIRTUAL_MEM,PAGE_READWRITE)
    written = c_int(0)
    whhh=kernel32.WriteProcessMemory(handle_process,arg_address,dll_path,dll_len,byref(written))
    print('arg_address:%x'%arg_address,whhh)

    handle_kernel32=win32api.GetModuleHandle('kernel32.dll')
    handle_loadlib =win32api.GetProcAddress(handle_kernel32, 'LoadLibraryA')
    print('%x'%handle_kernel32,'%x'%handle_loadlib)
    thread_id=c_ulong(0)
    handle= kernel32.CreateRemoteThread(handle_process, None,0,handle_loadlib,arg_address, 0,byref(thread_id)  )
    print(handle)
    return handle_kernel32
    '''


injectDll("winmine.exe")

    
