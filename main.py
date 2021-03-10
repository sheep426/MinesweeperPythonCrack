#coding:utf-8
import sys
import psutil
import ctypes 
import win32api
import struct
from ctypes.wintypes import *

import mine_injector

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
        mine_data = mine_injector.mine_obj(pid)
        print (mine_data.get_mine_list() )
        #mine_data.revert_time()
        mine_data.auto_play()
        #mine_data.stop_time()
        #mine_data.disable_bome()
    else:
        print ("%s not found" % app_name)

if __name__ == "__main__":
    injectDll("winmine.exe")

    
