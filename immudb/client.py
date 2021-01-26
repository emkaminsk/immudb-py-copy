import grpc
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2

from immudb import header_manipulator_client_interceptor
from immudb.handler import (batchGet, batchSet, changePassword, createUser,
                          currentRoot, databaseCreate, databaseList, databaseUse, 
                          get, listUsers, safeGet, safeSet, setValue, history, 
                          scan, reference)
from immudb.rootService import RootService
from immudb.grpc import schema_pb2_grpc


class ImmudbClient:
    def __init__(self, immudUrl=None):
        if immudUrl is None:
            immudUrl = "localhost:3322"
        self.channel = grpc.insecure_channel(immudUrl)
        self.__stub = schema_pb2_grpc.ImmuServiceStub(self.channel)
        self.__rs = None

    def login(self, username, password, database=b"defaultdb"):
        req = schema_pb2_grpc.schema__pb2.LoginRequest(user=bytes(
            username, encoding='utf-8'), password=bytes(
                password, encoding='utf-8'
                ))
        try:
            self.__login_response = schema_pb2_grpc.schema__pb2.LoginResponse = \
                self.__stub.Login(
                    req
                )
        except ValueError as e:
            raise Exception("Attempted to login on termninated client, channel has been shutdown") from e
            
        self.__stub = self.set_token_header_interceptor(self.__login_response)
        # Select database, modifying stub function accordingly
        request = schema_pb2_grpc.schema__pb2.Database(databasename=database)
        resp = self.__stub.UseDatabase(request)
        self.__stub = self.set_token_header_interceptor(resp)

        self.init()
        return self.__login_response

    def init(self):
        rs = RootService(self.__stub)
        rs.init()
        self.__rs = rs

    def shutdown(self):
        self.channel.close()
        self.channel = None
        self.intercept_channel.close
        self.intercept_channel = None

    def set_token_header_interceptor(self, response):
        try:
            token = response.token
        except AttributeError:
            token = response.reply.token
        self.header_interceptor = \
            header_manipulator_client_interceptor.header_adder_interceptor(
                'authorization', "Bearer "+token
            )
        try:
            self.intercept_channel = grpc.intercept_channel(
                self.channel, self.header_interceptor)
        except ValueError as e:
            raise Exception("Attempted to login on termninated client, channel has been shutdown") from e
        return schema_pb2_grpc.ImmuServiceStub(self.intercept_channel)

    @property
    def stub(self):
        return self.__stub

    def get(self, key: bytes):
        return get.call(self.__stub, self.__rs, key)
    
    def getValue(self, key: bytes):
        ret=get.call(self.__stub, self.__rs, key)
        if ret==None:
            return None
        return ret.value

    def set(self, key: bytes, value: bytes):
        return setValue.call(self.__stub, self.__rs, key, value)

    def safeGet(self, key: bytes):
        return safeGet.call(self.__stub, self.__rs, key)

    def safeSet(self, key: bytes, value: bytes):
        return safeSet.call(self.__stub, self.__rs, key, value)

    def getAllValues(self, keys: list):
        resp = batchGet.call(self.__stub, self.__rs, keys)
        return resp

    def getAll(self, keys: list):
        resp = batchGet.call(self.__stub, self.__rs, keys)
        return {key:value.value for key, value in resp.items()}

    def setAll(self, kv: dict):
        return batchSet.call(self.__stub, self.__rs, kv)

    def changePassword(self, user, newPassword, oldPassword):
        request = schema_pb2_grpc.schema__pb2.ChangePasswordRequest(
                    user=bytes(user, encoding='utf-8'),                     
                    newPassword=bytes(newPassword, encoding='utf-8'),
                    oldPassword=bytes(oldPassword, encoding='utf-8')
                    )
        return changePassword.call(self.__stub, self.__rs, request)
    
    def createUser(self, user, password, permission, database):
        request = schema_pb2_grpc.schema__pb2.CreateUserRequest(
                    user=bytes(user, encoding='utf-8'),
                    password=bytes(password, encoding='utf-8'),
                    permission=permission,
                    database=database
                    )
        return createUser.call(self.__stub, self.__rs, request)
    
    def listUsers(self):
        return listUsers.call(self.__stub, None)
    
    def databaseList(self):
        dbs=databaseList.call(self.__stub, self.__rs, None)
        return [x.databasename for x in dbs.dblist.databases]

    def databaseUse(self, dbName: bytes):
        request = schema_pb2_grpc.schema__pb2.Database(databasename=dbName)
        resp = databaseUse.call(self.__stub, self.__rs, request)
        # modify header token accordingly
        self.__stub = self.set_token_header_interceptor(resp)
        self.__rs = RootService(self.__stub)
        self.__rs.init()
        return resp

    def databaseCreate(self, dbName: bytes):
        request = schema_pb2_grpc.schema__pb2.Database(databasename=dbName)
        return databaseCreate.call(self.__stub, self.__rs, request)

    def currentRoot(self):
        return currentRoot.call(self.__stub, self.__rs, None)

    def history(self, key: bytes, offset: int, limit: int, sortorder: bool):
        return history.call(self.__stub, self.__rs, key, offset, limit, sortorder)

    def logout(self):
        self.__stub.Logout(google_dot_protobuf_dot_empty__pb2.Empty())
        self.__login_response = None
        
    def scan(self, key:bytes, prefix:bytes, desc:bool, limit:int,sinceTx:int=None):
        return scan.call(self.__stub, self.__rs, key, prefix, desc, limit, sinceTx)
    
    def reference(self, referredkey: bytes, newkey:  bytes):
        return reference.call(self.__stub, self.__rs, referredkey, newkey)
    
    def zadd(self):
        pass
    
    def zscan(self):
        pass
