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

def _post(route,uc,params=None,data=None,headers=None,files=None):
    if uc.anonymous:
        raise ValueError('User context cannot be anonymous.')
    r = requests.post(uc.scheme + '://' + uc.host + route, params=params, data=data, headers=headers, files=files, auth=uc)
    r.raise_for_status()
    return _fetch_content(r)

def _put(route,uc,params=None,data=None,headers=None,files=None):
    if uc.anonymous:
        raise ValueError('User context cannot be anonymous.')
    r = requests.put(uc.scheme + '://' + uc.host + route, params=params, data=data, headers=headers, files=files, auth=uc)
    r.raise_for_status()
    return _fetch_content(r)

def _get_anon(route,uc,params=None,data=None,headers=None):
    r = requests.get(uc.scheme + '://' + uc.host + route, params=params, data=data, headers=headers, auth=uc)
    r.raise_for_status()
    return _fetch_content(r)

def _post_anon(route,uc,params=None,data=None,headers=None,files=None):
    r = requests.post(uc.scheme + '://' + uc.host + route, params=params, data=data, headers=headers, files=files, auth=uc)
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

def get_users(uc,org_defined_id=None,user_name=None,bookmark=None,ver='1.0'):
    route = '/d2l/api/lp/{0}/users/'.format(ver)
    result = None
    if not (bookmark or org_defined_id or user_name):
        r = _get(route,uc)
        result = d2ldata.PagedResultSet(r)
    elif bookmark:
        r = _get(route,uc,params={'bookmark':bookmark})
        result = d2ldata.PagedResultSet(r)
    elif org_defined_id:
        r = _get(route,uc,params={'orgDefinedId':org_defined_id})
        result = []
        if len(r) < 1:
            pass
        else:
            for i in range(len(r)):
                result.append(d2ldata.UserData(r[i]))
    elif user_name:
        r = _get(route,uc,params={'userName':user_name})
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
def get_classlist(uc,org_unit_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/classlist/'.format(ver,org_unit_id)
    r = _get(route,uc)
    result = []
    for i in range(len(r)):
        result.append(d2ldata.ClasslistUser(r[i]))
    return result

def get_my_enrollments(uc,org_unit_type_id=None,bookmark=None,ver='1.0'):
    route = '/d2l/api/lp/{0}/enrollments/myenrollments/'.format(ver)
    result = None
    if not (bookmark or org_unit_type_id):
        r = _get(route,uc)
    elif bookmark:
        r = _get(route,uc,params={'bookmark':bookmark})
    elif org_unit_type_id:
        r = _get(route,uc,params={'orgUnitTypeId':org_unit_type_id})

    return d2ldata.PagedResultSet(r)

def get_enrolled_users_for_orgunit(uc,org_unit_id,role_id=None,bookmark=None,ver='1.0'):
    route = '/d2l/api/lp/{0}/enrollments/orgUnits/{1}/users/'.format(ver,org_unit_id)
    result = None
    if not (bookmark or role_id):
        r = _get(route,uc)
    elif bookmark:
        r = _get(route,uc,params={'bookmark':bookmark})
    elif role_id:
        r = _get(route,uc,params={'roleId':role_id})

    return d2ldata.PagedResultSet(r)


## Course offerings
def delete_course_offering(uc,org_unit_id,ver='1.0'):
    route = '/d2l/api/lp/{0}/courses/{1}'.format(ver,org_unit_id)
    return _delete(route,uc)

def get_course_schemas(uc,ver='1.0'):
    route = '/d2l/api/lp/{0}/courses/schema'.format(ver)
    r = _get(route,uc)
    result = []
    for i in range(len(r)):
        result.append( d2ldata.CourseSchemaElement(r[i]))
    return result

def get_course_offering(uc,org_unit_id,ver='1.0'):
    route = '/d2l/api/lp/{0}/courses/{1}'.format(ver,org_unit_id)
    return d2ldata.CourseOffering(_get(route,uc))

def create_course_offering(uc,new_course_offering,ver='1.0'):
    if not isinstance(new_course_offering, d2ldata.CreateCourseOffering):
        raise TypeError('New course offering must implement d2lvalence.data.CreateCoursOffering')
    route = '/d2l/api/lp/{0}/courses/'.format(ver)
    r = _post(route,uc,data=new_course_offering.as_json())
    return d2ldata.CourseOffering(r)

def update_course_offering(uc,org_unit_id,course_offering_update,ver='1.0'):
    if not isinstance(course_offering_update, d2ldata.CourseOfferingInfo):
        raise TypeError('Course offering update must implement d2lvalence.data.CourseOfferingInfo')
    route = '/d2l/api/lp/{0}/courses/{1}'.format(ver,org_unit_id)
    r = _put(route,uc,data=course_offering_update.as_json())
    return d2ldata.CourseOffering(r)

# Course templates
def delete_course_template(uc,org_unit_id,ver='1.0'):
    route = '/d2l/api/lp/{0}/coursetemplates/{1}'.format(ver,org_unit_id)
    return _delete(route,uc)

def get_course_template(uc,org_unit_id,ver='1.0'):
    route = '/d2l/api/lp/{0}/coursetemplates/{1}'.format(ver,org_unit_id)
    return d2ldata.CourseTemplate(_get(route,uc))

def get_course_templates_schema(uc,ver='1.0'):
    route = '/d2l/api/lp/{0}/coursetemplates/schema'.format(ver)
    r = _get(route,uc)
    result = []
    for i in range(len(r)):
        result.append( d2ldata.CourseSchemaElement(r[i]))
    return result

def create_course_template(uc,new_course_template,ver='1.0'):
    if not isinstance(new_course_template,d2ldata.CreateCourseTemplate):
        raise TypeError('New course template must implement d2lvalence.data.CreateCourseTemplate')
    route = '/d2l/api/lp/{0}/coursetemplates/'.format(ver)
    r = _post(route,uc,data=new_course_template.as_json(),headers={'Content-Type':'application/json'})
    return d2ldata.CourseTemplate(r)

def update_course_template(uc,org_unit_id,course_template_update,ver='1.0'):
    if not isinstance(course_template_update, d2ldata.CourseTemplateInfo):
        raise TypeError('Course template update must implement d2lvalence.data.CourseTemplateInfo')
    route = '/d2l/api/lp/{0}/coursetemplates/{1}'.format(ver,org_unit_id)
    return _put(route,uc,data=course_template_update.as_json(),headers={'Content-Type':'application/json'})

## Grades
def get_all_grade_objects_for_org(uc,org_unit_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/grades/'.format(ver,org_unit_id)
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

def get_grade_object_for_org(uc,org_unit_id,grade_object_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/grades/{2}'.format(ver,org_unit_id,grade_object_id)
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

def get_final_grade_value_for_user_in_org(uc,org_unit_id,user_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/grades/final/values/{2}'.format(ver,org_unit_id,user_id)
    return d2ldata.GradeValueComputable(_get(route,uc))

def get_grade_value_for_user_in_org(uc,org_unit_id,grade_object_id,user_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/grades/{2}/values/{3}'.format(ver,org_unit_id,grade_object_id,user_id)
    r = _get(route,uc)
    result = None
    if 'PointsNumerator' in r:
        result = d2ldata.GradeValueComputable(r)
    else:
        result = d2ldata.GradeValue(r)
    return result

def get_all_grade_values_for_user_in_org(uc,org_unit_id,user_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/grades/values/{2}/'.format(ver,org_unit_id,user_id)
    r = _get(route,uc)
    result = []
    for i in range(len(r)):
        if 'PointsNumerator' in r[i]:
            result.append(d2ldata.GradeValueComputable(r[i]))
        else:
            result.append(d2ldata.GradeValue(r[i]))
    return result

def get_my_final_grade_value_for_org(uc,org_unit_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/grades/final/values/myGradeValue'.format(ver,org_unit_id)
    return d2ldata.GradeValueComputable(_get(route,uc))

def get_my_grade_value_for_org(uc,org_unit_id,grade_object_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/grades/{2}/values/myGradeValue'.format(ver,org_unit_id,grade_object_id)
    r = _get(route,uc)
    result = None
    if 'PointsNumerator' in r:
        result = d2ldata.GradeValueComputable(r)
    else:
        result = d2ldata.GradeValue(r)
    return result

def get_all_my_grade_values_for_org(uc,org_unit_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/grades/values/myGradeValues/'.format(ver,org_unit_id)
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

def create_my_locker_file(uc,d2l_file,path='/',ver='1.0'):
    if _check_path(path):
        route = '/d2l/api/le/{0}/locker/myLocker{1}'.format(ver,path)
        return _simple_upload(route,uc,d2l_file)

def create_locker_file(uc,user_id,d2l_file,path='/',ver='1.0'):
    if _check_path(path):
        route = '/d2l/api/le/{0}/locker/user/{1}{2}'.format(ver,user_id,path)
        return _simple_upload(route,uc,d2l_file)

def rename_my_locker_folder(uc,new_folder_name,path='/',ver='1.0'):
    if _check_path(path):
        route = '/d2l/api/le/{0}/locker/myLocker{1}'.format(ver,path)
        return _put(route,uc,data=json.dumps(new_folder_name),headers={'Content-Type':'application/json'})

def rename_locker_folder(uc,user_id,new_folder_name,path='/',ver='1.2'):
    if _check_path(path):
        route = '/d2l/api/le/{0}/locker/user/{1}{2}'.format(ver,user_id,path)
        return _put(route,uc,data=json.dumps(new_folder_name),headers={'Content-Type':'application/json'})

# Lockers and groups
def delete_group_locker_item(uc,org_unit_id,group_id,path='/',ver='1.0'):
    if _check_path(path):
        route = '/d2l/api/le/{0}/{1}/locker/group/{2}{3}'.format(ver,org_unit_id,group_id,path)
        r = _delete(route,uc)

def get_group_locker_category(uc,org_unit_id,group_cat_id,ver='1.0'):
    route = '/d2l/api/lp/{0}/{1}/groupcategories/{2}/locker'.format(ver,org_unit_id,group_cat_id)
    return d2ldata.GroupLocker(_get(route,uc))

def get_group_locker_item(uc,org_unit_id,group_id,path='/',ver='1.0'):
    if _check_path(path):
        route = '/d2l/api/le/{0}/{1}/locker/group/{2}{3}'.format(ver,org_unit_id,group_id,path)
        return _get_locker_item(uc,route)

def setup_group_locker_category(uc,org_unit_id,group_cat_id,ver='1.0'):
    route = '/d2l/api/lp/{0}/{1}/groupcategories/{2}/locker'.format(ver,org_unit_id,group_cat_id)
    return d2ldata.GroupLocker(_post(route,uc))

def create_group_locker_folder(uc,org_unit_id,group_id,folder,path='/',ver='1.0'):
    if _check_path(path):
        route = '/d2l/api/le/{0}/{1}/locker/group/{2}{3}'.format(ver,org_unit_id,group_id,path)
        return _post(route,uc,data=json.dumps(folder),headers={'Content-Type':'application/json'})

def create_group_locker_file(uc,org_unit_id,group_id,d2l_file,path='/',ver='1.0'):
    if _check_path(path):
        route = '/d2l/api/le/{0}/{1}/locker/group/{2}{3}'.format(ver,org_unit_id,group_id,path)
        return _simple_upload(route,uc,d2l_file)

def rename_group_locker_folder(uc,org_unit_id,group_id,new_folder_name,path='/',ver='1.0'):
    if _check_path(path):
        route = '/d2l/api/le/{0}/{1}/locker/group/{2}{3}'.format(ver,org_unit_id,group_id,path)
        return _put(route,uc,data=json.dumps(new_folder_name),headers={'Content-Type':'application/json'})

## Discussion forum routes
def delete_discussion_forum(uc,org_unit_id,forum_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}'.format(ver,org_unit_id,forum_id)
    return _delete(route,uc)

def get_discussion_forums(uc,org_unit_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/'.format(ver,org_unit_id)
    r = _get(route,uc)
    result = []
    for i in range(len(r)):
        result.append(d2ldata.Forum(r[i]))
    return result

def get_discussion_forum(uc,org_unit_id,forum_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}'.format(ver,org_unit_id,forum_id)
    return d2ldata.Forum(_get(route,uc))

def create_discussion_forum(uc,org_unit_id,new_forum_data,ver='1.0'):
    if not isinstance(new_forum_data, d2ldata.ForumData):
        raise TypeError('New forum data must implement d2lvalence.data.ForumData')
    route = '/d2l/api/le/{0}/{1}/discussions/forums/'.format(ver,org_unit_id)
    r = _post(route,uc,data=new_forum_data.as_json(),headers={'Content-Type':'application/json'})
    return d2ldata.Forum(r)

def update_discussion_forum(uc,org_unit_id,forum_id,updated_forum_data,ver='1.0'):
    if not isinstance(updated_forum_data, d2ldata.ForumUpdateData):
        raise TypeError('Updated forum data must implement d2lvalence.data.ForumUpdateData')
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}'.format(ver,org_unit_id,forum_id)
    r = _put(route,uc,data=updated_forum_data.as_json(),headers={'Content-Type':'application/json'})
    return d2ldata.Forum(r)

# Discussion topics
def delete_discussion_topic(uc,org_unit_id,forum_id,topic_id,ver='1.0'):
    route = '/d2l/api/{0}/{1}/discussions/forums/{2}/topics/{3}'.format(ver,org_unit_id,forum_id,topic_id)
    return _delete(route,uc)

def delete_discussion_topic_group_restriction(uc,org_unit_id,forum_id,topic_id,group_restriction,ver='1.0'):
    if not isinstance(group_restriction, d2ldata.GroupRestriction):
        raise TypeError('Group restriction must implement d2lvalence.data.GroupRestriction')
    route = '/d2l/api/{0}/{1}/discussions/forums/{2}/topics/{3}/groupRestrictions/'.format(ver,org_unit_id,forum_id,topic_id)
    return _delete(route,uc,data=group_restriction.as_json(),headers={'Content-Type':'application/json'})

def get_discussion_topics(uc,org_unit_id,forum_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/'.format(ver,org_unit_id,forum_id)
    r = _get(route,uc)
    result = []
    for i in range(len(r)):
        result.append(d2ldata.Topic(r[i]))
    return result

def get_discussion_topic(uc,org_unit_id,forum_id,topic_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}'.format(ver,org_unit_id,forum_id,topic_id,ver='1.0')
    return d2ldata.Topic(_get(route,uc))

def get_discussion_topics_group_restrictions(uc,org_unit_id,forum_id,topic_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/groupRestrictions/'.format(ver,org_unit_id,forum_id,topic_id)
    r = _get(route,uc)
    result = []
    for i in range(len(r)):
        result.append(d2ldata.GroupRestriction(r[i]))
    return result

def create_discussion_topic(uc,org_unit_id,forum_id,new_topic_data,ver='1.0'):
    if not isinstance(new_topic_data,d2ldata.CreateTopicData):
        raise TypeError('New topic data must implement d2lvalence.data.CreateTopicData')
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/'.format(ver,org_unit_id,forum_id)
    r = _post(route,uc,data=new_topic_data.as_json(),headers={'Content-Type':'application/json'})
    return d2ldata.Topic(r)

def update_discussion_topic(uc,org_unit_id,forum_id,topic_id,new_topic_data,ver='1.0'):
    if not isinstance(new_topic_data,d2ldata.CreateTopicData):
        raise TypeError('Updated topic data must implement d2lvalence.data.CreateTopicData')
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}'.format(ver,org_unit_id,forum_id,topic_id)
    r = _put(route,uc,data=new_topic_data.as_json(),headers={'Content-Type':'application/json'})
    return d2ldata.Topic(r)

def update_group_restrictions_list(uc,org_unit_id,forum_id,topic_id,group_restriction,ver='1.0'):
    if not isinstance(group_restriction,d2ldata.GroupRestriction):
        raise TypeError('Group restriction must implement d2lvalence.data.GroupRestriction')
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/groupRestrictions/'.format(ver,org_unit_id,forum_id,topic_id)
    return _put(route,uc,data=group_restriction.as_json(),headers={'Content-Type':'application/json'})

# Discussion posts
def delete_discussion_post(uc,org_unit_id,forum_id,topic_id,post_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    return _delete(route,uc)

def delete_my_rating_for_discussion_post(uc,org_unit_id,forum_id,topic_id,post_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}/Rating/MyRating'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    return _delete(route,uc)

def get_discussion_posts(uc,org_unit_id,forum_id,topic_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/'.format(ver,org_unit_id,forum_id,topic_id)
    r = _get(route,uc)
    result = []
    for i in range(len(r)):
        result.append(d2ldata.Post(r[1]))
    return result

def get_discussion_post(uc,org_unit_id,forum_id,topic_id,post_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    return d2ldata.Post(_get(route,uc))

def get_discussion_post_approval_status(uc,org_unit_id,forum_id,topic_id,post_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}/Approval'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    return d2ldata.ApprovalData(_get(route,uc))

def get_discussion_post_flag_status(uc,org_unit_id,forum_id,topic_id,post_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}/Flag'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    return d2ldata.FlagData(_get(route,uc))

def get_discussion_post_rating(uc,org_unit_id,forum_id,topic_id,post_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}/Rating'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    return d2ldata.RatingData(_get(route,uc))

def get_discussion_my_post_rating(uc,org_unit_id,forum_id,topic_id,post_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}/Rating/MyRating'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    return d2ldata.UserRatingData(_get(route,uc))

def get_discussion_post_read_status(uc,org_unit_id,forum_id,topic_id,post_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}/ReadStatus'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    return d2ldata.ReadStatusData(_get(route,uc))

def create_discussion_post(uc,org_unit_id,forum_id,topic_id,new_post,ver='1.0'):
    if not isinstance(new_post, d2ldata.CreatePostData):
        raise TypeError('New post must implement d2lvalence.data.CreatePostData')
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/'.format(ver,org_unit_id,forum_id,topic_id)
    r = _post(route,uc,data=new_post.as_json(),headers={'Content-Type':'application/json'})
    return d2ldata.Post(r)

def update_discussion_post(uc,org_unit_id,forum_id,topic_id,post_id,updated_post,ver='1.0'):
    if not isinstance(updated_post, d2ldata.UpdatePostData):
        raise TypeError('Updated post most implement d2lvalence.data.UpdatePostData')
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    r = _put(route,uc,data=updated_post.as_json(),headers={'Content-Type':'application/json'})
    return d2ldata.Post(r)

def set_discussion_post_approval_status(uc,org_unit_id,forum_id,topic_id,post_id,approval_status,ver='1.0'):
    if not isinstance(approval_status, d2ldata.ApprovalData):
        raise TypeError('Approval status must implement d2lvalence.data.ApprovalData')
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}/Approval'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    r = _put(route,uc,data=approval_status.as_json(),headers={'Content-Type':'application/json'})
    return d2ldata.ApprovalData(r)

def set_discussion_post_flag_status(uc,org_unit_id,forum_id,topic_id,post_id,flag_status,ver='1.0'):
    if not isinstance(flag_status, d2ldata.FlagData):
        raise TypeError('Approval status must implement d2lvalence.data.FlagData')
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}/Flag'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    r = _put(route,uc,data=flag_status.as_json(),headers={'Content-Type':'application/json'})
    return d2ldata.FlagData(r)

def set_discussion_post_my_rating(uc,org_unit_id,forum_id,topic_id,post_id,my_rating,ver='1.0'):
    if not isinstance(my_rating, d2ldata.UserRatingData):
        raise TypeError('My rating must implement d2lvalence.data.UserRatingData')
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}/Rating/MyRating'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    r = _put(route,uc,data=my_rating.as_json(),headers={'Content-Type':'application/json'})
    return d2ldata.UserRatingData(r)

def set_discussion_post_read_status(uc,org_unit_id,forum_id,topic_id,post_id,read_status,ver='1.0'):
    if not isinstance(read_status,d2ldata.ReadStatusData):
        raise TypeError('Read status must implement d2lvalence.data.ReadStatusData')
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}/ReadStatus'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    r = _put(route,uc,data=read_status.as_json(),headers={'Content-Type':'application/json'})
    return d2ldata.ReadStatusData(r)


## Conntent routes
def delete_content_module(uc,org_unit_id,module_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/content/modules/{2}'.format(ver,org_unit_id,module_id)
    return _delete(route,uc)

def delete_content_topic(uc,org_unit_id,topic_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/content/topics/{2}'.format(ver,org_unit_id,topic_id)
    return _delete(route,uc)

def get_content_module(uc,org_unit_id,module_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/content/modules/{2}'.format(ver,org_unit_id,module_id)
    return d2ldata.ContentObjectModule(_get(route,uc))

def get_content_module_structure(uc,org_unit_id,module_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/content/modules/{2}/structure/'.format(ver,org_unit_id,module_id)
    r = _get(route,uc)
    result = []
    for i in range(len(r)):
        if 'Type' in r[i]:
            if r[i]['Type'] == 0:
                result.append(d2ldata.ContentObjectModule(r[i]))
            elif r[i]['Type'] == 1:
                result.append(d2ldata.ContentObjectTopic(r[i]))
            else:
                result.append(r[i])
        else:
            result.append(r[i])
    return result

def get_content_root_modules(uc,org_unit_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/content/root/'.format(ver,org_unit_id)
    r = _get(route,uc)
    result = []
    for i in range(len(r)):
        result.append(d2ldata.ContentObjectModule(r[i]))
    return result

def get_content_topic(uc,org_unit_id,topic_id,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/content/topics/{2}'.format(ver,org_unit_id,topic_id)
    return d2ldata.ContentObjectTopic(_get(route,uc))

def create_content_new_module(uc,org_unit_id,module_id,new_module_data,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/content/modules/{2}/structure/'.format(ver,org_unit_id,module_id)
    return _post(route,uc,data=new_module_data.as_json(),headers={'Content-Type':'application/json'})

def create_content_new_topic_link(uc,org_unit_id,module_id,new_topic_data,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/content/modules/{2}/structure/'.format(ver,org_unit_id,module_id)
    return _post(route,uc,data=new_topic_data.as_json(),headers={'Content-Type':'application/json'})

def create_content_new_topic_file(uc,org_unit_id,module_id,d2l_file,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/content/modules/{2}/structure/'.format(ver,org_unit_id,module_id)
    return _simple_upload(route,uc,d2l_file)

def create_content_root_module(uc,org_unit_id,root_module_data,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/content/root/'.format(ver,org_unit_id)
    return _post(route,uc,data=root_module_data.as_json(),headers={'Content-Type':'application/json'})

def update_content_module(uc,org_unit_id,module_id,updated_module_data,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/content/modules/{2}'.format(ver,org_unit_id,module_id)
    return _put(route,uc,data=updated_module_data.as_json(),headers={'Content-Type':'application/json'})

def update_content_topic(uc,org_unit_id,topic_id,updated_topic_data,ver='1.0'):
    route = '/d2l/api/le/{0}/{1}/content/topics/{2}'.format(ver,org_unit_id,topic_id)
    return _put(route,uc,data=updated_topic_data.as_json(),headers={'Content-Type':'application/json'})

# Learning Repository routes
def get_learning_objects_by_search(uc,cql_string,offset,count,repo_list,ver='1.0'):
    route = '/d2l/api/lr/{0}/objects/search/'.format(ver)
    p = {'query': cql_string,
         'offset': offset,
         'count': count,
         'repositories': repo_list}
    r = _get(route,uc,params=p)
    result = None
    if ('ExecutionStatus' in r):
        result = d2ldata.LRWSSearchResultCollection(r)
        if (r['ExecutionStatus'] == 0) and ('Results' in r):
            t = []
            for i in range(len(r['Results'])):
                           t.append(d2ldata.LRWSSearchResult(r['Results'][i]))
            result.props['Results']=t

    return result

def get_learning_object(uc,object_id,ver='1.0'):
    route = '/d2l/api/lr/{0}/objects/{1}/download/'.format(ver,object_id)
    return _get(route,uc)

def get_learning_object_link(uc,object_id,ver='1.0'):
    route = '/d2l/api/lr/{0}/objects/{1}/link/'.format(ver,object_id)
    return d2ldata.LRWSObjectLink(_get(route,uc))

def get_learning_object_properties(uc,object_id,ver='1.0'):
    route = '/d2l/api/lr/{0}/objects/{1}/properties/'.format(ver,object_id)
    return d2ldata.LRWSObjectProperties(_get(route,uc))

def get_learning_object_version(uc,object_id,object_ver,ver='1.0'):
    route = '/d2l/api/lr/{0}/objects/{1}/{2}/download/'.format(ver,object_id,object_ver)
    return _get(route,uc)

def get_learning_object_link_version(uc,object_id,object_ver,ver='1.0'):
    route = '/d2l/api/lr/{0}/objects/{1}/{2}/link/'.format(ver,object_id,object_ver)
    return d2ldata.LRWSObjectLink(_get(route,uc))

def get_learning_object_metadata_version(uc,object_id,object_ver,ver='1.0'):
    route = '/d2l/api/lr/{0}/objects/{1}/{2}/metadata/'.format(ver,object_id,object_ver)
    return _get(route,uc)

def get_learning_object_properties_version(uc,object_id,object_ver,ver='1.0'):
    route = '/d2l/api/lr/{0}/objects/{1}/{2}/properties/'.format(ver,object_id)
    return d2ldata.LRWSObjectProperties(_get(route,uc))

def delete_learning_object(uc,object_id,ver='1.0'):
    route = '/d2l/api/lr/{0}/objects/{1}/delete/'.format(ver,object_id)
    return _post(route,uc,headers={'Content-Length':'0'})

def update_learning_object(uc,object_id,d2l_file,ver='1.0'):
    if not isinstance(d2l_file, d2ldata.D2LFile):
        raise TypeError('File must implement d2lvalence.data.D2LFile')
    route = '/d2l/api/lr/{0}/objects/{1}/'.format(ver,object_id)
    r = _post(route,uc,files={'Resource': (d2l_file.Name, d2l_file.Stream)})
    return d2ldata.LRWSPublishResult(r)

def update_learning_object_properties(uc,object_id,new_props,ver='1.0'):
    if not isinstance(new_props, d2ldata.LRWSObjectPropertiesInput):
        raise TypeError('New properties must implement d2lvalence.data.LRWSObjectPropertiesInput')
    route = '/d2l/api/lr/{0}/objects/{1}/properties/'.format(ver,object_id)
    return _post(route,uc,data=new_props.as_json())

def update_learning_object_properties_version(uc,object_id,object_ver,new_props,ver='1.0'):
    if not isinstance(new_props, d2ldata.LRWSObjectPropertiesInput):
        raise TypeError('New properties must implement d2lvalence.data.LRWSObjectPropertiesInput')
    route = '/d2l/api/lr/{0}/objects/{1}/{2}/properties/'.format(ver,object_id,object_ver)
    return _post(route,uc,data=new_props.as_json())

def create_new_learning_object(uc,repo_id,d2l_file,ver='1.0'):
    if not isinstance(d2l_file, d2ldata.D2LFile):
        raise TypeError('File must implement d2lvalence.data.D2LFile')
    route = '/d2l/api/lr/{0}/objects/'.format(ver)
    f = {'Resource': (d2l_file.Name, d2l_file.Stream)}
    p = {'repositoryId': repo_id}
    r = _put(route,uc,params=p,files=f)
    return d2ldata.LRWSPublishResult(r)
