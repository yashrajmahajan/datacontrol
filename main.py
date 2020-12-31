import fcntl
import os
from .import setting
from .datastr import ds


def filename() -> str:
    
    #Creates a unique file name for ds
    import uuid
    uniq_append_string = uuid.uuid4().hex
    return "LOCAL_STORAGE_{}".format(uniq_append_string)


def instance(file_name=None) -> ds:
    if file_name is None:
        file_name = filename()
    full_file_name = f"{setting.storagepath}/{file_name}"
    file_descriptor = os.open(full_file_name, os.O_CREAT | os.O_RDWR)


   #Try to acquire file lock. 
    
    try:
        print(f"Acquiring file lock on {file_name}")
        fcntl.flock(file_descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise BlockingIOError(f"Resource '{file_name}' is already locked'")
    except Exception:
        raise
    else:
        print(f"File lock acquired on {file_name}")

    #File lock acquired. 

    if not os.path.isfile(full_file_name) or os.fstat(file_descriptor).st_size == 0:
        with open(full_file_name, 'ab') as f:
            string = "{}"
            f.write(bytes(string.encode('ascii')))
    return ds(file_descriptor)

__all__ = ['instance']