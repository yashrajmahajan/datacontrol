import json
import mmap
import sys
import threading
import time
from collections import OrderedDict
from key_value_ds import setting


def is_legit(val, val_type="key"):
    
    if val_type == "key":
        if not isinstance(val, str):
            raise ValueError(f"Key [{val}] must be of type str.")
        return len(val) <= setting.maxkey
    elif val_type == "value":
        if isinstance(val, dict):
            return sys.getsizeof(val) <= setting.maxvalue
        raise ValueError(f"Value [{val}] must be of type dict.")


class DataStoreVO:

    #A simple ValueObject class which can be used to access value based on its ttl if provided.
       
    

    def __init__(self, value, created_at, ttl, *args, **kwargs):
        self.value = value
        self.ttl = ttl
        self.created_at = created_at

    def is_expired(self):
        if self.ttl is None:
            return False
        curr_ts = int(time.time() * 1000)
        return (curr_ts - self.created_at) > self.ttl * 1000


class ds:
    def __init__(self, file_descriptor, *args, **kwargs):
        self.__fd = file_descriptor
        self.__mmap = self._get_mmaped_fd()
        self.__data = OrderedDict()
        self.__lock = threading.Lock()
        self._read_data()

    def _get_mmaped_fd(self) -> mmap.mmap:

            #creates an mmap object for the provided file_descriptor.
        try:
            mmaped_fd = mmap.mmap(self.__fd, 0, access=mmap.ACCESS_WRITE)
            mmaped_fd.resize(setting.maxstorage)
            return mmaped_fd
        except mmap.error:
            raise

    def _read_data(self) -> None:
        
        raw_data = self.__mmap[:].decode('ascii').rstrip('\0')
        self.__data = json.loads(raw_data)

    def create(self, key, value, ttl=None) -> None:
        """
            Creates a new entry for the given key with the value in data if and only if,
                1. The key is not already present.
                2. Both key and value satisfies the size constraints.
                3. If ttl is provided, it must be an integer in milli-seconds

        """
        with self.__lock:
            if key in self.__data:
                raise ValueError(f"Key '{key}' already present.")
            if is_legit(key, val_type="key") and is_legit(value, val_type="value"):
                if ttl is not None:
                    try:
                        ttl = int(ttl)
                    except:
                        raise ValueError(f"Time-to-live {ttl} must be an integer value.")
                value_arr = [value, int(time.time() * 1000), ttl]
                self.__data[key] = value_arr
                self.flush()
            else:
                raise ValueError(
                    f"Either provided key(allowed_size:{setting.maxkey} characters) or value(allowed_size:{setting.maxvalue} bytes) doesn't meet the size setting.")

    def delete(self, key) -> None:
        
        #Deletes the key-value pair from data.If key is not present it will ignore.
        
        with self.__lock:
            if key not in self.__data:
                return  # Ignore if key is non-existent
            del self.__data[key]
            self.flush()

    def get(self, key) -> dict:
        
        with self.__lock:
            if key not in self.__data:
                raise ValueError(f"Key [{key}] not in datastore.")
            value = DataStoreVO(*self.__data.get(key))  
            if value.is_expired():
                self.__data.pop(key)
                self.flush()
                raise ValueError(f"Key [{key}] Time-to-live expired.")
            return value.value

    def delall(self):
        
        #Additional method to flush the database and start new.
        
        with self.__lock:
            self.__data = dict()
            self.flush()

    def flush(self) -> None:
        
        #Writes the data to mmap by converting it to bytes and filling the unused space with null byte char.
        
        self.__mmap.seek(0)
        data_string = bytes(json.dumps(self.__data).encode('ascii'))
        self.__mmap.write(data_string)
        empty_space_bytes = self.__mmap.size() - self.__mmap.tell()
        self.__mmap[self.__mmap.tell():] = b'\0' * empty_space_bytes

    def __getitem__(self, item):
        
        return self.get(item)
