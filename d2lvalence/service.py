# -*- coding: utf-8 -*-
# D2LValence package, service module.
#
# Copyright (c) 2012 Desire2Learn Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the license at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

"""
:module: d2lvalence.service
:synopsis: Provides a suite of convenience functions for making D2L Valence calls.
"""
import json
import requests

import d2lvalence.auth as d2lauth
import d2lvalence.data as d2ldata


# internal utility functions

def _delete(route,uc,params=None):
    r = requests.delete(uc.scheme + '://' + uc.host + route, params=params, auth=uc)
    r.raise_for_status()
    # catch TypeError because the current version of the requests library throws it here
    # when the body is empty --> r.text returns ''
    try:
        return r.json
    except TypeError:
        return r.text

def _get(route,uc,params=None):
    r = requests.get(uc.scheme + '://' + uc.host + route, params=params, auth=uc)
    r.raise_for_status()
    return r.json

def _post(route,uc,params=None,data=None):
    r = requests.post(uc.scheme + '://' + uc.host + route, data=data, auth=uc)
    r.raise_for_status()
    if r.json:
        return r.json

def _put(route,uc,params=None,data=None):
    r = requests.put(uc.scheme + '://' + uc.host + route, data=data, auth=uc)
    r.raise_for_status()
    if r.json:
        return r.json

## API Properties functions
# Versions

def get_versions_for_product_component(uc,pc):
    route = '/d2l/api/{0}/versions/'.format(pc)
    return d2ldata.ProductVersions(_get(route,uc))

def get_version_for_product_component(uc,pc,ver):
    route = '/d2l/api/{0}/versions/{1}'.format(pc,ver)
    return d2ldata.SupportedVersion(_get(route,uc))

def get_all_versions(uc):
    route = '/d2l/api/versions/'
    r = _get(route,uc)
    result = []
    for i in range(len(r)):
        result.append(r[i]) 
    return result

def check_versions(uc,supported_version_request_array):
    route = '/d2l/api/versions/check'
    return d2ldata.BulkSupportedVersionResponse(_post(route,uc,data=supported_version_request_array))


## User functions
# User data
def delete_user(uc,user_id,ver='1.0'):
    route = '/d2l/api/lp/{0}/users/{1}'.format(ver,user_id)
    return _delete(route,uc)

def get_users(uc,ver='1.0',orgDefinedId=None,userName=None,bookmark=None):
    route = '/d2l/api/lp/{0}/users/'.format(ver)
    result = None
    if not (bookmark or orgDefinedId or userName):
        r = _get(route,uc)
        result = d2ldata.PagedResultSet(r)
    elif bookmark:
        r = _get(route,uc,params={'bookmark':bookmark})
        result = d2ldata.PagedResultSet(r)
    elif orgDefinedId:
        r = _get(route,uc,params={'orgDefinedId':orgDefinedId})
        result = []
        if len(r) < 1:
            pass
        else:
            for i in range(len(r)):
                result.append(d2ldata.UserData(r[i]))
    elif userName:
        r = _get(route,uc,params={'userName':userName})
        result = d2ldata.UserData(r)

    return result

def get_user(uc,user_id,ver='1.0'):
    route = '/d2l/api/lp/{0}/users/{1}'.format(ver,user_id)
    return d2ldata.UserData(_get(route,uc))

def get_whoami(uc,ver='1.0'):
    route = '/d2l/api/lp/{0}/users/whoami'.format(ver)
    return d2ldata.WhoAmIUser(_get(route,uc))

def create_user(uc,create_user_data,ver='1.0'):
    route = '/d2l/api/lp/{0}/users/'.format(ver)
    return d2ldata.UserData(_post(route,uc,data=create_user_data.as_json()))

# Profiles
def get_profile_by_profile_id(uc,profile_id,ver='1.0'):
    route = '/d2l/api/lp/{0}/profile/{1}'.format(ver,profile_id)
    return d2ldata.UserProfile(_get(route,uc))

def get_my_profile(uc,ver='1.0'):
    route = '/d2l/api/lp/{0}/profile/myProfile'.format(ver)
    return d2ldata.UserProfile(_get(route,uc))

def update_my_profile(uc,updated_profile_data,ver='1.0'):
    route = '/d2l/api/lp/{0}/profile/myProfile'.format(ver)
    return d2ldata.UserProfile(_put(route,uc,data=updated_profile_data.as_json()))

# Roles
def get_all_roles(uc,ver='1.0'):
    route = '/d2l/api/lp/{0}/roles/'.format(ver)
    r = _get(route,uc)
    result = []
    if len(r) < 1:
        pass
    else:
        for i in range(len(r)):
            result.append(d2ldata.Role(r[i]))
    return result

def get_role(uc,role_id,ver='1.0'):
    route = '/d2l/api/lp/{0}/roles/{1}'.format(ver,role_id)
    return d2ldata.Role(_get(route,uc))

## Org structure
def get_all_outypes(uc,ver='1.0'):
    route = '/d2l/api/lp/{0}/outypes/'.format(ver)
    r = _get(route,uc)
    result = []
    if len(r) < 1:
        pass
    else:
        for i in range(len(r)):
            result.append(d2ldata.OrgUnitType(r[i]))
    return result

def get_outype(uc,outype_id,ver='1.0'):
    route = '/d2l/api/lp/{0}/outypes/{1}'.format(ver,outype_id)
    return d2ldata.OrgUnitType(_get(route,uc))


## Enrollments
def get_classlist(uc,orgUnitId,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/classlist/'.format(ver,orgUnitId)
    r = _get(route,uc)
    result = []
    for i in range(len(r)):
        result.append(d2ldata.ClasslistUser(r[i]))
    return result

def get_my_enrollments(uc,ver='1.0',orgUnitTypeId=None,bookmark=None):
    route = '/d2l/api/lp/{0}/enrollments/myenrollments/'.format(ver)
    result = None
    if not (bookmark or orgUnitTypeId):
        r = _get(route,uc)
    elif bookmark:
        r = _get(route,uc,params={'bookmark':bookmark})
    elif orgUnitTypeId:
        r = _get(route,uc,params={'orgUnitTypeId':orgUnitTypeId})

    return d2ldata.PagedResultSet(r)

def get_enrolled_users_for_orgunit(uc,orgUnitId,ver='1.0',roleId=None,bookmark=None):
    route = '/d2l/api/lp/{0}/enrollments/orgUnits/{1}/users/'.format(ver,orgUnitId)
    result = None
    if not (bookmark or roleId):
        r = _get(route,uc)
    elif bookmark:
        r = _get(route,uc,params={'bookmark':bookmark})
    elif roleId:
        r = _get(route,uc,params={'roleId':roleId})

    return d2ldata.PagedResultSet(r)



## Grades
def get_all_grade_objects_for_org(uc,orgUnitId,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/grades/'.format(ver,orgUnitId)
    r = _get(route,uc)
    result = []
    for i in range(len(r)):
        t = r[i]['GradeType']
        if t == 'Numeric':
            result.append( d2ldata.GradeObjectNumeric(r[i]))
        elif t == 'PassFail':
            result.append( d2ldata.GradeObjectPassFail(r[i]))
        elif t == 'SelectBox':
            result.append( d2ldata.GradeObjectSelectBox(r[i]))
        elif t == 'Text':
            result.append( d2ldata.GradeObjectText(r[i]))
        else:
            result.append( d2ldata.GradeObject(r[i]))

    return result
                      
def get_grade_object_for_org(uc,orgUnitId,gradeObjectId,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/grades/{2}'.format(ver,orgUnitId,gradeObjectId)
    r = _get(route,uc)
    t = r['GradeType']
    result = None
    if t == 'Numeric':
        result = d2ldata.GradeObjectNumeric(r)
    elif t == 'PassFail':
        result = d2ldata.GradeObjectPassFail(r)
    elif t == 'SelectBox':
        result = d2ldata.GradeObjectSelectBox(r)
    elif t == 'Text':
        result = d2ldata.GradeObjectText(r)
    else:
        result = d2ldata.GradeObject(r)

    return result

def get_final_grade_value_for_user_in_org(uc,orgUnitId,userId,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/grades/final/values/{2}'.format(ver,orgUnitId,userId)
    return d2ldata.GradeValueComputable(_get(route,uc))

def get_grade_value_for_user_in_org(uc,orgUnitId,gradeObjectId,userId,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/grades/{2}/values/{3}'.format(ver,orgUnitId,gradeObjectId,userId)
    r = _get(route,uc)
    result = None
    if 'PointsNumerator' in r:
        result = d2ldata.GradeValueComputable(r)
    else:
        result = d2ldata.GradeValue(r)

    return result

def get_all_grade_values_for_user_in_org(uc,orgUnitId,userId,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/grades/values/{2}/'.format(ver,orgUnitId,userId)
    r = _get(route,uc)
    result = []
    for i in range(len(r)):
        if 'PointsNumerator' in r[i]:
            result.append(d2ldata.GradeValueComputable(r[i]))
        else:
            result.append(d2ldata.GradeValue(r[i]))
    return result


