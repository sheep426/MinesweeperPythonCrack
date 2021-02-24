import sys
import psutil
import ctypes 
import win32api
import struct

from ctypes.wintypes import BOOL
from ctypes.wintypes import DWORD
from ctypes.wintypes import HANDLE
from ctypes.wintypes import LPVOID
from ctypes.wintypes import LPCVOID


OpenProcess = ctypes.windll.kernel32.OpenProcess
OpenProcess.restype = HANDLE
OpenProcess.argtypes = (DWORD, BOOL, DWORD)


ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
ReadProcessMemory.restype = BOOL
ReadProcessMemory.argtypes = (HANDLE, LPCVOID, LPVOID, DWORD, DWORD)
PROCESS_ALL_ACCESS =  (0x000F0000|0x00100000|0xFFF)

class mine_obj():
    def __init__(self,pid):
        self.row_address = 0x1005338
        self.col_address = 0x1005334
        self.game_time_address = 0x100579C
        self.bome_count_address = 0x1005194
        self.pid = pid

        self.handle_process =OpenProcess(PROCESS_ALL_ACCESS,False,int(pid))
        if not self.handle_process:
            print ("error get handle of pid %s" % pid)
            exit(1)

    def read_memory(pid,address,size):
        #buffer = (c_byte * getlenght(type))()
        dwNumberOfBytesRead = ReadProcessMemory.argtypes[-1]()
        buffer = ctypes.create_string_buffer(size)
        result  = ReadProcessMemory(pid, address, buffer, size, ctypes.addressof(dwNumberOfBytesRead) )
        if result is None or result == 0:
            raise Exception("error %s" % ctypes.GetLastError() )

    def get_row_data(self):
        return self.read_memory(self.pid,self.row_address,4)

    def get_col_data(self):
        return self.read_memory(self.pid,self.col_address,4)

    def get_game_time_data(self):
        return self.read_memory(self.pid,self.bome_count_address,4)

    def refresh_data(self):
        return 0


def injectDll(app_name=None):
    PAGE_READWRITE = 0x04
    PROCESS_ALL_ACCESS =  (0x000F0000|0x00100000|0xFFF)
    VIRTUAL_MEM = (0x1000 | 0x2000)

    #dll_path  = "bin/CheatTools.dll".encode("ascii",'ignore')
    #dll_len = len(dll_path)

    pid_list = psutil.pids()

    for pid  in pid_list:
        process_data = psutil.Process(pid)
        if process_data.name() == app_name:
            break
    print ('pid',pid)

    mine_data = mine_obj(pid)
    print (mine_data.get_row_data() )

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


injectDll("winmine1.exe")

    
