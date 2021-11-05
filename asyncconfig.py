import logging
import time

from easilogging import EasiLogging

LOGGING = 0

class AsyncConfig():

    dbpool = None
    loop = None

    async def set_db_pool_loop(pool, loop):
        AsyncConfig.dbpool = pool
        AsyncConfig.loop = loop

    async def get_int(key, defaultValue=None):
        return int(await AsyncConfig.get(key, defaultValue))
        
    async def get_bool(key, defaultValue=None):
        return bool(int(await AsyncConfig.get(key, defaultValue)))

    async def set(key, value):
        if(AsyncConfig.dbpool is None):
            return setattr(AsyncConfig, key, value)
        else:
            setattr(AsyncConfig, key, value)
            async with AsyncConfig.dbpool.acquire() as conn:
                async with conn.cursor() as cur:
                    if key.startswith("v"):
                        await cur.execute("SELECT value FROM tbl_cash_box_var WHERE `key`=%s", (key,))
                    elif key.startswith("_"):
                        await cur.execute("SELECT value FROM tbl_cash_box_config_sys WHERE `key`=%s", (key,))
                    else:
                        await cur.execute("SELECT value FROM tbl_cash_box_config  WHERE `key`=%s", (key,))            
                    row = await cur.fetchone()

                    if row is None:
                        if key.startswith("v"):
                            await cur.execute("INSERT INTO tbl_cash_box_var(`key`, value) VALUES (%s,%s)", (key,value,))
                        elif key.startswith("_"):
                            await cur.execute("INSERT INTO tbl_cash_box_config_sys(`key`, value) VALUES (%s,%s)", (key,value,))
                        else:
                            await cur.execute("INSERT INTO tbl_cash_box_config(`key`, value) VALUES (%s,%s)", (key,value,))         
                    else:
                        if key.startswith("v"):
                            await cur.execute("UPDATE tbl_cash_box_var SET value=%s WHERE `key`=%s", (value,key,))
                        elif key.startswith("_"):
                            await cur.execute("UPDATE tbl_cash_box_config_sys SET value=%s WHERE `key`=%s", (value,key,))
                        else:
                            await cur.execute("UPDATE tbl_cash_box_config SET value=%s WHERE `key`=%s", (value,key,))          
                    await conn.commit()

    async def get(key, defaultValue=None):
        if(AsyncConfig.dbpool is None):
            return str(getattr(AsyncConfig, key))
        else:
            if(hasattr(AsyncConfig,key)):
                return str(getattr(AsyncConfig, key))
            else:
                async with AsyncConfig.dbpool.acquire() as conn:
                    async with conn.cursor() as cur:
                        if key.startswith("v"):
                            await cur.execute("SELECT value FROM tbl_cash_box_var WHERE `key`=%s", (key,))
                        elif key.startswith("_"):
                            await cur.execute("SELECT value FROM tbl_cash_box_config_sys WHERE `key`=%s", (key,))
                        else:
                            await cur.execute("SELECT value FROM tbl_cash_box_config  WHERE `key`=%s", (key,))

                        row = await cur.fetchone()
                        if(row is None):
                            return str(defaultValue)
                        else:
                            return str(row[0])
                            
    async def get_password():
        password = None
        while(password is None):
            password = await AsyncConfig.get("_LICENSE_KEY")
            if(password is None):
                sleep_time = 10
                EasiLogging.error("Password not set! sleeping for {} seconds".format(sleep_time))
                time.sleep(sleep_time) #time sleep para travar funcionamento do codigo
            
        return password
    async def get_product_idx():
        product_idx = None
        while(product_idx is None):
            product_idx = await AsyncConfig.get("_PRODUCT_IDX")
            if(product_idx is None):
                sleep_time = 10
                EasiLogging.error("Product idx not set! sleeping for {} seconds".format(sleep_time))
                time.sleep(sleep_time) #time sleep para travar funcionamento do codigo
            
        return product_idx

    async def get_store_idx():
        store_idx = None
        while(store_idx is None):
            store_idx = await AsyncConfig.get("_PRODUCT_STORE_IDX")
            if(store_idx is None):
                sleep_time = 10
                EasiLogging.error("Store idx not set! sleeping for {} seconds".format(sleep_time))
                time.sleep(sleep_time) #time sleep para travar funcionamento do codigo
            
        return store_idx