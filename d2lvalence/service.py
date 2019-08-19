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
import sys       # for exception throwing
import json      # for packing and unpacking dicts into JSON structures
import requests  # for making HTTP requests of the back-end service
import uuid      # for generating unique boundary tags in multi-part POST/PUT requests

import d2lvalence.auth as d2lauth
import d2lvalence.data as d2ldata


# internal utility functions

def _fetch_content(request):
    ct = ''
    if request.headers['content-type']:
        ct = request.headers['content-type']
    if 'application/json' in ct:
        return request.json
    elif 'text/plain' in ct:
        return request.text
    else:
        return request.content

def _delete(route,uc,params=None,data=None,headers=None):
    if uc.anonymous:
        raise ValueError('User context cannot be anonymous.')
    r = requests.delete(uc.scheme + '://' + uc.host + route, params=params, data=data, headers=headers, auth=uc)
    r.raise_for_status()
    return _fetch_content(r)

def _get(route,uc,params=None,data=None,headers=None):
    if uc.anonymous:
        raise ValueError('User context cannot be anonymous.')
    r = requests.get(uc.scheme + '://' + uc.host + route, params=params, data=data, headers=headers, auth=uc)
    r.raise_for_status()
    return _fetch_content(r)

def _post(route,uc,params=None,data=None,headers=None):
    if uc.anonymous:
        raise ValueError('User context cannot be anonymous.')
    r = requests.post(uc.scheme + '://' + uc.host + route, params=params, data=data, headers=headers, auth=uc)
    r.raise_for_status()
    return _fetch_content(r)

def _put(route,uc,params=None,data=None,headers=None):
    if uc.anonymous:
        raise ValueError('User context cannot be anonymous.')
    r = requests.put(uc.scheme + '://' + uc.host + route, params=params, data=data, headers=headers, auth=uc)
    r.raise_for_status()
    return _fetch_content(r)

def _get_anon(route,uc,params=None,data=None,headers=None):
    r = requests.get(uc.scheme + '://' + uc.host + route, params=params, data=data, headers=headers, auth=uc)
    r.raise_for_status()
    return _fetch_content(r)

def _post_anon(route,uc,params=None,data=None,headers=None):
    r = requests.post(uc.scheme + '://' + uc.host + route, params=params, data=data, headers=headers, auth=uc)
    r.raise_for_status()
    return _fetch_content(r)

## API Properties functions
# Versions

def get_versions_for_product_component(uc,pc):
    route = '/d2l/api/{0}/versions/'.format(pc)
    return d2ldata.ProductVersions(_get_anon(route,uc))

def get_version_for_product_component(uc,pc,ver):
    route = '/d2l/api/{0}/versions/{1}'.format(pc,ver)
    return d2ldata.SupportedVersion(_get_anon(route,uc))

def get_all_versions(uc):
    route = '/d2l/api/versions/'
    r = _get_anon(route,uc)
    result = []
    for i in range(len(r)):
        result.append(r[i])
    return result

def check_versions(uc,supported_version_request_array):
    route = '/d2l/api/versions/check'
    return d2ldata.BulkSupportedVersionResponse(_post_anon(route,uc,data=json.dumps(supported_version_request_array)))


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

def get_profile_by_user_id(uc,user_id,ver='1.0'):
    route = '/d2l/api/lp/{0}/profile/user/{1}'.format(ver,user_id)
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

def get_my_final_grade_value_for_org(uc,orgUnitId,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/grades/final/values/myGradeValue'.format(ver,orgUnitId)
    return d2ldata.GradeValueComputable(_get(route,uc))

def get_my_grade_value_for_org(uc,orgUnitId,gradeObjectId,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/grades/{2}/values/myGradeValue'.format(ver,orgUnitId,gradeObjectId)
    r = _get(route,uc)
    result = None
    if 'PointsNumerator' in r:
        result = d2ldata.GradeValueComputable(r)
    else:
        result = d2ldata.GradeValue(r)
    return result

def get_all_my_grade_values_for_org(uc,orgUnitId,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/grades/values/myGradeValues/'.format(ver,orgUnitId)
    r = _get(route,uc)
    result = []
    for i in range(len(r)):
        t = r[i]['GradeObjectTypeName']
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


## Lockers
def _simple_upload(route,uc,f):
    if not isinstance(f, d2ldata.D2LFile):
        raise TypeError('File must implement d2lvalence.data.D2LFile')

    boundary = uuid.uuid4().hex
    f.Stream.seek(0) # check the tape
    fdata = f.Stream.read()
    f.Stream.seek(0) # please be kind, rewind

    pdescr = '--{0}\r\nContent-Type: application/json\r\n\r\n{1}\r\n'.format(boundary,json.dumps(f.DescriptorDict)).encode(encoding='utf-8')
    ptopbound = '--{0}\r\nContent-Disposition: form-data; name=""; filename="{1}"\r\nContent-Type: {2}\r\n\r\n'.format(boundary,f.Name,f.ContentType).encode(encoding='utf-8')
    pbotbound = '\r\n--{0}--'.format(boundary).encode(encoding='utf-8')

    payload = pdescr + ptopbound + fdata + pbotbound

    headers = {'Content-Type':'multipart/mixed;boundary='+boundary,
               'Content-Length': str(len(payload))}

    return _post(route,uc,data=payload,headers=headers)

def _get_locker_item(uc,route):
    result = None
    r = _get(route,uc)
    if '/' in route[-1:]:
        result = []
        for i in range(len(r)):
            result.append(d2ldata.LockerItem(r[i]))
    else:
        result = r
    return result

def _check_path(path):
    if not '/' in path[0]:
        raise ValueError('Path must be rooted with in initial "/".').with_traceback(sys.exc_info()[2])
    else:
        return True

def delete_my_locker_item(uc,path='/',ver='1.0'):
    if _check_path(path):
        route = '/d2l/api/le/{0}/locker/myLocker{1}'.format(ver,path)
        r = _delete(route,uc)

def delete_locker_item(uc,user_id,path='/',ver='1.0'):
    if _check_path(path):
        route = '/d2l/api/le/{0}/locker/user/{1}{2}'.format(ver,user_id,path)
        r = _delete(route,uc)

def get_my_locker_item(uc,path='/',ver='1.0'):
    if _check_path(path):
        route = '/d2l/api/le/{0}/locker/myLocker{1}'.format(ver,path)
        return _get_locker_item(uc,route)

def get_locker_item(uc,user_id,path='/',ver='1.0'):
    if _check_path(path):
        route = '/d2l/api/le/{0}/locker/user/{1}{2}'.format(ver,user_id,path)
        return _get_locker_item(uc,route)

def create_my_locker_folder(uc,folder,path='/',ver='1.0'):
    if _check_path(path):
        route = '/d2l/api/le/{0}/locker/myLocker{1}'.format(ver,path)
        return _post(route,uc,data=json.dumps(folder),headers={'Content-Type':'application/json'})

def create_locker_folder(uc,user_id,folder,path='/',ver='1.0'):
    if _check_path(path):
        route = '/d2l/api/le/{0}/locker/user/{1}{2}'.format(ver,user_id,path)
        return _post(route,uc,data=json.dumps(folder),headers={'Content-Type':'application/json'})

def create_my_locker_file(uc,d2lfile,path='/',ver='1.0'):
    if _check_path(path):
        route = '/d2l/api/le/{0}/locker/myLocker{1}'.format(ver,path)
        return _simple_upload(route,uc,d2lfile)

def create_locker_file(uc,user_id,d2lfile,path='/',ver='1.0'):
    if _check_path(path):
        route = '/d2l/api/le/{0}/locker/user/{1}{2}'.format(ver,user_id,path)
        return _simple_upload(route,uc,d2lfile)

def rename_my_locker_folder(uc,new_folder_name,path='/',ver='1.0'):
    if _check_path(path):
        route = '/d2l/api/le/{0}/locker/myLocker{1}'.format(ver,path)
        return _put(route,uc,data=json.dumps(new_folder_name),headers={'Content-Type':'application/json'})

def rename_locker_folder(uc,user_id,new_folder_name,path='/',ver='1.2'):
    if _check_path(path):
        route = '/d2l/api/le/{0}/locker/user/{1}{2}'.format(ver,user_id,path)
        return _put(route,uc,data=json.dumps(new_folder_name),headers={'Content-Type':'application/json'})

# Lockers and groups
def delete_group_locker_item(uc,orgunit_id,group_id,path='/',ver='1.0'):
    if _check_path(path):
        route = '/d2l/api/le/{0}/{1}/locker/group/{2}{3}'.format(ver,orgunit_id,group_id,path)
        r = _delete(route,uc)

def get_group_locker_category(uc,orgunit_id,groupcat_id,ver='1.0'):
    route = '/d2l/api/lp/{0}/{1}/groupcategories/{2}/locker'.format(ver,orgunit_id,groupcat_id)
    return d2ldata.GroupLocker(_get(route,uc))

def get_group_locker_item(uc,orgunit_id,group_id,path='/',ver='1.0'):
    if _check_path(path):
        route = '/d2l/api/le/{0}/{1}/locker/group/{2}{3}'.format(ver,orgunit_id,group_id,path)
        return _get_locker_item(uc,route)

def setup_group_locker_category(uc,orgunit_id,groupcat_id,ver='1.0'):
    route = '/d2l/api/lp/{0}/{1}/groupcategories/{2}/locker'.format(ver,orgunit_id,groupcat_id)
    return d2ldata.GroupLocker(_post(route,uc))

def create_group_locker_folder(uc,orgunit_id,group_id,folder,path='/',ver='1.0'):
    if _check_path(path):
        route = '/d2l/api/le/{0}/{1}/locker/group/{2}{3}'.format(ver,orgunit_id,group_id,path)
        return _post(route,uc,data=json.dumps(folder),headers={'Content-Type':'application/json'})

def create_group_locker_file(uc,orgunit_id,group_id,d2lfile,path='/',ver='1.0'):
    if _check_path(path):
        route = '/d2l/api/le/{0}/{1}/locker/group/{2}{3}'.format(ver,orgunit_id,group_id,path)
        return _simple_upload(route,uc,d2lfile)

def rename_group_locker_folder(uc,orgunit_id,group_id,new_folder_name,path='/',ver='1.0'):
    if _check_path(path):
        route = '/d2l/api/le/{0}/{1}/locker/group/{2}{3}'.format(ver,user_id,path)
        return _put(route,uc,data=json.dumps(new_folder_name),headers={'Content-Type':'application/json'})
