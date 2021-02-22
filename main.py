import sys
import psutil
from ctypes import *
import win32api

print ("dll injector")


def injectDll(app_name=None):
    PAGE_READWRITE = 0x04
    PROCESS_ALL_ACCESS =  (0x000F0000|0x00100000|0xFFF)
    VIRTUAL_MEM = (0x1000 | 0x2000)

    dll_path  = "bin/CheatTools.dll".encode("ascii",'ignore')
    dll_len = len(dll_path)
    kernel32 = windll.kernel32

    pid_list = psutil.pids()

    for pid  in pid_list:
        process_data = psutil.Process(pid)
        if process_data.name() == app_name:
            break
    print ('pid',pid)

    handle_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS,False,int(pid))
    if not handle_process:
        print ("error get handle of pid %s" % pid)

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


injectDll("winmine1.exe")

    
