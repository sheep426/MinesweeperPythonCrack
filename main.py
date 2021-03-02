#coding:utf-8
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
MEM_DECOMMIT  = 0x00004000

class mine_obj():
    def __init__(self,pid):
        self.row_address = 0x01005338
        self.col_address = 0x01005334
        self.game_time_address = 0x100579C
        self.bome_count_address = 0x01005194
        self.pid = pid

        self.block_start_address = 0x01005340

        self.handle =OpenProcess(PROCESS_ALL_ACCESS,False,int(pid))
        if not self.handle:
            print ("error get handle of pid %s" % pid)
            raise Exception("error %s" % ctypes.GetLastError() )
            exit(1)

    def read_memory(self,handle,address,size):
        #buffer = (c_byte * getlenght(type))()
        ##dwNumberOfBytesRead = ReadProcessMemory.argtypes[-1](0)
        numberOfBytesRead = 0
        if size == 4:
            buffer = ctypes.c_int()
        elif size ==2:
            buffer = ctypes.c_short()
        elif size ==1:
            buffer = ctypes.c_char()
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
        return self.read_memory(self.handle,self.game_time_address,4)

    def get_bome_count_data(self):
        return self.read_memory(self.handle,self.bome_count_address,4)

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
            raise Exception('Error: %s' %ctypes.GetLastError())
        return result

    def stop_time(self):
        #6bytes
        #这里应该要用virtualProtect来绕过dep的保护。但是不知道为什么不需要直接写入就可以了.
        shellcode = b"\x90\x90\x90\x90\x90\x90"
        shellcode_length = 6
        game_time_add_asm_address = 0x1002FF5
        self.write_buffer(self.handle,game_time_add_asm_address,shellcode,shellcode_length)

    def disable_bome(self):
        #这里是把跳转去掉，增加了一个
        #这里应该要用virtualProtect来绕过dep的保护。但是不知道为什么不需要直接写入就可以了.
        shellcode = b"\x90\x90\x90\x90\x58"
        shellcode_length = len(shellcode)
        check_bome_asm_address = 0x10035AB
        self.write_buffer(self.handle,check_bome_asm_address,shellcode,shellcode_length)

    def get_mine_list(self):
        mine_dict = {}
        col_count = self.get_col_data()
        row_count = self.get_row_data()

        for row in range(1,row_count+1):
            for col in range(1,col_count+1):
                address = int( hex(self.block_start_address + row * 32 + col),16)
                block_data = self.read_memory(self.handle,address,1)
                if not row in mine_dict:
                    mine_dict[row] = {}
                if block_data == b'\x8f':
                    mine_dict[row][col] = True
                else:
                    mine_dict[row][col] = False
        return mine_dict

    def click(self,x,y):
        '''
        push ebp
        mov ebp,esp
		push dword ptr 3
		push dword ptr 4
		mov eax, 0x1003512
		call eax
        xor eax,eax
        mov esp,ebp
        pop ebp
        ret
        '''
        shellcode_list = []
        shellcode_list.append(b'\x55\x89\xE5\x6a')
        shellcode_list.append(bytes([x]))
        shellcode_list.append(b'\x6a')
        shellcode_list.append(bytes([y]))
        shellcode_list.append(b'\xb8\x12\x35\x00\x01\xFF\xD0\x31\xC0\x89\xEC\x5D\xC3')
       
        shellcode = b''.join( shellcode_list )
        shellcode_length = len(shellcode) 
        arg_address = self.allocate(self.handle,0,shellcode_length,VIRTUAL_MEM,PAGE_READWRITE)
        whhh=self.write_buffer(self.handle,arg_address,shellcode,shellcode_length)

        thread_id = ctypes.c_ulong(0)
        thread =ctypes.windll.kernel32.CreateRemoteThread(self.handle,None,0,arg_address,None,0,ctypes.byref(thread_id))
        if not thread:
            raise Exception('Error: %s' %ctypes.GetLastError())
        ctypes.windll.kernel32.WaitForSingleObject(thread,0xFFFFFFFF)
        #一定要close要不会挂，暂时原因不知道
        ctypes.windll.kernel32.CloseHandle(thread)
        #调试的时候这句要关闭，要不attach上去的时候地址就被处理了
        ctypes.windll.kernel32.VirtualFreeEx(self.handle, arg_address, shellcode_length, MEM_DECOMMIT)

    def revert_time(self):
        '''
        push ebp
        mov ebp,esp
        mov eax,0
        mov [0x100579c],eax
        mov esp,ebp
        pop ebp
        ret
        '''
        shellcode = b"\x55\x89\xE5\xB8\x00\x00\x00\x00\xA3\x9C\x57\x00\x01\x89\xEC\x5D\xC3"
        self.run_shell_code(shellcode)

    def run_shell_code(self,shellcode):
        shellcode_length = len(shellcode) 
        arg_address = self.allocate(self.handle,0,shellcode_length,VIRTUAL_MEM,PAGE_READWRITE)
        whhh=self.write_buffer(self.handle,arg_address,shellcode,shellcode_length)

        thread_id = ctypes.c_ulong(0)
        thread =ctypes.windll.kernel32.CreateRemoteThread(self.handle,None,0,arg_address,None,0,ctypes.byref(thread_id))
        if not thread:
            raise Exception('Error: %s' %ctypes.GetLastError())
        ctypes.windll.kernel32.WaitForSingleObject(thread,0xFFFFFFFF)
        #一定要close要不会挂，暂时原因不知道
        ctypes.windll.kernel32.CloseHandle(thread)
        #调试的时候这句要关闭，要不attach上去的时候地址就被处理了
        ctypes.windll.kernel32.VirtualFreeEx(self.handle, arg_address, shellcode_length, MEM_DECOMMIT)


    def auto_play(self):
        mine_dict = self.get_mine_list()
        col_count = self.get_col_data()
        row_count = self.get_row_data()
        for row in range(1,row_count+1):
            for col in range(1,col_count+1):
                if  not mine_dict[row][col]:
                    self.click(row,col)

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
        print (mine_data.get_mine_list() )
        #mine_data.revert_time()
        #mine_data.auto_play()
        #mine_data.stop_time()
        mine_data.disable_bome()
    else:
        print ("%s not found" % app_name)


injectDll("winmine.exe")

    
