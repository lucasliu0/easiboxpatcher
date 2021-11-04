
from enum import Enum
import logging
import time

import pymysql.cursors

from easilogging import EasiLogging
from enum import Enum

LOGGING = 0
class Config():

    class RecorderAuthMode(Enum):
        DIGEST = 0
        BASIC = 1

        def __str__(self):
            return str(self.value)

        def equals(self, v):
            return self.value == v            

    class RecorderSchemaMode(Enum):
        SECURE = "https://"
        NOT_SECURE = "http://"

        def __str__(self):
            return str(self.value)

        def equals(self, v):
            return self.value == v                       

    #### Padrao
    DEFAULT_MQTT_BROKER_MIDDLEWARE = "127.0.0.1"
    DEFAULT_MQTT_PORT = 8883

    DEFAULT_ALARM_ENABLED = 0

    DEFAULT_AR_INTERVAL_GET_VIDEOS = 600
    DEFAULT_AR_PORT = 80
    DEFAULT_AR_SCHEMA = RecorderSchemaMode.NOT_SECURE
    DEFAULT_AR_IGNORE_CERT = True
    DEFAULT_AR_AUTH_MODE = RecorderAuthMode.DIGEST

    DEFAULT_AR_SUBTRACT_TIME_GET_VIDEO = 60
    DEFAULT_AR_DAYS_BEFORE_GET_VIDEOS = 8
    DEFAULT_AR_TIME_PRE_RECORD = 10
    DEFAULT_AR_TIME_POST_RECORD = 10
    DEFAULT_AR_RTPS_PORT = 554
    DEFAULT_AR_CHANNEL = 101

    DEFAULT_CR_PORT = 80
    DEFAULT_CR_SCHEMA = RecorderSchemaMode.NOT_SECURE
    DEFAULT_CR_IGNORE_CERT = True
    DEFAULT_CR_AUTH_MODE = RecorderAuthMode.DIGEST  
    DEFAULT_CR_RTPS_PORT = 554
    DEFAULT_CR_CHANNEL = 101

    #### Sistema
    _DEFAULT_ENDPOINT = 'https://easi.live/'
    _DEFAULT_ENDPOINT_API = 'https://api.easi.live/'
    _DEFAULT_CERT_CA_PATH = '/mnt/easicash/certs/ca'
    _DEFAULT_CERT_CERTIFICATES_PATH = '/mnt/easicash/certs/cert'
    _DEFAULT_MODULES_PATH = 'modules'
    _DEFAULT_NETWORK_IFACE = 'eth0'
    _DEFAULT_NETWORK_CHUNK_READ_FILE_SIZE = 4096
    _DEFAULT_NETWORK_CHUNK_DOWNLOAD_FILE_SIZE = 4096
    _DEFAULT_VIDEO_TMP_PATH = '/tmp/video'
    _DEFAULT_ALARM_RECORDER_PATH = 'recorders/alarm'
    _DEFAULT_CONTINUOUS_RECORDER_PATH = 'recorders/continuous'
    _DEFAULT_ENDPOINT_TOKEN = 'auth/lambda'
    _DEFAULT_ENDPOINT_UPLOAD_VIDEO = 'easiguard/getpresignedvideourl'
    _DEFAULT_ENDPOINT_GET_COORD = 'easicash/GetCoord'
    _DEFAULT_ENDPOINT_UPLOAD_EXCEPTION_OPERATION = 'api/registerCashExceptionOperations'
    _DEFAULT_ENDPOINT_GET_EXCEPTION_RULES = 'api/getAllExceptionRules'
    _DEFAULT_ENDPOINT_TOKEN_VALIDATE = 'auth/Validatetoken'
    _DEFAULT_ENDPOINT_GET_PRODUCT_STORE_IDX = 'api/Getproductintel'
    
    #### Variáveis
    

    def get_int(key, defaultValue=None):
        return int(Config.get(key, defaultValue))
        
    def get_bool(key, defaultValue=None):
        return bool(int(Config.get(key, defaultValue)))

    def set(key, value):
        setattr(Config, key, value)
        connection = pymysql.connect(unix_socket='/var/run/mysqld/mysqld.sock',
                            user='easi',
                            password='$easi$',
                            database='easi',
                            cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cur:
                if key.startswith("v"):
                    cur.execute("SELECT value FROM tbl_cash_box_var WHERE `key`=%s", (key,))
                elif key.startswith("_"):
                    cur.execute("SELECT value FROM tbl_cash_box_config_sys WHERE `key`=%s", (key,))
                else:
                    cur.execute("SELECT value FROM tbl_cash_box_config  WHERE `key`=%s", (key,))            
                row = cur.fetchone()

                if row is None:
                    if key.startswith("v"):
                        cur.execute("INSERT INTO tbl_cash_box_var(`key`, value) VALUES (%s,%s)", (key,value,))
                    elif key.startswith("_"):
                        cur.execute("INSERT INTO tbl_cash_box_config_sys(`key`, value) VALUES (%s,%s)", (key,value,))
                    else:
                        cur.execute("INSERT INTO tbl_cash_box_config(`key`, value) VALUES (%s,%s)", (key,value,))         
                else:
                    if key.startswith("v"):
                        cur.execute("UPDATE tbl_cash_box_var SET value=%s WHERE `key`=%s", (value,key,))
                    elif key.startswith("_"):
                        cur.execute("UPDATE tbl_cash_box_config_sys SET value=%s WHERE `key`=%s", (value,key,))
                    else:
                        cur.execute("UPDATE tbl_cash_box_config SET value=%s WHERE `key`=%s", (value,key,))          

                Config.dbconn.commit()
        finally:
            connection.close()

    def get(key, defaultValue=None):
        if(hasattr(Config,key)):
            return str(getattr(Config, key))
        else:
            connection = pymysql.connect(unix_socket='/var/run/mysqld/mysqld.sock',
                                user='easi',
                                password='$easi$',
                                database='easi',
                                cursorclass=pymysql.cursors.DictCursor)
            try:
                with connection.cursor() as cur:
                    if key.startswith("v"):
                        cur.execute("SELECT value FROM tbl_cash_box_var WHERE `key`=%s", (key,))
                    elif key.startswith("_"):
                        cur.execute("SELECT value FROM tbl_cash_box_config_sys WHERE `key`=%s", (key,))
                    else:
                        cur.execute("SELECT value FROM tbl_cash_box_config  WHERE `key`=%s", (key,))

                    row = cur.fetchone()
                    if(row is None):
                        if(defaultValue is None):
                            raise KeyError("Row doesn't exist and default value is None")
                        return str(defaultValue)
                    else:
                        return str(row['value'])
            except KeyError as e:
                EasiLogging.error(str(e))
                return False
            finally:
                connection.close()

    def get_password():
        password = 'None'
        while(password is 'None'):
            password = Config.get("_LICENSE_KEY")
            if(password is 'None'):
                sleep_time = 10
                EasiLogging.error("Password not set! sleeping for {} seconds".format(sleep_time))
                time.sleep(sleep_time) #time sleep para travar funcionamento do codigo
            
        return password
    

    def get_pos_code():
        pos_code = 'None'
        while(pos_code is 'None'):
            pos_code = Config.get("_POS_CODE")
            if(pos_code is 'None'):
                sleep_time = 10
                logging.error("POS Store Code not set! sleeping for {} seconds".format(sleep_time))
                time.sleep(sleep_time) #time sleep para travar funcionamento do codigo

        return pos_code


    def get_product_idx():
        product_idx = 'None'
        while(product_idx is 'None'):
            product_idx = Config.get("_PRODUCT_IDX")
            if(product_idx is 'None'):
                sleep_time = 10
                EasiLogging.error("Product idx not set! sleeping for {} seconds".format(sleep_time))
                time.sleep(sleep_time) #time sleep para travar funcionamento do codigo
            
        return product_idx

    def get_store_idx():
        store_idx = 'None'
        while(store_idx is 'None'):
            store_idx = Config.get("_PRODUCT_STORE_IDX")
            if(store_idx is 'None'):
                sleep_time = 10
                EasiLogging.error("Store idx not set! sleeping for {} seconds".format(sleep_time))
                time.sleep(sleep_time) #time sleep para travar funcionamento do codigo
            
        return store_idx
    
