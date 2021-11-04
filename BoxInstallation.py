
from datetime import datetime
from logging import FileHandler
import os
from sqlite3.dbapi2 import version
import subprocess

import aiohttp
from config import *
from update.handler.sqlhandler import SqlHandler
from easilogging import EasiLogging
from util import *
from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove

import zipfile
import signal
import config
import requests
import sqlite3
import json

#Aqui vao conter todos os scripts/dependencias necessarias para instalar e configurar o box pela primeira vez 
#talvez trocar para varias subpastas com coisas especificas necessarias na instalacao e reinstalacao

LOGGING = 0
class BoxInstallation():

    # def installBox():
    #     EasiLogging.info("Preparing installation")
    #     pass

    # def signal_handler():
    #     signal.signal(signal.SIGUSR2, BoxInstallation.installBox)
        
    async def getCoord(loop):  #first time installing
        async with aiohttp.ClientSession(loop=loop,connector=aiohttp.TCPConnector(verify_ssl=False)) as client:  
            
                macaddress = Util.get_mac_address_async()
                url = await AsyncConfig.get("_ENDPOINT", Config._DEFAULT_ENDPOINT)
                endpoint = url + Config._DEFAULT_ENDPOINT_GET_COORD
                myobj = {'macaddress': macaddress}
                async with client.post(endpoint, data=myobj) as response:
                    resp_json = json.loads(await response.text())
                    latitude = resp_json['lat']
                    longitude = resp_json['long']

                    await AsyncConfig.set("_LAT", latitude)
                    await AsyncConfig.set("_LONG", longitude)

                    EasiLogging.info('Terminated')

    async def getWeather(loop):
        EasiLogging.debug("BoxInstallation: executing getWeather")
        async with aiohttp.ClientSession(loop=loop,connector=aiohttp.TCPConnector(verify_ssl=False)) as client:  
            datetime_sql = await AsyncConfig.get("vLAST_TIME_WEATHER", defaultValue=None)
            datetimenow = datetime.now().timestamp()
            if(datetime_sql == 'None'):
                await AsyncConfig.set("vLAST_TIME_WEATHER", 0)
            else:
                datetime_hourlater = float(datetime_sql) + 3600
                if(datetimenow >= datetime_hourlater):
                    latitude = await AsyncConfig.get("_LAT")
                    longitude = await AsyncConfig.get("_LONG")

                    url = await AsyncConfig.get("_ENDPOINT_API_WEATHER")   #this part is wrong in so many levels but it works so its fine
                    q = latitude + ',' + longitude                       #gotta add to sql key and url so we dont do this ugly shit again
                    myobj = {'key': '7eaefe5c7b7f4b66bc8160809202112', 'q': q}

                    async with client.post(url, data=myobj) as response:
                        resp_json = json.loads(await response.text())
                        temperature = resp_json['current']['temp_c']
                        cloud = resp_json['current']['cloud']
                        await AsyncConfig.set("vTEMPERATURE_C", temperature)
                        await AsyncConfig.set("vCLOUD", cloud)
                        await AsyncConfig.set("vLAST_TIME_WEATHER", datetimenow)
                else:
                    EasiLogging.info("BoxInstallation: Too early to get weather")
                    return

            

            EasiLogging.debug('BoxInstallation: finished getWeather')

    # def replace_line_cash(file_name, resp):
    #     store_idx = resp["store_idx"]
    #     product_idx = resp["product_idx"]
    #     lines = open(file_name, 'r').readlines()
    #     lines[19] =  'subscribe_topic = \"v1/store/'+store_idx+'/device_idx/'+product_idx+'/janus/to\"# Topic for incoming messages'
    #     lines[21] =  'publish_topic = \"v1/store/'+store_idx+'/device_idx/'+product_idx+'/janus/from\" # Topic for outgoing messages'
    #     out = open(file_name, 'w')
    #     out.writelines(lines)
    #     out.close()

    def search_string_in_file(file_name, string_to_search):
        
        line_number = 0
        # Open the file in read only mode
        with open(file_name, 'r') as read_obj:
            # Read all lines in the file one by one
            for line in read_obj:
                # For each line, check if line contains the string
                line_number += 1
                if string_to_search in line:
                    if "bridge" in line and "bridge" not in string_to_search:
                        continue
                    else:
                        # If yes, then add the line number & line as a tuple in the list
                        return line_number


    
    def replace_line_middleware(file_name, resp):
        store_idx = resp["store_idx"]
        mac_address = Util.get_mac_address_sync().upper()
        password = Config.get_password()
        keyword_dict = {
                        'connection bridge' : 'connection bridge-'+mac_address+'\n',
                        'remote_username' : 'remote_username '+mac_address+'\n',
                        'remote_password' : 'remote_password '+password+'\n',
                        'bridge_certfile' : 'bridge_certfile /mnt/easicash/certs/cert/'+mac_address+'.crt\n',
                        'bridge_keyfile' : 'bridge_keyfile /mnt/easicash/certs/cert/'+mac_address+'.key\n',
                        '/# out 2' : 'topic v1/store/'+str(store_idx)+'/# out 2\n',
                        '/# in 2' : 'topic v1/store/'+str(store_idx)+'/# in 2\n',
                        'certfile' : 'certfile /mnt/easicash/certs/cert/'+mac_address+'.crt\n',
                        'keyfile' : 'keyfile /mnt/easicash/certs/cert/'+mac_address+'.key\n',
                }
        lines = open(file_name, 'r').readlines()
        for keyword in keyword_dict:
            response = BoxInstallation.search_string_in_file(file_name, keyword)
            if(response == None):
                EasiLogging.error("Response was None At keyword: \'%s\'", keyword)
                break
            lines[response-1] = keyword_dict[keyword]
        out = open(file_name, 'w')
        out.writelines(lines)
        out.close()

    def changeBrokerConfig(resp):
        if(Config.get_bool("SYSTEM_IS_MIDDLEWARE")):
            BoxInstallation.replace_line_middleware('/mnt/easicash/mosquitto/mqtt.conf', resp)       

    ############################################################################################
    #update box functions
    ############################################################################################
    
    #
    # Retorna uma lista dos nomes do arquivo do diretorio desejado
    #
    def get_files(dir):
        
        files = sorted(os.listdir(dir))
        return files
    

    #
    # Inicia update no Box
    #
    def update_box():
        user='easi'
        password='$easi$'
        database='easi'
        
        #EasiMigrate.request_update_files() #implementar funcao q faz request para o servidor com numero de versao atual

        dir ='/mnt/easicash/easiboxsrv/update/data/'
        files = BoxInstallation.get_files(dir)

        SqlHandler.create_dump_sql(user, password, database, dir)
        
        BoxInstallation.stopServices()

        FileHandler.backup_files()
        connection = pymysql.connect(unix_socket='/var/run/mysqld/mysqld.sock',
                            user=user,
                            password=password,
                            database=database,
                            cursorclass=pymysql.cursors.DictCursor)

        EasiLogging.debugc(LOGGING, "Connection made")
        try:
            for file in files:
                with zipfile.ZipFile(dir + str(file), 'r') as zip_ref:
                    version_dir = dir + 'temp/' + str(file)
                    zip_ref.extractall(dir + 'temp/' + str(file))
                    update_files = BoxInstallation.get_files(version_dir) # update files contem um arquivo txt com instrucoes para o update de arquivos
                                                                            # além de um arquivo script sql para executar no banco 
                    sql_update = SqlHandler.sql_update(update_files[1], connection, dir + 'temp/' + str(file))
                    if not sql_update:
                        #troca pro dump e restarta serviços
                        SqlHandler.restore_sql()
                        BoxInstallation.startServices()
                        return

                    file_update = FileHandler.file_update(update_files, dir + 'temp/' + str(file))
                    if not file_update:
                        FileHandler.restore_files()
                        BoxInstallation.startServices()
                        #substitui tudo pelo backup e restarta serviços
                        pass
                    
        except Exception as e:
            pass

    def stopServices():
        EasiLogging.debugc(LOGGING, "stopping services")
        if(Config.get_bool("SYSTEM_IS_MIDDLEWARE")):
            p1 = subprocess.call("service easiboxmidsrv stop", shell=True)
            p2 = subprocess.call("service mosquitto stop", shell=True)

        if(Config.get_bool("SYSTEM_IS_CASH") or Config.get_bool("SYSTEM_IS_GUARD")):
            p1 = subprocess.call("service janus stop", shell=True)
            p2 = subprocess.call("service easiboxsrv stop", shell=True)
            
        EasiLogging.debugc(LOGGING, "services stopped")

    def startServices():
        EasiLogging.debugc(LOGGING, "starting services")
        if(Config.get_bool("SYSTEM_IS_MIDDLEWARE")):
            p1 = subprocess.call("service easiboxmidsrv start", shell=True)
            p2 = subprocess.call("service mosquitto start", shell=True)

        if(Config.get_bool("SYSTEM_IS_CASH") or Config.get_bool("SYSTEM_IS_GUARD")):
            p1 = subprocess.call("service janus start", shell=True)
            p2 = subprocess.call("service easiboxsrv start", shell=True)

        EasiLogging.debugc(LOGGING, "services started")
        
        EasiLogging.debugc(LOGGING, "started services")
