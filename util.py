
import aiofiles
import aiofiles.os

from getmac import get_mac_address
from config import *
from asyncconfig import AsyncConfig

import time
import logging

from stat import S_ISDIR, S_ISREG
from subprocess import Popen, PIPE

LOGGING = 0
class Util:

    def is_ntp_synced():
        process = Popen(["ntpstat"], stdout=PIPE)
        (output, err) = process.communicate()
        return process.wait() == 0

    async def is_file_async(file_path):
        try:
            ret_stat = await aiofiles.os.stat(file_path)
            return bool(S_ISREG(ret_stat.st_mode)  != 0)
        except Exception as e:
            EasiLogging.debug("Could not possible get file information: " + str(e))
            return False
            
    async def get_file_size_async(file_path):
        try:
            ret_stat = await aiofiles.os.stat(file_path)
            return ret_stat.st_size
        except Exception:
            return -1

    def get_mac_address_sync():
        return get_mac_address(interface=Config.get("_NETWORK_IFACE", Config._DEFAULT_NETWORK_IFACE)).replace(':', '')

    async def get_mac_address_async():
        return get_mac_address(interface= await AsyncConfig.get("_NETWORK_IFACE", Config._DEFAULT_NETWORK_IFACE)).replace(':', '')

        
    def get_epoch_miliseconds():
        return time.time_ns() // 1000000


