# datacontrol

================================Problem statement==============================


Build a file-based key-value data store that supports the basic CRD(create, read and delete) operations. This data store is meant to be used as a local storage for one single process on one laptop. The data store must be exposed as a library to client that can instantiate a class and work with the data store.


=============The data store will support the following functional requirements================

1. It can be initilized using as optional file path it one is not provided, it will reliably create itself in a reasonable location on laptop.

2. New key value pair can be addded to the data store using the create operation, the key is always string-capped at 32 char the value is always a JOSON object- capped at 60kb

3. If create is invoked for an exsting key an appropriate error must be retured.

4. Read operation on a key can be performe by providing a key and receiving value in respose JSON object.

5. A delete opration can be perform by providign key.

6. Every key supports setting a time-to-live property, when it is optional. If provided, it will be evaluated as an integer defining the number of senconds. The key must be retained in the data stored Onece the time to live for a key has expiered. key will no longer be available for read or delete operation.

7. Appropriate error responsed must always be returned to a client, if it uses a data store in unexpected way or breached any limits.


***********The data store will also support the following non-fuctional requiredments*****************

1. The size of the file storing data must never exceed 1GB

2. More than one client process cannot be allowed to use the same file as a data store at any given time.

3. A client proccess is allowed to access the data store using multiple threads, if it desires to.

4. A client will bear as little memory costs as possible to use this data store, while deriving maximum performance with respect to response times for accessing the data store.

=================================================================================================================

Usage

=================Creating an instance===========================================

import key_value_ds
d_instance = key_value_ds.get_instance()


=================Creating an data================================================

data_key = 'test_key'
data_value = {"value": 1}
time_to_live = 5*1000
ds_instance.create(data_key, data_value, ttl=time_to_live)

=================Retrieving data==================================================

retrieve_key = 'test_key'
ds_instance.get(retrieve_key)


=================Deleting data======================================================

delete = 'test_key'
ds_instance.delete(key_to_delete)

=================Delete all data=====================================================

ds_instance.delete_all()

