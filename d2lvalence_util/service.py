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
:module: d2lvalence_util.service
:synopsis: Provides a suite of convenience functions for making D2L Valence calls.
"""
import sys          # for exception throwing
import json         # for packing and unpacking dicts into JSON structures
import requests     # for making HTTP requests of the back-end service
import uuid         # for generating unique boundary tags in multi-part POST/PUT requests

import d2lvalence.auth as d2lauth
import d2lvalence_util.data as d2ldata

# internal utility functions
def _str_to_num(s):
    """Convert a string token to a number: either int or float."""
    try:
        r = int(s)
    except ValueError:
        #try float
        r = float(s)
    return r

def _fetch_content(r,debug=None):
    if debug and not isinstance(debug, d2ldata.D2LDebugInfo):
        raise TypeError('If not None, debug info object must implement d2lvalence.data.D2LDebugInfo')
    elif debug:
        # DebugInfo object passed down: add the response object to it
        debug.add_response(r)
    r.raise_for_status()
    ct = ''
    if 'content-type' in r.headers:
        ct = r.headers['content-type']
    if 'application/json' in ct:
        if requests.__version__[0] is '0':
            return r.json
        else:
            return r.json()
    elif 'text/plain' in ct:
        return r.text
    else:
        return r.content

def _delete(route,uc,**kwargs):
    if uc.anonymous:
        raise ValueError('User context cannot be anonymous.').with_traceback(sys.exc_info()[2])
    kwargs.setdefault('params', None)
    kwargs.setdefault('data', None)
    kwargs.setdefault('headers', None)
    kwargs.setdefault('auth', uc)
    d = None
    if 'd2ldebug' in kwargs:
        d = kwargs['d2ldebug']
        del kwargs['d2ldebug']
    r = requests.delete(uc.scheme + '://' + uc.host + route, **kwargs)
    return _fetch_content(r,debug=d)

def _get(route,uc,**kwargs):
    if uc.anonymous:
        raise ValueError('User context cannot be anonymous.').with_traceback(sys.exc_info()[2])
    kwargs.setdefault('params', None)
    kwargs.setdefault('data', None)
    kwargs.setdefault('headers', None)
    kwargs.setdefault('auth', uc)
    d = None
    if 'd2ldebug' in kwargs:
        d = kwargs['d2ldebug']
        del kwargs['d2ldebug']
    r = requests.get(uc.scheme + '://' + uc.host + route, **kwargs)
    return _fetch_content(r,debug=d)

def _post(route,uc,**kwargs):
    if uc.anonymous:
        raise ValueError('User context cannot be anonymous.').with_traceback(sys.exc_info()[2])
    kwargs.setdefault('params', None)
    kwargs.setdefault('data', None)
    kwargs.setdefault('headers', None)
    kwargs.setdefault('files', None)
    kwargs.setdefault('auth', uc)
    d = None
    if 'd2ldebug' in kwargs:
        d = kwargs['d2ldebug']
        del kwargs['d2ldebug']
    r = requests.post(uc.scheme + '://' + uc.host + route, **kwargs)
    return _fetch_content(r,debug=d)

def _put(route,uc,**kwargs):
    if uc.anonymous:
        raise ValueError('User context cannot be anonymous.').with_traceback(sys.exc_info()[2])
    kwargs.setdefault('params', None)
    kwargs.setdefault('data', None)
    kwargs.setdefault('headers', None)
    kwargs.setdefault('files', None)
    kwargs.setdefault('auth', uc)
    d = None
    if 'd2ldebug' in kwargs:
        d = kwargs['d2ldebug']
        del kwargs['d2ldebug']
    r = requests.put(uc.scheme + '://' + uc.host + route, **kwargs)
    return _fetch_content(r,debug=d)

def _get_anon(route,uc,**kwargs):
    kwargs.setdefault('params', None)
    kwargs.setdefault('data', None)
    kwargs.setdefault('headers', None)
    kwargs.setdefault('auth', uc)
    d = None
    if 'd2ldebug' in kwargs:
        d = kwargs['d2ldebug']
        del kwargs['d2ldebug']
    r = requests.get(uc.scheme + '://' + uc.host + route, **kwargs)
    return _fetch_content(r,debug=d)

def _post_anon(route,uc,**kwargs):
    kwargs.setdefault('params', None)
    kwargs.setdefault('data', None)
    kwargs.setdefault('headers', None)
    kwargs.setdefault('files', None)
    kwargs.setdefault('auth', uc)
    d = None
    if 'd2ldebug' in kwargs:
        d = kwargs['d2ldebug']
        del kwargs['d2ldebug']
    r = requests.post(uc.scheme + '://' + uc.host + route, **kwargs)
    return _fetch_content(r,debug=d)

def _simple_upload(route,uc,f,**kwargs):
    if not isinstance(f, d2ldata.D2LFile):
        raise TypeError('File must implement d2lvalence.data.D2LFile').with_traceback(sys.exc_info()[2])

    boundary = uuid.uuid4().hex
    f.Stream.seek(0) # check the tape
    fdata = f.Stream.read()
    f.Stream.seek(0) # please be kind, rewind

    pdescr = '--{0}\r\nContent-Type: application/json\r\n\r\n{1}\r\n'.format(boundary,json.dumps(f.DescriptorDict)).encode(encoding='utf-8')
    ptopbound = '--{0}\r\nContent-Disposition: form-data; name=""; filename="{1}"\r\nContent-Type: {2}\r\n\r\n'.format(boundary,f.Name,f.ContentType).encode(encoding='utf-8')
    pbotbound = '\r\n--{0}--'.format(boundary).encode(encoding='utf-8')

    payload = pdescr + ptopbound + fdata + pbotbound

    ctype_header = {'Content-Type':'multipart/mixed;boundary='+boundary}

    # populate the default state of the passed in kwargs that we care about
    kwargs.setdefault('auth',uc)
    kwargs.setdefault('data',payload)
    kwargs.setdefault('files',None)
    kwargs.setdefault('params',None)
    kwargs.setdefault('headers',None)
    kwargs.setdefault('verify',True)
    d = None
    if 'd2ldebug' in kwargs:
        d = kwargs['d2ldebug']
        del kwargs['d2ldebug']

    s = requests.Session()
    # set the session default values
    s.auth = kwargs['auth']
    s.verify = kwargs['verify']
    if kwargs['headers']:
        s.headers.update(kwargs['headers'])
    if kwargs['params']:
        s.params.update(kwargs['params'])

    # Build PreppedRequest
    p = requests.Request('POST',
                         uc.scheme + '://' + uc.host + route,
                         data = kwargs['data'],
                         auth = s.auth,
                         headers = s.headers,
                         params = s.params).prepare()

    # overlay the multipart content type header
    p.headers.update(ctype_header)
    if d:
        d.add_request(p)
    r = s.send(p)
    return _fetch_content(r,debug=d)


## API Properties functions
# Versions

def get_versions_for_product_component(uc,pc,**kwargs):
    route = '/d2l/api/{0}/versions/'.format(pc)
    return d2ldata.ProductVersions(_get_anon(route,uc,**kwargs))

def get_version_for_product_component(uc,pc,ver,**kwargs):
    route = '/d2l/api/{0}/versions/{1}'.format(pc,ver)
    return d2ldata.SupportedVersion(_get_anon(route,uc,**kwargs))

def get_all_versions(uc,**kwargs):
    route = '/d2l/api/versions/'
    r = _get_anon(route,uc,**kwargs)
    result = []
    for i in range(len(r)):
        result.append(r[i])
    return result

def check_versions(uc,supported_version_request_array,**kwargs):
    route = '/d2l/api/versions/check'
    reqs = []
    for i in range(len(supported_version_request_array)):
        if not isinstance(supported_version_request_array[i], d2ldata.SupportedVersionRequest):
            raise TypeError('Supported version request array elements must implement d2lvalence.data.SupportedVersionRequest').with_traceback(sys.exc_info()[2])
        reqs.append(supported_version_request_array[i].as_dict())

    kwargs.setdefault('data',json.dumps(reqs))
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    return d2ldata.BulkSupportedVersionResponse(_post_anon(route,uc,**kwargs))


## User functions
# User data
def delete_user(uc,user_id,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/users/{1}'.format(ver,user_id)
    return _delete(route,uc,**kwargs)

def get_users(uc,org_defined_id=None,user_name=None,bookmark=None,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/users/'.format(ver)
    result = None
    kwargs.setdefault('params',{})
    if bookmark:
        kwargs['params'].update({'bookmark':bookmark})
    if user_name:
        kwargs['params'].update({'userName':user_name})
    if org_defined_id:
        kwargs['params'].update({'orgDefinedId':org_defined_id})
    r = _get(route,uc,**kwargs)
    if org_defined_id:
        result = []
        if len(r) < 1:
            pass
        else:
            for i in range(len(r)):
                result.append(d2ldata.UserData(r[i]))
    elif user_name:
        result = d2ldata.UserData(r)
    else:
        result = d2ldata.PagedResultSet(r)

    return result

def get_user(uc,user_id,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/users/{1}'.format(ver,user_id)
    return d2ldata.UserData(_get(route,uc,**kwargs))

def get_whoami(uc,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/users/whoami'.format(ver)
    return d2ldata.WhoAmIUser(_get(route,uc,**kwargs))

def create_user(uc,create_user_data,ver='1.0',**kwargs):
    if not isinstance(create_user_data, d2ldata.CreateUserData):
        raise TypeError('New user data must implement d2lvalence.data.CreateUserData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/lp/{0}/users/'.format(ver)
    kwargs.setdefault('data',create_user_data.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    return d2ldata.UserData(_post(route,uc,**kwargs))

def update_user(uc,user_id,update_user_data,ver='1.0',**kwargs):
    if not isinstance(update_user_data, d2ldata.UpdateUserData):
        raise TypeError('Update user data must implement d2lvalence.data.UpdateUserData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/lp/{0}/users/{1}'.format(ver,user_id)
    kwargs.setdefault('data',update_user_data.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    return d2ldata.UserData(_put(route,uc,**kwargs))

# Activation
def get_user_activation(uc,user_id,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/users/{1}/activation'.format(ver,user_id)
    return d2ldata.UserActivationData(_get(route,uc,**kwargs))

def update_user_activation(uc,user_id,activation_data,ver='1.0',**kwargs):
    if not isinstance(activation_data, d2ldata.UserActivationData):
        raise TypeError('Activation data for user must implement d2lvalence.data.UserActivationData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/lp/{0}/users/{1}/activation'.format(ver,user_id)
    kwargs.setdefault('data',activation_data.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    return _put(route,uc,**kwargs)

# Profiles
def delete_my_profile_image(uc,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/profile/myProfile/image'.format(ver)
    return _delete(route,uc,**kwargs)

def delete_profile_image_by_profile_id(uc,profile_id,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/profile/{1}/image'.format(ver,profile_id)
    return _delete(route,uc,**kwargs)

def delete_profile_image_by_user_id(uc,user_id,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/profile/user/{1}/image'.format(ver,user_id)
    return _delete(route,uc,**kwargs)

def get_profile_by_profile_id(uc,profile_id,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/profile/{1}'.format(ver,profile_id)
    return d2ldata.UserProfile(_get(route,uc,**kwargs))

def get_profile_image_by_profile_id(uc,profile_id,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/profile/{1}/image'.format(ver,profile_id)
    return _get(route,uc,**kwargs)

def get_profile_by_user_id(uc,user_id,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/profile/user/{1}'.format(ver,user_id)
    return d2ldata.UserProfile(_get(route,uc,**kwargs))

def get_profile_image_by_user_id(uc,user_id,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/profile/user/{1}/image'.format(ver,user_id)
    return _get(route,uc,**kwargs)

def get_my_profile(uc,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/profile/myProfile'.format(ver)
    return d2ldata.UserProfile(_get(route,uc,**kwargs))

def get_my_profile_image(uc,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/profile/myProfile/image'.format(ver)
    return _get(route,uc,**kwargs)

def update_my_profile(uc,updated_profile_data,ver='1.0',**kwargs):
    if not isinstance(updated_profile_data, d2ldata.UserProfile):
        raise TypeError('Updated profile data must implement d2lvalence.data.UserProfile').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/lp/{0}/profile/myProfile'.format(ver)
    kwargs.setdefault('data', updated_profile_data.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    return d2ldata.UserProfile(_put(route,uc,**kwargs))

def update_profile_image_by_user_id(uc,user_id,d2l_file,ver='1.0',**kwargs):
    if not isinstance(d2l_file, d2ldata.D2LFile):
        raise TypeError('Image must implement d2lvalence.data.D2LFile').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/lp/{0}/profile/user/{1}/image'.format(ver,user_id)
    kwargs.setdefault('files',{})
    kwargs['files'].update({'profileImage': (d2l_file.Name, d2l_file.Stream)})
    return _post(route,uc,**kwargs)

def update_profile_image_by_profile_id(uc,profile_id,d2l_file,ver='1.0',**kwargs):
    if not isinstance(d2l_file, d2ldata.D2LFile):
        raise TypeError('Image must implement d2lvalence.data.D2LFile').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/lp/{0}/profile/{1}/image'.format(ver,profile_id)
    kwargs.setdefault('files',{})
    kwargs['files'].update({'profileImage': (d2l_file.Name, d2l_file.Stream)})
    return _post(route,uc,**kwargs)

def update_my_profile_image(uc,d2l_file,ver='1.0',**kwargs):
    if not isinstance(d2l_file, d2ldata.D2LFile):
        raise TypeError('Image must implement d2lvalence.data.D2LFile').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/lp/{0}/profile/myProfile/image'.format(ver)
    kwargs.setdefault('files',{})
    kwargs['files'].update({'profileImage': (d2l_file.Name, d2l_file.Stream)})
    return _post(route,uc,**kwargs)


# Passwords
def delete_password_for_user(uc,user_id,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/users/{1}/password'.format(ver,user_id)
    return _delete(route,uc,**kwargs)

def send_password_reset_email_for_user(uc,user_id,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/users/{1}/password'.format(ver,user_id)
    kwargs.setdefault('data',None)
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Length':'0'})
    return _post(route,uc,**kwargs)

def update_password_for_user(uc,user_id,new_password,ver='1.0',**kwargs):
    if not isinstance(new_password, d2ldata.UserPasswordData):
        raise TypeError('New password data must implement d2lvalence.data.UserPasswordData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/lp/{0}/users/{1}/password'.format(ver,user_id)
    kwargs.setdefault('data',new_password.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    return _put(route,uc,**kwargs)

# Roles
def get_all_roles(uc,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/roles/'.format(ver)
    r = _get(route,uc,**kwargs)
    result = []
    if len(r) < 1:
        pass
    else:
        for i in range(len(r)):
            result.append(d2ldata.Role(r[i]))
    return result

def get_role(uc,role_id,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/roles/{1}'.format(ver,role_id)
    return d2ldata.Role(_get(route,uc,**kwargs))


## Org structure
def get_organization_info(uc,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/organization/info'.format(ver)
    return d2ldata.Organization(_get(route,uc,**kwargs))

def get_orgunit_children(uc,org_unit_id,org_unit_type_id=None,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/orgstructure/{1}/children/'.format(ver,org_unit_id)
    kwargs.setdefault('params', {})
    if org_unit_type_id:
       kwargs['params'].update({'ouTypeId':org_unit_type_id})
    r = _get(route,uc,**kwargs)
    result = []
    for i in range(len(r)):
        result.append(d2ldata.OrgUnit(r[i]))
    return result

def get_orgunit_descendants(uc,org_unit_id,org_unit_type_id=None,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/orgstructure/{1}/descendants/'.format(ver,org_unit_id)
    kwargs.setdefault('params', {})
    if org_unit_type_id:
        kwargs['params'].update({'ouTypeId':org_unit_type_id})
    r = _get(route,uc,**kwargs)
    result = []
    for i in range(len(r)):
        result.append(d2ldata.OrgUnit(r[i]))
    return result

def get_orgunit_parents(uc,org_unit_id,org_unit_type_id=None,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/orgstructure/{1}/parents/'.format(ver,org_unit_id)
    kwargs.setdefault('params', {})
    if org_unit_type_id:
        kwargs['params'].update({'ouTypeId':org_unit_type_id})
    r = _get(route,uc,**kwargs)
    result = []
    for i in range(len(r)):
        result.append(d2ldata.OrgUnit(r[i]))
    return result

def get_orgunit_properties(uc,org_unit_id,ver='1.3',**kwargs):
    route = '/d2l/api/lp/{0}/orgstructure/{1}'.format(ver,org_unit_id)
    r = _get(route,uc,**kwargs)
    return d2ldata.OrgUnit(r)

def create_custom_orgunit(uc,org_unit_create_data=None,ver='1.3',**kwargs):
    if not isinstance(org_unit_create_data, d2ldata.OrgUnitCreateData):
        raise TypeError('New orgunit must implement d2lvalence.data.OrgUnitCreateData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/lp/{0}/orgstructure/'.format(ver)
    kwargs.setdefault('data',org_unit_create_data.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    return d2ldata.OrgUnit(_post(route,uc,**kwargs))

def update_custom_orgunit(uc,org_unit_id,org_unit_properties=None,ver='1.4',**kwargs):
    if not isinstance(org_unit_properties, d2ldata.OrgUnitProperties):
        raise TypeError('New orgunit properties must implement d2lvalence.data.OrgUnitProperties').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/lp/{0}/orgstructure/{1}'.format(ver,org_unit_id)
    kwargs.setdefault('data',org_unit_properties.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    return d2ldata.OrgUnitProperties(_put(route,uc,**kwargs))

# Org unit types
def get_all_outypes(uc,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/outypes/'.format(ver)
    r = _get(route,uc,**kwargs)
    result = []
    if len(r) < 1:
        pass
    else:
        for i in range(len(r)):
            result.append(d2ldata.OrgUnitType(r[i]))
    return result

def get_outype(uc,outype_id,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/outypes/{1}'.format(ver,outype_id)
    return d2ldata.OrgUnitType(_get(route,uc,**kwargs))


## Enrollments
def get_classlist(uc,org_unit_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/classlist/'.format(ver,org_unit_id)
    r = _get(route,uc,**kwargs)
    result = []
    for i in range(len(r)):
        result.append(d2ldata.ClasslistUser(r[i]))
    return result

def delete_user_enrollment_in_orgunit(uc,org_unit_id,user_id,org_first=True,ver='1.0',**kwargs):
    if org_first:
        route = '/d2l/api/lp/{0}/enrollments/orgUnits/{1}/users/{2}'.format(ver,org_unit_id,user_id)
    else:
        route = '/d2l/api/lp/{0}/enrollments/users/{1}/orgUnits/{2}'.format(ver,user_id,org_unit_id)
    return _delete(route,uc,**kwargs)

def get_my_enrollments(uc,org_unit_type_id=None,bookmark=None,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/enrollments/myenrollments/'.format(ver)
    kwargs.setdefault('params',{})
    if bookmark:
        kwargs['params'].update({'bookmark':bookmark})
    if org_unit_type_id:
        kwargs['params'].update({'orgUnitTypeId':org_unit_type_id})
    r = _get(route,uc,**kwargs)
    return d2ldata.PagedResultSet(r)

def get_enrolled_users_for_orgunit(uc,org_unit_id,role_id=None,bookmark=None,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/enrollments/orgUnits/{1}/users/'.format(ver,org_unit_id)
    kwargs.setdefault('params',{})
    if bookmark:
        kwargs['params'].update({'bookmark':bookmark})
    if role_id:
        kwargs['params'].update({'roleId':role_id})
    r = _get(route,uc,**kwargs)
    return d2ldata.PagedResultSet(r)

def get_enrolled_user_in_orgunit(uc,org_unit_id,user_id,org_first=True,ver='1.0',**kwargs):
    if org_first:
        route = '/d2l/api/lp/{0}/enrollments/orgUnits/{1}/users/{2}'.format(ver,org_unit_id,user_id)
    else:
        route = '/d2l/api/lp/{0}/enrollments/users/{1}/orgUnits/{2}'.format(ver,user_id,org_unit_id)
    return d2ldata.EnrollmentData(_get(route,uc,**kwargs))

def get_all_enrollments_for_user(uc,user_id,org_unit_type_id=None,role_id=None,bookmark=None,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/enrollments/users/{1}/orgUnits/'.format(ver,user_id)
    kwargs.setdefault('params',{})
    if bookmark:
        kwargs['params'].update({'bookmark':bookmark})
    if org_unit_type_id:
        kwargs['params'].update({'orgUnitTypeId':org_unit_type_id})
    if role_id:
        kwargs['params'].update({'roleId':role_id})
    r = _get(route,uc,**kwargs)
    return d2ldata.PagedResultSet(r)

def create_enrollment_for_user(uc,new_enrollment,ver='1.0',**kwargs):
    if not isinstance(new_enrollment, d2ldata.CreateEnrollmentData):
        raise TypeError('New enrollment must implement d2lvalence.data.CreateEnrollmentData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/lp/{0}/enrollments/'.format(ver)
    kwargs.setdefault('data',new_enrollment.as_json())
    r = _post(route,uc,**kwargs)
    return d2ldata.EnrollmentData(r)

# Groups
def delete_group_category_from_orgunit(uc,org_unit_id,group_category_id,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/{1}/groupcategories/{2}'.format(ver,org_unit_id,group_category_id)
    return _delete(route,uc,**kwargs)

def delete_group_from_orgunit(uc,org_unit_id,group_category_id,group_id,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/{1}/groupcategories/{2}/groups/{3}'.format(ver,org_unit_id,group_category_id,group_id)
    return _delete(route,uc,**kwargs)

def delete_user_from_group(uc,org_unit_id,group_category_id,group_id,user_id,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/{1}/groupcategories/{2}/groups/{3}/enrollments/{4}'.format(ver,org_unit_id,group_category_id,group_id,user_id)
    return _delete(route,uc,**kwargs)

def get_group_categories_for_orgunit(uc,org_unit_id,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/{1}/groupcategories/'.format(ver,org_unit_id)
    r = _get(route,uc,**kwargs)
    result = []
    for i in range(len(r)):
        result.append( d2ldata.GroupCategoryDataFetch(r[i]))
    return result

## Course offerings
def delete_course_offering(uc,org_unit_id,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/courses/{1}'.format(ver,org_unit_id)
    return _delete(route,uc,**kwargs)

def get_course_schemas(uc,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/courses/schema'.format(ver)
    r = _get(route,uc,**kwargs)
    result = []
    for i in range(len(r)):
        result.append( d2ldata.CourseSchemaElement(r[i]))
    return result

def get_course_offering(uc,org_unit_id,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/courses/{1}'.format(ver,org_unit_id)
    return d2ldata.CourseOffering(_get(route,uc,**kwargs))

def create_course_offering(uc,new_course_offering,ver='1.0',**kwargs):
    if not isinstance(new_course_offering, d2ldata.CreateCourseOffering):
        raise TypeError('New course offering must implement d2lvalence.data.CreateCoursOffering').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/lp/{0}/courses/'.format(ver)
    kwargs.setdefault('data',new_course_offering.as_json())
    r = _post(route,uc,**kwargs)
    return d2ldata.CourseOffering(r)

def update_course_offering(uc,org_unit_id,course_offering_update,ver='1.0',**kwargs):
    if not isinstance(course_offering_update, d2ldata.CourseOfferingInfo):
        raise TypeError('Course offering update must implement d2lvalence.data.CourseOfferingInfo').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/lp/{0}/courses/{1}'.format(ver,org_unit_id)
    kwargs.setdefault('data',course_offering_update.as_json())
    r = _put(route,uc,**kwargs)
    return d2ldata.CourseOffering(r)

# Course templates
def delete_course_template(uc,org_unit_id,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/coursetemplates/{1}'.format(ver,org_unit_id)
    return _delete(route,uc,**kwargs)

def get_course_template(uc,org_unit_id,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/coursetemplates/{1}'.format(ver,org_unit_id)
    return d2ldata.CourseTemplate(_get(route,uc,**kwargs))

def get_course_templates_schema(uc,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/coursetemplates/schema'.format(ver)
    r = _get(route,uc,**kwargs)
    result = []
    for i in range(len(r)):
        result.append( d2ldata.CourseSchemaElement(r[i]))
    return result

def create_course_template(uc,new_course_template,ver='1.0',**kwargs):
    if not isinstance(new_course_template,d2ldata.CreateCourseTemplate):
        raise TypeError('New course template must implement d2lvalence.data.CreateCourseTemplate').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/lp/{0}/coursetemplates/'.format(ver)
    kwargs.setdefault('data',new_course_template.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    r = _post(route,uc,**kwargs)
    return d2ldata.CourseTemplate(r)

def update_course_template(uc,org_unit_id,course_template_update,ver='1.0',**kwargs):
    if not isinstance(course_template_update, d2ldata.CourseTemplateInfo):
        raise TypeError('Course template update must implement d2lvalence.data.CourseTemplateInfo').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/lp/{0}/coursetemplates/{1}'.format(ver,org_unit_id)
    kwargs.setdefault('data',course_template_update.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    return _put(route,uc,**kwargs)

## Grades
def delete_grade_object_for_org(uc,org_unit_id,grade_object_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/grades/{2}'.format(ver,org_unit_id,grade_object_id)
    return _delete(route,uc,**kwargs)

def get_all_grade_objects_for_org(uc,org_unit_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/grades/'.format(ver,org_unit_id)
    r = _get(route,uc,**kwargs)
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

def get_grade_object_for_org(uc,org_unit_id,grade_object_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/grades/{2}'.format(ver,org_unit_id,grade_object_id)
    r = _get(route,uc,**kwargs)
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

def create_grade_object_for_org(uc,org_unit_id,new_grade_object,ver='1.0',**kwargs):
    if not isinstance(new_grade_object, d2ldata.GradeObjectCreateData):
        raise TypeError('New grade object must implement d2lvalence.data.GradeObjectCreateData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/le/{0}/{1}/grades/'.format(ver,org_unit_id)
    kwargs.setdefault('data',new_grade_object.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    r = _post(route,uc,**kwargs)
    return d2ldata.GradeObject(r)

def update_grade_object_for_org(uc,org_unit_id,grade_object_id,new_grade_object,ver='1.0',**kwargs):
    if not isinstance(new_grade_object, d2ldata.GradeObjectCreateData):
        raise TypeError('New grade object must implement d2lvalence.data.GradeObjectCreateData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/le/{0}/{1}/grades/{2}'.format(ver,org_unit_id)
    kwargs.setdefault('data',new_grade_object.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    r = _put(route,uc,**kwargs)
    return d2ldata.GradeObject(r)

# Grade categories
def delete_grade_category_for_orgunit(uc,org_unit_id,category_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/grades/categories/{2}'.format(ver,org_unit_id,category_id)
    return _delete(route,uc,**kwargs)

def get_all_grade_categories_for_orgunit(uc,org_unit_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/grades/categories/'.format(ver,org_unit_id)
    r = _get(route,uc,**kwargs)
    result = []
    for i in range(len(r)):
        result.append(d2ldata.GradeObjectCategory(r[i]))
    return result

def get_grade_category_for_orgunit(uc,org_unit_id,category_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/grades/categories/{2}'.format(ver,org_unit_id,category_id)
    return d2ldata.GradeObjectCategory(_get(route,uc,**kwargs))

def create_grade_category_for_orgunit(uc,org_unit_id,new_grade_category_data,ver='1.0',**kwargs):
    if not isinstance(new_grade_category_data, d2ldata.GradeObjectCategoryData):
        raise TypeError('New grade category data must implement d2lvalence.data.GradeObjectCategoryData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/le/{0}/{1}/grades/categories/'.format(ver,org_unit_id)
    kwargs.setdefault('data',new_grade_category_data.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    r = _post(route,uc,**kwargs)
    return d2ldata.GradeObjectCategory(r)

# Grade schemes
def get_all_grade_schemes_for_orgunit(uc,org_unit_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/grades/schemes/'.format(ver,org_unit_id)
    r = _get(route,uc,**kwargs)
    result = []
    for i in range(len(r)):
        result.append(d2ldata.GradeScheme(r[i]))
    return result

def get_grade_scheme_for_orgunit(uc,org_unit_id,scheme_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/grades/schemes/{2}'.format(ver,org_unit_id,scheme_id)
    return (d2ldata.GradeScheme(_get(route,uc,**kwargs)))


# Grade values
def get_my_final_grade_value_for_org(uc,org_unit_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/grades/final/values/myGradeValue'.format(ver,org_unit_id)
    return d2ldata.GradeValueComputable(_get(route,uc,**kwargs))

def get_final_grade_value_for_user_in_org(uc,org_unit_id,user_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/grades/final/values/{2}'.format(ver,org_unit_id,user_id)
    return d2ldata.GradeValueComputable(_get(route,uc,**kwargs))

def get_grade_value_for_user_in_org(uc,org_unit_id,grade_object_id,user_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/grades/{2}/values/{3}'.format(ver,org_unit_id,grade_object_id,user_id)
    r = _get(route,uc,**kwargs)
    result = None
    if 'PointsNumerator' in r:
        result = d2ldata.GradeValueComputable(r)
    else:
        result = d2ldata.GradeValue(r)
    return result

def get_my_grade_value_for_org(uc,org_unit_id,grade_object_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/grades/{2}/values/myGradeValue'.format(ver,org_unit_id,grade_object_id)
    r = _get(route,uc,**kwargs)
    result = None
    if 'PointsNumerator' in r:
        result = d2ldata.GradeValueComputable(r)
    else:
        result = d2ldata.GradeValue(r)
    return result

def get_all_my_grade_values_for_org(uc,org_unit_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/grades/values/myGradeValues/'.format(ver,org_unit_id)
    r = _get(route,uc,**kwargs)
    result = []
    for i in range(len(r)):
        if 'PointsNumerator' in r[i]:
            result.append(d2ldata.GradeValueComputable(r[i]))
        else:
            result.append(d2ldata.GradeValue(r[i]))
    return result

def get_all_grade_values_for_user_in_org(uc,org_unit_id,user_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/grades/values/{2}/'.format(ver,org_unit_id,user_id)
    r = _get(route,uc,**kwargs)
    result = []
    for i in range(len(r)):
        if 'PointsNumerator' in r[i]:
            result.append(d2ldata.GradeValueComputable(r[i]))
        else:
            result.append(d2ldata.GradeValue(r[i]))
    return result

def recalculate_final_grade_value_for_user_in_org(uc,org_unit_id,user_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/grades/final/calculated/{2}'.format(ver,org_unit_id,user_id)
    kwargs.setdefault('data',None)
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Length':'0'})
    return _post(route,uc,**kwargs)

def recalculate_all_final_grade_values_for_org(uc,org_unit_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/grades/final/calculated/all'.format(ver,org_unit_id)
    kwargs.setdefault('data',None)
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Length':'0'})
    return _post(route,uc,**kwargs)

def update_final_adjusted_grade_value_for_user_in_org(uc,org_unit_id,user_id,updated_final_adjusted_grade,ver='1.0',**kwargs):
    if not isinstance(updated_final_adjusted_grade, d2ldata.IncomingFinalAdjustedGradeValue):
        raise TypeError('New grade value must implement d2lvalence.data.IncomingFinalAdjustedGradeValue').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/le/{0}/{1}/grades/final/values/{2}'.format(ver,org_unit_id,user_id)
    kwargs.setdefault('data',updated_final_adjusted_grade.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    return _put(route,uc,**kwargs)

def update_grade_value_for_user_in_org(uc,org_unit_id,grade_object_id,user_id,updated_grade_value,ver='1.0',**kwargs):
    if not isinstance(updated_grade_value, d2ldata.IncomingGradeValue):
        raise TypeError('New grade value must implement d2lvalence.data.IncomingGradeValue').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/le/{0}/{1}/grades/{2}/values/{3}'.format(ver,org_unit_id,grade_object_id,user_id)
    kwargs.setdefault('data',updated_grade_value.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    return _put(route,uc,**kwargs)

# Course completion
def delete_course_completion(uc,org_unit_id,completion_id,ver='1.1',**kwargs):
    route = '/d2l/api/le/{0}/{1}/grades/courseCompletion/{2}'.format(ver,org_unit_id,completion_id)
    return _delete(route,uc,**kwargs)

def get_all_course_completions_for_org(uc,org_unit_id,user_id=None,start_expiry=None,end_expiry=None,bookmark=None,ver='1.1',**kwargs):
    route = '/d2l/api/le/{0}/{1}/grades/courseCompletion/'.format(ver,org_unit_id)
    kwargs.setdefault('params',{})
    if user_id:
        kwargs['params'].update({'userId': user_id})
    if start_expiry:
        kwargs['params'].update({'startExpiry': start_expiry})
    if end_expiry:
        kwargs['params'].update({'endExpiry': end_expiry})
    if bookmark:
        kwargs['params'].update({'bookmark': bookmark})
    r = _get(route,uc,**kwargs)
    return d2ldata.PagedResultSet(r)

def get_all_course_completions_for_user(uc,user_id,start_expiry=None,end_expiry=None,bookmark=None,ver='1.1',**kwargs):
    route = '/d2l/api/le/{0}/grades/courseCompletion/{1}/'.format(ver,user_id)
    kwargs.setdefault('params',{})
    if start_expiry:
        kwargs['params'].update({'startExpiry': start_expiry})
    if end_expiry:
        kwargs['params'].update({'endExpiry': end_expiry})
    if bookmark:
        kwargs['params'].update({'bookmark': bookmark})
    r = _get(route,uc,**kwargs)
    return d2ldata.PagedResultSet(r)

def create_course_completion_for_org(uc,org_unit_id,new_course_completion,ver='1.1',**kwargs):
    if not isinstance(new_course_completion, d2ldata.CourseCompletionCreateData):
        raise TypeError('New course completion record must implement d2lvalence.data.CourseCompletionCreateData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/le/{0}/{1}/grades/courseCompletion/'.format(ver,org_unit_id)
    kwargs.setdefault('data',new_course_completion.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    r = _post(route,uc,**kwargs)
    return d2ldata.CourseCompletion(r)

def update_course_completion_for_org(uc,org_unit_id,course_completion_id,updated_course_completion,ver='1.1',**kwargs):
    if not isinstance(updated_course_completion, d2ldata.CourseCompletionUpdateData):
        raise TypeError('New course completion record must implement d2lvalence.data.CourseCompletionUpdateData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/le/{0}/{1}/grades/courseCompletion/{2}'.format(ver,org_unit_id,course_completion_id)
    kwargs.setdefault('data',updated_course_completion.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    r = _post(route,uc,**kwargs)
    return d2ldata.CourseCompletion(r)


## Dropbox
def get_all_dropbox_folders_for_orgunit(uc,org_unit_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/dropbox/folders/'.format(ver,org_unit_id)
    return _get(route,uc,**kwargs)

def get_dropbox_folder_for_orgunit(uc,org_unit_id,folder_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/dropbox/folders/{2}'.format(ver,org_unit_id,folder_id)
    return _get(route,uc,**kwargs)

def create_my_submission_for_dropbox(uc,org_unit_id,folder_id,d2l_file,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/dropbox/folders/{2}/submissions/mysubmissions/'.format(ver,org_unit_id,folder_id)
    return _simple_upload(route,uc,d2l_file,**kwargs)

def create_submission_for_group_dropbox_folder(uc,org_unit_id,folder_id,group_id,d2l_file,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/dropbox/folders/{2}/submissions/group/{3}'.format(ver,org_unit_id,folder_id,group_id)
    return _simple_upload(route,uc,d2l_file,**kwargs)

def get_submissions_for_dropbox_folder(uc,org_unit_id,folder_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/dropbox/folders/{2}/submissions/'.format(ver,org_unit_id,folder_id)
    return _get(route,uc,**kwargs)

## Lockers
def _get_locker_item(uc,route,**kwargs):
    result = None
    r = _get(route,uc,**kwargs)
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

def delete_my_locker_item(uc,path='/',ver='1.0',**kwargs):
    if _check_path(path):
        route = '/d2l/api/le/{0}/locker/myLocker{1}'.format(ver,path)
        r = _delete(route,uc,**kwargs)

def delete_locker_item(uc,user_id,path='/',ver='1.0',**kwargs):
    if _check_path(path):
        route = '/d2l/api/le/{0}/locker/user/{1}{2}'.format(ver,user_id,path)
        r = _delete(route,uc,**kwargs)

def get_my_locker_item(uc,path='/',ver='1.0',**kwargs):
    if _check_path(path):
        route = '/d2l/api/le/{0}/locker/myLocker{1}'.format(ver,path)
        return _get_locker_item(uc,route,**kwargs)

def get_locker_item(uc,user_id,path='/',ver='1.0',**kwargs):
    if _check_path(path):
        route = '/d2l/api/le/{0}/locker/user/{1}{2}'.format(ver,user_id,path)
        return _get_locker_item(uc,route,**kwargs)

def create_my_locker_folder(uc,folder_name,path='/',ver='1.0',**kwargs):
    if _check_path(path):
        route = '/d2l/api/le/{0}/locker/myLocker{1}'.format(ver,path)
        kwargs.setdefault('data',json.dumps(folder_name))
        kwargs.setdefault('headers',{})
        kwargs['headers'].update({'Content-Type':'application/json'})
        return _post(route,uc,**kwargs)

def create_locker_folder(uc,user_id,folder_name,path='/',ver='1.0',**kwargs):
    if _check_path(path):
        route = '/d2l/api/le/{0}/locker/user/{1}{2}'.format(ver,user_id,path)
        kwargs.setdefault('data',json.dumps(folder_name))
        kwargs.setdefault('headers',{})
        kwargs['headers'].update({'Content-Type':'application/json'})
        return _post(route,uc,**kwargs)

def create_my_locker_file(uc,d2l_file,path='/',ver='1.0',**kwargs):
    if _check_path(path):
        route = '/d2l/api/le/{0}/locker/myLocker{1}'.format(ver,path)
        return _simple_upload(route,uc,d2l_file,**kwargs)

def create_locker_file(uc,user_id,d2l_file,path='/',ver='1.0',**kwargs):
    if _check_path(path):
        route = '/d2l/api/le/{0}/locker/user/{1}{2}'.format(ver,user_id,path)
        return _simple_upload(route,uc,d2l_file,**kwargs)

def rename_my_locker_folder(uc,new_folder_name,path='/',ver='1.0',**kwargs):
    if _check_path(path):
        route = '/d2l/api/le/{0}/locker/myLocker{1}'.format(ver,path)
        kwargs.setdefault('data',json.dumps(new_folder_name))
        kwargs.setdefault('headers',{})
        kwargs['headers'].update({'Content-Type':'application/json'})
        return _put(route,uc,**kwargs)

def rename_locker_folder(uc,user_id,new_folder_name,path='/',ver='1.2',**kwargs):
    if _check_path(path):
        route = '/d2l/api/le/{0}/locker/user/{1}{2}'.format(ver,user_id,path)
        kwargs.setdefault('data',json.dumps(new_folder_name))
        kwargs.setdefault('headers',{})
        kwargs['headers'].update({'Content-Type':'application/json'})
        return _put(route,uc,**kwargs)

# Lockers and groups
def delete_group_locker_item(uc,org_unit_id,group_id,path='/',ver='1.0',**kwargs):
    if _check_path(path):
        route = '/d2l/api/le/{0}/{1}/locker/group/{2}{3}'.format(ver,org_unit_id,group_id,path)
        return _delete(route,uc,**kwargs)

def get_group_locker_category(uc,org_unit_id,group_cat_id,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/{1}/groupcategories/{2}/locker'.format(ver,org_unit_id,group_cat_id)
    return d2ldata.GroupLocker(_get(route,uc,**kwargs))

def get_group_locker_item(uc,org_unit_id,group_id,path='/',ver='1.0',**kwargs):
    if _check_path(path):
        route = '/d2l/api/le/{0}/{1}/locker/group/{2}{3}'.format(ver,org_unit_id,group_id,path)
        return _get_locker_item(uc,route,**kwargs)

def setup_group_locker_category(uc,org_unit_id,group_cat_id,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/{1}/groupcategories/{2}/locker'.format(ver,org_unit_id,group_cat_id)
    return d2ldata.GroupLocker(_post(route,uc,**kwargs))

def create_group_locker_folder(uc,org_unit_id,group_id,folder_name,path='/',ver='1.0',**kwargs):
    if _check_path(path):
        route = '/d2l/api/le/{0}/{1}/locker/group/{2}{3}'.format(ver,org_unit_id,group_id,path)
        kwargs.setdefault('data',json.dumps(folder_name))
        kwargs.setdefault('headers',{})
        kwargs['headers'].update({'Content-Type':'application/json'})
        return _post(route,uc,**kwargs)

def create_group_locker_file(uc,org_unit_id,group_id,d2l_file,path='/',ver='1.0',**kwargs):
    if _check_path(path):
        route = '/d2l/api/le/{0}/{1}/locker/group/{2}{3}'.format(ver,org_unit_id,group_id,path)
        return _simple_upload(route,uc,d2l_file,**kwargs)

def rename_group_locker_folder(uc,org_unit_id,group_id,new_folder_name,path='/',ver='1.0',**kwargs):
    if _check_path(path):
        route = '/d2l/api/le/{0}/{1}/locker/group/{2}{3}'.format(ver,org_unit_id,group_id,path)
        kwargs.setdefault('data',json.dumps(new_folder_name))
        kwargs.setdefault('headers',{})
        kwargs['headers'].update({'Content-Type':'application/json'})
        return _put(route,uc,**kwargs)

## Discussion forum routes
def delete_discussion_forum(uc,org_unit_id,forum_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}'.format(ver,org_unit_id,forum_id)
    return _delete(route,uc,**kwargs)

def get_discussion_forums(uc,org_unit_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/'.format(ver,org_unit_id)
    r = _get(route,uc,**kwargs)
    result = []
    for i in range(len(r)):
        result.append(d2ldata.Forum(r[i]))
    return result

def get_discussion_forum(uc,org_unit_id,forum_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}'.format(ver,org_unit_id,forum_id)
    return d2ldata.Forum(_get(route,uc,**kwargs))

def create_discussion_forum(uc,org_unit_id,new_forum_data,ver='1.0',**kwargs):
    if not isinstance(new_forum_data, d2ldata.ForumData):
        raise TypeError('New forum data must implement d2lvalence.data.ForumData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/le/{0}/{1}/discussions/forums/'.format(ver,org_unit_id)
    kwargs.setdefault('data',new_forum_data.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    r = _post(route,uc,**kwargs)
    return d2ldata.Forum(r)

def update_discussion_forum(uc,org_unit_id,forum_id,updated_forum_data,ver='1.0',**kwargs):
    if not isinstance(updated_forum_data, d2ldata.ForumUpdateData):
        raise TypeError('Updated forum data must implement d2lvalence.data.ForumUpdateData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}'.format(ver,org_unit_id,forum_id)
    kwargs.setdefault('data',updated_forum_data.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    r = _put(route,uc,**kwargs)
    return d2ldata.Forum(r)

# Discussion topics
def delete_discussion_topic(uc,org_unit_id,forum_id,topic_id,ver='1.0',**kwargs):
    route = '/d2l/api/{0}/{1}/discussions/forums/{2}/topics/{3}'.format(ver,org_unit_id,forum_id,topic_id)
    return _delete(route,uc,**kwargs)

def delete_discussion_topic_group_restriction(uc,org_unit_id,forum_id,topic_id,group_restriction,ver='1.0',**kwargs):
    if not isinstance(group_restriction, d2ldata.GroupRestriction):
        raise TypeError('Group restriction must implement d2lvalence.data.GroupRestriction').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/{0}/{1}/discussions/forums/{2}/topics/{3}/groupRestrictions/'.format(ver,org_unit_id,forum_id,topic_id)
    kwargs.setdefault('data',group_restriction.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    return _delete(route,uc,**kwargs)

def get_discussion_topics(uc,org_unit_id,forum_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/'.format(ver,org_unit_id,forum_id)
    r = _get(route,uc,**kwargs)
    result = []
    for i in range(len(r)):
        result.append(d2ldata.Topic(r[i]))
    return result

def get_discussion_topic(uc,org_unit_id,forum_id,topic_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}'.format(ver,org_unit_id,forum_id,topic_id,ver='1.0')
    return d2ldata.Topic(_get(route,uc,**kwargs))

def get_discussion_topics_group_restrictions(uc,org_unit_id,forum_id,topic_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/groupRestrictions/'.format(ver,org_unit_id,forum_id,topic_id)
    r = _get(route,uc,**kwargs)
    result = []
    for i in range(len(r)):
        result.append(d2ldata.GroupRestriction(r[i]))
    return result

def create_discussion_topic(uc,org_unit_id,forum_id,new_topic_data,ver='1.0',**kwargs):
    if not isinstance(new_topic_data,d2ldata.CreateTopicData):
        raise TypeError('New topic data must implement d2lvalence.data.CreateTopicData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/'.format(ver,org_unit_id,forum_id)
    kwargs.setdefault('data',new_topic_data.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    r = _post(route,uc,**kwargs)
    return d2ldata.Topic(r)

def update_discussion_topic(uc,org_unit_id,forum_id,topic_id,new_topic_data,ver='1.0',**kwargs):
    if not isinstance(new_topic_data,d2ldata.CreateTopicData):
        raise TypeError('Updated topic data must implement d2lvalence.data.CreateTopicData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}'.format(ver,org_unit_id,forum_id,topic_id)
    kwargs.setdefault('data',new_topic_data.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    r = _put(route,uc,**kwargs)
    return d2ldata.Topic(r)

def update_group_restrictions_list(uc,org_unit_id,forum_id,topic_id,group_restriction,ver='1.0',**kwargs):
    if not isinstance(group_restriction,d2ldata.GroupRestriction):
        raise TypeError('Group restriction must implement d2lvalence.data.GroupRestriction').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/groupRestrictions/'.format(ver,org_unit_id,forum_id,topic_id)
    kwargs.setdefault('data',group_restriction.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    return _put(route,uc,**kwargs)

# Discussion posts
def delete_discussion_post(uc,org_unit_id,forum_id,topic_id,post_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    return _delete(route,uc,**kwargs)

def delete_my_rating_for_discussion_post(uc,org_unit_id,forum_id,topic_id,post_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}/Rating/MyRating'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    return _delete(route,uc,**kwargs)

def get_discussion_posts(uc,org_unit_id,forum_id,topic_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/'.format(ver,org_unit_id,forum_id,topic_id)
    r = _get(route,uc,**kwargs)
    result = []
    for i in range(len(r)):
        result.append(d2ldata.Post(r[1]))
    return result

def get_discussion_post(uc,org_unit_id,forum_id,topic_id,post_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    return d2ldata.Post(_get(route,uc,**kwargs))

def get_discussion_post_approval_status(uc,org_unit_id,forum_id,topic_id,post_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}/Approval'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    return d2ldata.ApprovalData(_get(route,uc,**kwargs))

def get_discussion_post_flag_status(uc,org_unit_id,forum_id,topic_id,post_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}/Flag'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    return d2ldata.FlagData(_get(route,uc,**kwargs))

def get_discussion_post_rating(uc,org_unit_id,forum_id,topic_id,post_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}/Rating'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    return d2ldata.RatingData(_get(route,uc,**kwargs))

def get_discussion_my_post_rating(uc,org_unit_id,forum_id,topic_id,post_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}/Rating/MyRating'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    return d2ldata.UserRatingData(_get(route,uc,**kwargs))

def get_discussion_post_read_status(uc,org_unit_id,forum_id,topic_id,post_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}/ReadStatus'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    return d2ldata.ReadStatusData(_get(route,uc,**kwargs))

def create_discussion_post(uc,org_unit_id,forum_id,topic_id,new_post,d2l_file_list=None,ver='1.0',**kwargs):
    if not isinstance(new_post, d2ldata.CreatePostData):
        raise TypeError('New post must implement d2lvalence.data.CreatePostData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/'.format(ver,org_unit_id,forum_id,topic_id)

    if not d2l_file_list:
        kwargs.setdefault('data',new_post.as_json())
        kwargs.setdefault('headers',{})
        kwargs['headers'].update({'Content-Type':'application/json'})
        ret = _post(route,uc,**kwargs)

    else:
        boundary = uuid.uuid4().hex
        pdescr = '--{0}\r\nContent-Type: application/json\r\n\r\n{1}\r\n'.format(boundary,new_post.as_json()).encode(encoding='utf-8')
        pbotbound = '\r\n--{0}--'.format(boundary).encode(encoding='utf-8')
        pfileparts = b''
        for i in range(len(d2l_file_list)):
            f = d2l_file_list[i]
            if isinstance(f, d2ldata.D2LFile):
                f.Stream.seek(0)
                fdata = f.Stream.read()
                f.Stream.seek(0)
                pfileparts = pfileparts + '\r\n--{0}\r\nContent-Disposition: form-data; name="{1}"; filename="{2}"\r\nContent-Type: {3}\r\n\r\n'.format(boundary,'file '+str(i),f.Name,f.ContentType).encode(encoding='utf-8') + fdata

        payload = pdescr + pfileparts + pbotbound

        ctype_header = {'Content-Type': 'multipart/mixed;boundary='+boundary}

        #populate the default state of the passed in kwargs that we care about
        kwargs.setdefault('auth',uc)
        kwargs.setdefault('data',payload)
        kwargs.setdefault('files',None)
        kwargs.setdefault('params',None)
        kwargs.setdefault('headers',None)
        kwargs.setdefault('verify',True)
        d = None
        if 'd2ldebug' in kwargs:
            d = kwargs['d2ldebug']
            del kwargs['d2ldebug']

        s = requests.Session()
        # set the default session values
        s.auth = kwargs['auth']
        s.verify = kwargs['verify']
        if kwargs['headers']:
            s.headers.update(kwargs['headers'])
            if kwargs['params']:
                s.params.update(kwargs['params'])

        # Build PreppedRequest
        p = requests.Request('POST',
                             uc.scheme + '://' + uc.host + route,
                             data = kwargs['data'],
                             auth = s.auth,
                             headers = s.headers,
                             params = s.params).prepare()

        # overlay the multipart content type header
        p.headers.update(ctype_header)
        if d:
            d.add_request(p)
        r = s.send(p)
        ret = _fetch_content(r,debug=d)

    return d2ldata.Post(ret)

def update_discussion_post(uc,org_unit_id,forum_id,topic_id,post_id,updated_post,ver='1.0'):
    if not isinstance(updated_post, d2ldata.UpdatePostData):
        raise TypeError('Updated post most implement d2lvalence.data.UpdatePostData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    kwargs.setdefault('data',updated_post.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    r = _put(route,uc,**kwargs)
    return d2ldata.Post(r)

def set_discussion_post_approval_status(uc,org_unit_id,forum_id,topic_id,post_id,approval_status,ver='1.0',**kwargs):
    if not isinstance(approval_status, d2ldata.ApprovalData):
        raise TypeError('Approval status must implement d2lvalence.data.ApprovalData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}/Approval'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    kwargs.setdefault('data',approval_status.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    r = _put(route,uc,**kwargs)
    return d2ldata.ApprovalData(r)

def set_discussion_post_flag_status(uc,org_unit_id,forum_id,topic_id,post_id,flag_status,ver='1.0',**kwargs):
    if not isinstance(flag_status, d2ldata.FlagData):
        raise TypeError('Approval status must implement d2lvalence.data.FlagData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}/Flag'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    kwargs.setdefault('data',flag_status.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    r = _put(route,uc,**kwargs)
    return d2ldata.FlagData(r)

def set_discussion_post_my_rating(uc,org_unit_id,forum_id,topic_id,post_id,my_rating,ver='1.0',**kwargs):
    if not isinstance(my_rating, d2ldata.UserRatingData):
        raise TypeError('My rating must implement d2lvalence.data.UserRatingData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}/Rating/MyRating'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    kwargs.setdefault('data',my_rating.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    r = _put(route,uc,**kwargs)
    return d2ldata.UserRatingData(r)

def set_discussion_post_read_status(uc,org_unit_id,forum_id,topic_id,post_id,read_status,ver='1.0',**kwargs):
    if not isinstance(read_status,d2ldata.ReadStatusData):
        raise TypeError('Read status must implement d2lvalence.data.ReadStatusData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/le/{0}/{1}/discussions/forums/{2}/topics/{3}/posts/{4}/ReadStatus'.format(ver,org_unit_id,forum_id,topic_id,post_id)
    kwargs.setdefault('data',read_status.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    r = _put(route,uc,**kwargs)
    return d2ldata.ReadStatusData(r)


## News routes
def get_my_feed(uc,since=None,until=None,ver='1.0',**kwargs):
    route = '/d2l/api/lp/{0}/feed/'.format(ver)
    kwargs.setdefault('params',{})
    if since:
        kwargs['params'].update({'since':since})
    if until:
        kwargs['params'].update({'until':until})
    return _get(route,uc,**kwargs)

def delete_news_item_for_orgunit(uc,org_unit_id,news_item_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/news/{2}'.format(ver,org_unit_id,news_item_id)
    return _delete(route,uc,**kwargs)

def delete_attachment_for_news_item_in_orgunit(uc,org_unit_id,news_item_id,attachment_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/news/{2}/attachments/{3}'.format(ver,org_unit_id,news_item_id,attachment_id)
    return _delete(route,uc,**kwargs)

def get_news_for_orgunit(uc,org_unit_id,since=None,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/news/'.format(ver,org_unit_id)
    kwargs.setdefault('params',{})
    if since:
        kwargs['params'].update({'since':since})
    return _get(route,uc,**kwargs)

def get_news_item_for_orgunit(uc,org_unit_id,news_item_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/news/{2}'.format(ver,org_unit_id,news_item_id)
    return d2ldata.NewsItem(_get(route,uc,**kwargs))

def get_news_item_attachment_for_orgunit(uc,org_unit_id,news_item_id,file_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/news/{2}/attachments/{3}'.format(ver,org_unit_id,news_item_id,file_id)
    return _get(route,uc,**kwargs)


def dismiss_news_item_for_orgunit(uc,org_unit_id,news_item_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/news/{2}/dismiss'.format(ver,org_unit_id,news_item_id)
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Length':'0'})
    return _post(route,uc,**kwargs)

def restore_news_item_for_orgunit(uc,org_unit_id,news_item_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/news/{2}/restore'.format(ver,org_unit_id,news_item_id)
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Length':'0'})
    return _post(route,uc,**kwargs)

def create_news_item_for_orgunit(uc,org_unit_id,news_item_data,d2l_file_list=None,ver='1.0',**kwargs):
    if not isinstance(news_item_data, d2ldata.NewsItemData):
        raise TypeError('New news item must implement d2lvalence.data.NewsItemData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/le/{0}/{1}/news/'.format(ver,org_unit_id)

    boundary = uuid.uuid4().hex
    pdescr = '--{0}\r\nContent-Type: application/json\r\n\r\n{1}\r\n'.format(boundary,news_item_data.as_json()).encode(encoding='utf-8')
    pbotbound = '\r\n--{0}--'.format(boundary).encode(encoding='utf-8')
    if not d2l_file_list:
        payload = pdescr + pbotbound
    else:
        pfileparts = b''
        for i in range(len(d2l_file_list)):
            f = d2l_file_list[i]
            if isinstance(f, d2ldata.D2LFile):
                f.Stream.seek(0)
                fdata = f.Stream.read()
                f.Stream.seek(0)
                pfileparts = pfileparts + '\r\n--{0}\r\nContent-Disposition: form-data; name="{1}"; filename="{2}"\r\nContent-Type: {3}\r\n\r\n'.format(boundary,'file '+str(i),f.Name,f.ContentType).encode(encoding='utf-8') + fdata
        payload = pdescr + pfileparts + pbotbound

    ctype_header = {'Content-Type':'multipart/mixed;boundary='+boundary}

    # populate the default state of the passed in kwargs that we care about
    kwargs.setdefault('auth',uc)
    kwargs.setdefault('data',payload)
    kwargs.setdefault('files',None)
    kwargs.setdefault('params',None)
    kwargs.setdefault('headers',None)
    kwargs.setdefault('verify',True)
    d = None
    if 'd2ldebug' in kwargs:
        d = kwargs['d2ldebug']
        del kwargs['d2ldebug']

    s = requests.Session()
    # set the session default values
    s.auth = kwargs['auth']
    s.verify = kwargs['verify']
    if kwargs['headers']:
        s.headers.update(kwargs['headers'])
    if kwargs['params']:
        s.params.update(kwargs['params'])

    # Build PreppedRequest
    p = requests.Request('POST',
                         uc.scheme + '://' + uc.host + route,
                         data = kwargs['data'],
                         auth = s.auth,
                         headers = s.headers,
                         params = s.params).prepare()

    # overlay the multipart content type header
    p.headers.update(ctype_header)
    if d:
        d.add_request(p)
    r = s.send(p)
    return _fetch_content(r,debug=d)

def create_attachment_for_newsitem(uc,org_unit_id,news_item_id,d2l_file,ver='1.0',**kwargs):
    if not isinstance(d2l_file, d2ldata.D2LFile):
        raise TypeError('File must implement d2lvalence.data.D2LFile').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/le/{0}/{1}/news/{2}/attachments/'.format(ver,org_unit_id,news_item_id)

    boundary = uuid.uuid4().hex
    f = d2l_file
    f.Stream.seek(0)
    fdata = f.Stream.read()
    f.Stream.seek(0)

    pdescr = '--{0}\r\nContent-Disposition: form-data; name="file"; filename="{1}"\r\nContent-Type: {2}\r\n\r\n'.format(boundary,f.Name,f.ContentType).encode(encoding='utf-8')
    pbotbound = '\r\n--{0}--'.format(boundary).encode(encoding='utf-8')

    payload = pdescr + fdata + pbotbound

    ctype_header = {'Content-Type':'multipart/form-data,boundary='+boundary}

    # populate the default state of the passed in kwargs that we care about
    kwargs.setdefault('auth',uc)
    kwargs.setdefault('data',payload)
    kwargs.setdefault('files',None)
    kwargs.setdefault('params',None)
    kwargs.setdefault('headers',None)
    kwargs.setdefault('verify',True)
    d = None
    if 'd2ldebug' in kwargs:
        d = kwargs['d2ldebug']
        del kwargs['d2ldebug']

    s = requests.Session()
    # set the session default values
    s.auth = kwargs['auth']
    s.verify = kwargs['verify']
    if kwargs['headers']:
        s.headers.update(kwargs['headers'])
    if kwargs['params']:
        s.params.update(kwargs['params'])

    # Build PreppedRequest
    p = requests.Request('POST',
                         uc.scheme + '://' + uc.host + route,
                         data = kwargs['data'],
                         auth = s.auth,
                         headers = s.headers,
                         params = s.params).prepare()

    # overlay the multipart content type header
    p.headers.update(ctype_header)
    if d:
        d.add_request(p)
    r = s.send(p)
    return _fetch_content(r,debug=d)


## Calendar routes
def delete_calender_event_for_org(uc,org_unit_id,event_id,ver='1.1',**kwargs):
    route = '/d2l/api/le/{0}/{1}/calendar/event/{2}'.format(ver,org_unit_id,event_id)
    return _delete(route,uc,**kwargs)

def get_calendar_event_for_org(uc,org_unit_id,event_id,ver='1.1',**kwargs):
    route = '/d2l/api/le/{0}/{1}/calendar/event/{2}'.format(ver,org_unit_id,event_id)
    return _get(route,uc,**kwargs)

def get_all_calendar_events_for_org(uc,org_unit_id,associated_only=False,ver='1.1',**kwargs):
    route = '/d2l/api/le/{0}/{1}/calendar/events/'.format(ver,org_unit_id)
    kwargs.setdefault('params',{})
    if associated_only:
        kwargs['params'].update({'associatedEventsOnly':True})
    return _get(route,uc,**kwargs)

## Content routes
def delete_content_module(uc,org_unit_id,module_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/content/modules/{2}'.format(ver,org_unit_id,module_id)
    return _delete(route,uc,**kwargs)

def delete_content_topic(uc,org_unit_id,topic_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/content/topics/{2}'.format(ver,org_unit_id,topic_id)
    return _delete(route,uc,**kwargs)

def get_content_module(uc,org_unit_id,module_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/content/modules/{2}'.format(ver,org_unit_id,module_id)
    return d2ldata.ContentObjectModule(_get(route,uc,**kwargs))

def get_content_module_structure(uc,org_unit_id,module_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/content/modules/{2}/structure/'.format(ver,org_unit_id,module_id)
    r = _get(route,uc,**kwargs)
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

def get_content_root_modules(uc,org_unit_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/content/root/'.format(ver,org_unit_id)
    r = _get(route,uc,**kwargs)
    result = []
    for i in range(len(r)):
        result.append(d2ldata.ContentObjectModule(r[i]))
    return result

def get_content_topic(uc,org_unit_id,topic_id,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/content/topics/{2}'.format(ver,org_unit_id,topic_id)
    return d2ldata.ContentObjectTopic(_get(route,uc,**kwargs))

def create_content_new_module(uc,org_unit_id,module_id,new_module_data,ver='1.0',**kwargs):
    if not isinstance(new_module_data, d2ldata.ContentObjectModuleData):
        raise TypeError('New module data must implement d2lvalence.data.ContentObjectModuleData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/le/{0}/{1}/content/modules/{2}/structure/'.format(ver,org_unit_id,module_id)
    kwargs.setdefault('data',new_module_data.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    return _post(route,uc,**kwargs)

def create_content_new_topic_link(uc,org_unit_id,module_id,new_topic_data,ver='1.0',**kwargs):
    if not isinstance(new_topic_data, d2ldata.ContentObjectTopicData):
        raise TypeError('New module data must implement d2lvalence.data.ContentObjectTopicData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/le/{0}/{1}/content/modules/{2}/structure/'.format(ver,org_unit_id,module_id)
    kwargs.setdefault('data',new_topic_data.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    return _post(route,uc,**kwargs)

def create_content_new_topic_file(uc,org_unit_id,module_id,d2l_file,ver='1.0',**kwargs):
    route = '/d2l/api/le/{0}/{1}/content/modules/{2}/structure/'.format(ver,org_unit_id,module_id)
    return _simple_upload(route,uc,d2l_file,**kwargs)

def create_content_root_module(uc,org_unit_id,root_module_data,ver='1.0',**kwargs):
    if not isinstance(root_module_data, d2ldata.ContentObjectModuleData):
        raise TypeError('New module data must implement d2lvalence.data.ContentObjectModuleData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/le/{0}/{1}/content/root/'.format(ver,org_unit_id)
    kwargs.setdefault('data',root_module_data.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    return _post(route,uc,**kwargs)

def update_content_module(uc,org_unit_id,module_id,updated_module_data,ver='1.0',**kwargs):
    if not isinstance(updated_module_data, d2ldata.ContentObjectModuleData):
        raise TypeError('New module data must implement d2lvalence.data.ContentObjectModuleData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/le/{0}/{1}/content/modules/{2}'.format(ver,org_unit_id,module_id)
    kwargs.setdefault('data',updated_module_data.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    return _put(route,uc,**kwargs)

def update_content_topic(uc,org_unit_id,topic_id,updated_topic_data,ver='1.0',**kwargs):
    if not isinstance(updated_topic_data, d2ldata.ContentObjectTopicData):
        raise TypeError('New module data must implement d2lvalence.data.ContentObjectTopicData').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/le/{0}/{1}/content/topics/{2}'.format(ver,org_unit_id,topic_id)
    kwargs.setdefault('data',updated_topic_data.as_json())
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Type':'application/json'})
    return _put(route,uc,**kwargs)

# Learning Repository routes
def get_learning_objects_by_search(uc,cql_string,offset,count,repo_list,ver='1.0',**kwargs):
    route = '/d2l/api/lr/{0}/objects/search/'.format(ver)
    kwargs.setdefault('params',{})
    kwargs['params'].update({'query': cql_string,
                             'offset': offset,
                             'count': count,
                             'repositories': repo_list})
    r = _get(route,uc,**kwargs)
    result = None
    if ('ExecutionStatus' in r):
        result = d2ldata.LRWSSearchResultCollection(r)
        if (r['ExecutionStatus'] == 0) and ('Results' in r):
            t = []
            for i in range(len(r['Results'])):
                           t.append(d2ldata.LRWSSearchResult(r['Results'][i]))
            result.props['Results']=t

    return result

def get_learning_object(uc,object_id,ver='1.0',**kwargs):
    route = '/d2l/api/lr/{0}/objects/{1}/download/'.format(ver,object_id)
    return _get(route,uc,**kwargs)

def get_learning_object_link(uc,object_id,ver='1.0',**kwargs):
    route = '/d2l/api/lr/{0}/objects/{1}/link/'.format(ver,object_id)
    return d2ldata.LRWSObjectLink(_get(route,uc,**kwargs))

def get_learning_object_properties(uc,object_id,ver='1.0',**kwargs):
    route = '/d2l/api/lr/{0}/objects/{1}/properties/'.format(ver,object_id)
    return d2ldata.LRWSObjectProperties(_get(route,uc,**kwargs))

def get_learning_object_version(uc,object_id,object_ver,ver='1.0',**kwargs):
    route = '/d2l/api/lr/{0}/objects/{1}/{2}/download/'.format(ver,object_id,object_ver)
    return _get(route,uc,**kwargs)

def get_learning_object_link_version(uc,object_id,object_ver,ver='1.0',**kwargs):
    route = '/d2l/api/lr/{0}/objects/{1}/{2}/link/'.format(ver,object_id,object_ver)
    return d2ldata.LRWSObjectLink(_get(route,uc,**kwargs))

def get_learning_object_metadata_version(uc,object_id,object_ver,ver='1.0',**kwargs):
    route = '/d2l/api/lr/{0}/objects/{1}/{2}/metadata/'.format(ver,object_id,object_ver)
    return _get(route,uc,**kwargs)

def get_learning_object_properties_version(uc,object_id,object_ver,ver='1.0',**kwargs):
    route = '/d2l/api/lr/{0}/objects/{1}/{2}/properties/'.format(ver,object_id)
    return d2ldata.LRWSObjectProperties(_get(route,uc,**kwargs))

def delete_learning_object(uc,object_id,ver='1.0',**kwargs):
    route = '/d2l/api/lr/{0}/objects/{1}/delete/'.format(ver,object_id)
    return _post(route,uc,headers={'Content-Length':'0'})

def update_learning_object(uc,object_id,d2l_file,ver='1.0',**kwargs):
    if not isinstance(d2l_file, d2ldata.D2LFile):
        raise TypeError('File must implement d2lvalence.data.D2LFile').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/lr/{0}/objects/{1}/'.format(ver,object_id)
    kwargs.setdefault('files',{})
    kwargs['files'].update({'Resource': (d2l_file.Name, d2l_file.Stream)})
    r = _post(route,uc,**kwargs)
    return d2ldata.LRWSPublishResult(r)

def update_learning_object_properties(uc,object_id,new_props,ver='1.0',**kwargs):
    if not isinstance(new_props, d2ldata.LRWSObjectPropertiesInput):
        raise TypeError('New properties must implement d2lvalence.data.LRWSObjectPropertiesInput').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/lr/{0}/objects/{1}/properties/'.format(ver,object_id)
    kwargs.setdefault('data',new_props.as_json())
    return _post(route,uc,**kwargs)

def update_learning_object_properties_version(uc,object_id,object_ver,new_props,ver='1.0',**kwargs):
    if not isinstance(new_props, d2ldata.LRWSObjectPropertiesInput):
        raise TypeError('New properties must implement d2lvalence.data.LRWSObjectPropertiesInput').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/lr/{0}/objects/{1}/{2}/properties/'.format(ver,object_id,object_ver)
    kwargs.setdefault('data',new_props.as_json())
    return _post(route,uc,**kwargs)

def create_new_learning_object(uc,repo_id,d2l_file,ver='1.0',**kwargs):
    if not isinstance(d2l_file, d2ldata.D2LFile):
        raise TypeError('File must implement d2lvalence.data.D2LFile').with_traceback(sys.exc_info()[2])
    route = '/d2l/api/lr/{0}/objects/'.format(ver)
    kwargs.setdefault('files',{})
    kwargs.setdefault('params',{})
    kwargs['files'].update({'Resource': (d2l_file.Name, d2l_file.Stream)})
    kwargs['params'].update({'repositoryId': repo_id})
    r = _put(route,uc,**kwargs)
    return d2ldata.LRWSPublishResult(r)

## ePortfolio routes

# eP import/export

def get_ep_import_task_status(uc,import_task_id,ver='2.0',**kwargs):
    route = '/d2l/api/eP/{0}/import/{1}/status'.format(ver,import_task_id)
    return _get(route,uc,**kwargs)

def start_ep_import_task(uc,ep_import_package,user_id_list=None,import_with_details=False,ver='2.0',**kwargs):
    if not isinstance(ep_import_package, d2ldata.D2LFile):
        raise TypeError('eP import package must implement d2lvalence.data.D2LFile').with_traceback(sys.exc_info()[2])

    if import_with_details and (_str_to_num(ver) >= 2.2):
        route = '/d2l/api/eP/{0}/import/newwithdetails'.format(ver)
    else:
        route = '/d2l/api/eP/{0}/import/new'.format(ver)

    boundary = uuid.uuid4().hex
    pbotbound = '\r\n--{0}--'.format(boundary).encode(encoding='utf-8')

    puids = b''
    if user_id_list:
        for i in range(len(user_id_list)):
            puids = puids + '\r\n--{0}\r\nContent-Disposition: form-data; name="targetUsers"\r\nContent-Type: text/plain\r\n\r\n{1}'.format(boundary,str(user_id_list[i])).encode(encoding='utf-8')

    f = ep_import_package
    f.Stream.seek(0)
    fdata = f.Stream.read()
    f.Stream.seek(0)
    ppkg = '\r\n--{0}\r\nContent-Disposition: form-data; name="file"; filename="{1}"\r\nContent-Type: {2}\r\n\r\n'.format(boundary, f.Name, f.ContentType).encode(encoding='utf-8') + fdata

    payload = puids + ppkg + pbotbound

    ctype_header = {'Content-Type':'multipart/form-data; boundary='+boundary}

    kwargs.setdefault('auth',uc)
    kwargs.setdefault('data',payload)
    kwargs.setdefault('files',None)
    kwargs.setdefault('params',None)
    kwargs.setdefault('headers',None)
    kwargs.setdefault('verify',True)
    d = None
    if 'd2ldebug' in kwargs and not isinstance(kwargs['d2ldebug'], d2ldata.D2LDebugInfo):
        raise TypeError('If not None, debug info object must implement d2lvalence.data.D2LDebugInfo')
    elif 'd2ldebug' in kwargs:
        d = kwargs['d2ldebug']
        kwargs['d2ldebug'] = None
        del kwargs['d2ldebug']

    s = requests.Session()
    # set the default sesion values
    s.auth = kwargs['auth']
    s.verify = kwargs['verify']
    if kwargs['headers']:
        s.headers.update(kwargs['headers'])
    if kwargs['params']:
        s.params.update(kwargs['params'])

    # Build PreppedRequest
    p = requests.Request('POST',
                         uc.scheme + '://' + uc.host + route,
                         data = kwargs['data'],
                         auth = s.auth,
                         headers = s.headers,
                         params = s.params).prepare()

    # overlay the multipart content type header
    p.headers.update(ctype_header)
    if d:
        d.add_request(p)
    r = s.send(p)
    return _fetch_content(r,debug=d)

def start_ep_export_all_task(uc,ver='2.0',**kwargs):
    route = '/d2l/api/eP/{0}/export/new/all'.format(ver)
    kwargs.setdefault('data',None)
    kwargs.setdefault('headers',{})
    kwargs['headers'].update({'Content-Length':'0'})
    return _post(route,uc,**kwargs)

def start_ep_export_task(uc, object_id_list,
                         include_forms_items=False,
                         include_associated_reflections=False,
                         include_reflections_associations=False,
                         include_associated_items=False,
                         ver='2.0',
                         **kwargs):
    route = '/d2l/api/eP/{0}/export/new'.format(ver)

    kwargs.setdefault('params',{})
    kwargs.setdefault('headers',{})
    kwargs.setdefault('data',json.dumps(object_id_list))

    kwargs['headers'].update({'Content-Type':'application/json'})
    kwargs['params'].update({'include_forms_items':include_forms_items})
    if _str_to_num(ver) <= '2.0':
        kwargs['params'].update({'includeAssociatedReflections': include_associated_reflections,
                                 'includeReflectionsAssociations': include_reflections_associations})
    else:
        kwargs['params'].update({'include_associated_items': include_associated_items})

    return _post(route,uc,**kwargs)

def get_ep_export_task_status(uc,export_task_id,ver='2.0',**kwargs):
    route = '/d2l/api/eP/{0}/export/{1}/status'.format(ver,export_task_id)
    return _get(route,uc,**kwargs)

def get_ep_export_task_package(uc,export_task_id,ver='2.0',**kwargs):
    route = '/d2l/api/eP/{0}/export/{1}/package'.format(ver,export_task_id)
    return _get(route,uc,**kwargs)

## LTI routes

# LTI links

# LTI Tool providers

def get_lti_tool_providers_for_orgunit(uc,org_unit_id,ver='1.3',**kwargs):
    route = '/d2l/api/le/{0}/lti/tp/{1}/'.format(ver,org_unit_id)
    r = _get(route,uc,**kwargs)
    result = []
    for i in range(len(r)):
        result.append(d2ldata.LTIToolProviderData(r[i]))
    return result


def get_lti_tool_provider_info(uc,org_unit_id,tool_provider_id,ver='1.3',**kwargs):
    route = '/d2l/api/le/{0}/lti/tp/{1}/{2}'.format(ver,org_unit_id,tool_provider_id)
    return d2ldata.LTITooProviderData(_get(route,uc,**kwargs))
