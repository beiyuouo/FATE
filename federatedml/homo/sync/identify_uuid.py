#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import uuid

from federatedml.homo.utils.scatter import scatter
from federatedml.util.transfer_variable.base_transfer_variable import Variable
from federatedml.util import consts


class _Arbiter(object):
    def __init__(self, guest_uuid_trv, host_uuid_trv, conflict_flag_trv: Variable):
        self._guest_uuid_trv = guest_uuid_trv
        self._host_uuid_trv = host_uuid_trv
        self._conflict_flag_trv = conflict_flag_trv

    def validate_uuid(self):
        ind = 0
        while True:
            uuid_set = set()
            for uid in scatter(self._host_uuid_trv, self._guest_uuid_trv, suffix=ind):
                if uid in uuid_set:
                    self._conflict_flag_trv.remote(obj=False, role=None, idx=-1, suffix=ind)
                    ind += 1
                    break
                uuid_set.add(uid)
            else:
                break


class _Guest(object):
    def __init__(self, guest_uuid_trv: Variable, conflict_flag_trv: Variable):
        self._guest_uuid_trv = guest_uuid_trv
        self._conflict_flag_trv = conflict_flag_trv

    def generate_uuid(self):
        ind = -1
        while True:
            ind = ind + 1
            _uid = uuid.uuid1()
            self._guest_uuid_trv.remote(obj=_uid, role=consts.ARBITER, idx=0, suffix=ind)
            if self._conflict_flag_trv.get(idx=0, suffix=ind):
                break
        return _uid


class _Host(object):
    def __init__(self, host_uuid_trv: Variable, conflict_flag_trv: Variable):
        self._host_uuid_trv = host_uuid_trv
        self._conflict_flag_trv = conflict_flag_trv

    def generate_uuid(self):
        ind = -1
        while True:
            ind = ind + 1
            _uid = uuid.uuid1()
            self._host_uuid_trv.remote(obj=_uid, role=consts.ARBITER, idx=0, suffix=ind)
            if self._conflict_flag_trv.get(idx=0, suffix=ind):
                break
        return _uid


def arbiter(guest_uuid_trv, host_uuid_trv, conflict_flag_trv) -> _Arbiter:
    return _Arbiter(host_uuid_trv, guest_uuid_trv, conflict_flag_trv)


def guest(guest_uuid_trv, conflict_flag_trv) -> _Guest:
    return _Guest(guest_uuid_trv, conflict_flag_trv)


def host(host_uuid_trv, conflict_flag_trv) -> _Host:
    return _Host(host_uuid_trv, conflict_flag_trv)
