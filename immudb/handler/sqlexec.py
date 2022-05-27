# Copyright 2021 CodeNotary, Inc. All rights reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from immudb.grpc import schema_pb2
from immudb.grpc import schema_pb2_grpc
from immudb.rootService import RootService
from immudb.typeconv import py_to_sqlvalue


def call(service: schema_pb2_grpc.ImmuServiceStub, rs: RootService, stmt, params, noWait):
    return _call_with_executor(stmt, params, noWait, service.SQLExec)


def _call_with_executor(stmt, params, noWait, executor):
    paramsObj = []
    for key, value in params.items():
        paramsObj.append(schema_pb2.NamedParam(
            name=key, value=py_to_sqlvalue(value)))

    request = schema_pb2.SQLExecRequest(
        sql=stmt,
        params=paramsObj,
        noWait=noWait)

    result = executor(request)
    return result
