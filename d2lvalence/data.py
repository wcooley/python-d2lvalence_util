# -*- coding: utf-8 -*-
# D2LValence package, data module.
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
:module: d2lvalence.data
:synopsis: Provides definitions and support for handling Valence data structures
"""
import copy
import io
import json

## Utility functions
# these get used by the various data structures to provide for more elegant and compact
# construction of properties on the structures
def _get_string_prop(p):
    def func(self):
        return str(self.props[p])
    return func
def _set_string_prop(p):
    def func(self,v):
        self.props[p] = str(v)
    return func

def _get_number_prop(p):
    def func(self):
        return int(self.props[p])
    return func
def _set_number_prop(p):
    def func(self,v):
        self.props[p] = int(v)
    return func

def _get_boolean_prop(p):
    def func(self):
        return bool(self.props[p])
    return func
def _set_boolean_prop(p):
    def func(self,v):
        self.props[p] = bool(v)
    return func

## Base class
class D2LStructure():
    """Basic D2L data structure to encapsulate a JSON structure passed back and
    forth through the Valence API.
    """
    def __init__(self,props_dict):
        """Construct a new structure object.

        :param props_dict:
            Dictionary used to create the initial contents of the structure.
        """
        self.props = {}
        self.props.update(props_dict)

    def __repr__(self):
        """Retrieve this structure's properties as a string. """
        return str(self.props)

    def as_json(self):
        """Retrieve this structure's properties as a JSON string suitable for
        passing where you'd need JSON data. """
        return json.dumps(self.props)

    def as_dict(self):
        """Retrieve a new dict that's a deep copy of this structure's properties. """
        return copy.deepcopy(self.props)

## Utility classes
class PagedResultSet(D2LStructure):
    """Structure used to wrap paged result sets sent back from the API.

    The structure contains two top-level properties:

        `PagingInfo` contains the page bookmark, and a boolean property indicating
            if there are more data pages (you can also test this last with the
            `has_more_items` predicate method.

        `Items` contains an array of the relevant data structures. In some
            cases, the service layer might create a PagedResultSet.Items array
            so that each entry in the array is an appropriate inheritor of
            D2LStructure. In other cases, the service layer merely passes the
            raw JSON array provided through the API into this property, so it's
            fetchable as an array of dictionaries.

    """
    def __init__(self,props_dict):
        D2LStructure.__init__(self,props_dict)

    def has_more_items(self):
        return self.PagingInfo['HasMoreItems']

    @property
    def PagingInfo(self):
        return self.props['PagingInfo']

    @property
    def Bookmark(self):
        return self.props['PagingInfo']['Bookmark']

    @property
    def HasMoreItems(self):
        return self.props['PagingInfo']['HasMoreItems']

    @property
    def Items(self):
        return self.props['Items']

class D2LFile(D2LStructure):
    """Basic data structure used by the various simple upload routes to pass up
    file data encoded as multipart/mixed.

    This structure contains two top-level properties, corresonding to the two
    parts in the multipart/mixed data body provided to the server to
    simple-upload a file:

        `DescriptorDict` contains the JSON data to contain the descriptive
            meta-data for the file. In the case of the Locker routes, this
            amounts to a `Description` and a `Name` property for example.

        `Stream` contains a standard Python `io.BufferedIOBase` byte stream
            implementation that can provide the raw bytes for the file data to
            upload.

    The structure also contains the `Name` and `ContentType` (mime content-type)
    top-level properties that will get used to form the HTTP header and
    part-header fields needed in the simple-upload request.
    """
    def __init__(self,props_dict):
        D2LStructure.__init__(self,props_dict)

    @property
    def Stream(self):
        return self.props['Stream']

    @Stream.setter
    def Stream(self,f):
        if not isinstance(f, io.BufferedIOBase ):
            raise TypeError('File must implement io.BufferedIOBase')
        else:
            self.props['Stream']=f

    @property
    def DescriptorDict(self):
        return self.props['DescriptorDict']

    @DescriptorDict.setter
    def DescriptorDict(self,d):
        self.props['DescriptorDict']=d

    Name = property(_get_string_prop('Name'),_set_string_prop('Name'))
    ContentType = property(_get_string_prop('ContentType'),_set_string_prop('ContentType'))


class D2LLockerFile(D2LFile):
    """ D2LFile inheritor for forming file structures specifically for uploading
    to lockers.
    """
    def __init__(self,props_dict):
        D2LFile.__init__(self,props_dict)
        if 'DescriptorDict' not in self.props:
            self.props['DescriptorDict']={}

    @property
    def Description(self):
        return self.props['DescriptorDict']['Description']

    @Description.setter
    def Description(self,s):
        self.props['DescriptorDict']['Description']=s

    @property
    def IsPublic(self):
        return self.props['DescriptorDict']['IsPublic']

    @IsPublic.setter
    def IsPublic(self,b):
        self.props['DescriptorDict']['IsPublic']=b

class D2LLORPackage(D2LFile):
    """D2LFile inheritor for forming SCORM file structures specifically for
    uploading SCORM packages to LOR repositories.
    """
    def __init__(self,props_dict):
        D2LFile.__init__(self,props_dict)
        self.props['DescriptorDict']={}

## API Properties concrete classes
class BulkSupportedVersionResponse(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Supported = property(_get_boolean_prop('Supported'))

    @property
    def Versions(self):
        return self.props['Versions']

class ApiVersion(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Version = property(_get_string_prop('Version'))
    ProductCode = property(_get_string_prop('ProductCode'))

class ProductVersions(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    ProductCode = property(_get_string_prop('ProductCode'))
    LatestVersion = property(_get_string_prop('LatestVersion'))

    @property
    def SupportedVersions(self):
        return self.props['SupportedVersions']

class SupportedVersion(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Supported = property(_get_boolean_prop('Supported'))
    LatestVersion = property(_get_string_prop('LatestVersion'))

class SupportedVersionRequest(D2LStructure):
    def __init__(self,productCode,version):
        self.props = {'ProductCode':productCode, 'Version':version}

    ProductCode = property(_get_string_prop('ProductCode'), _set_string_prop('ProductCode'))
    Version = property(_get_string_prop('Version'), _set_string_prop('Version'))

## User concrete classes
class User(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Identifier = property(_get_string_prop('Identifier'))
    DisplayName = property(_get_string_prop('DisplayName'))
    EmailAddress = property(_get_string_prop('EmailAddress'))
    OrgDefinedId = property(_get_string_prop('OrgDefinedId'))
    ProfileBadgeUrl = property(_get_string_prop('ProfileBadgeUrl'))
    ProfileIdentifier = property(_get_string_prop('ProfileIdentifier'))

class CreateUserData(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    @staticmethod
    def fashion_CreateUserData(org_defined_id='',
                               first_name='',
                               middle_name='',
                               last_name='',
                               external_email='',
                               user_name='',
                               role_id=78,
                               is_active=False,
                               send_creation_email=False):
        cud = {'OrgDefinedId': org_defined_id,
               'FirstName': first_name,
               'MiddleName': middle_name,
               'LastName': last_name,
               'ExternalEmail': external_email,
               'UserName': user_name,
               'RoleId': role_id,
               'IsActive': is_active,
               'SendCreationEmail': send_creation_email }
        return CreateUserData(cud)

    OrgDefinedId = property(_get_string_prop('OrgDefinedId'),_set_string_prop('OrgDefinedId'))
    FirstName = property(_get_string_prop('FirstName'), _set_string_prop('FirstName'))
    MiddleName = property(_get_string_prop('MiddleName'), _set_string_prop('MiddleName'))
    LastName = property(_get_string_prop('LastName'), _set_string_prop('LastName'))
    ExternalEmail = property(_get_string_prop('ExternalEmail'), _set_string_prop('ExternalEmail'))
    UserName = property(_get_string_prop('UserName'), _set_string_prop('UserName'))
    RoleId = property(_get_number_prop('RoleId'), _set_number_prop('RoleId'))
    IsActive = property(_get_boolean_prop('IsActive'), _set_boolean_prop('IsActive'))
    SendCreationEmail = property(_get_boolean_prop('SendCreationEmail'), _set_boolean_prop('IsActive'))

class UpdateUserData(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    @staticmethod
    def fashion_UpdateUserData(org_defined_id='',
                               first_name='',
                               middle_name='',
                               last_name='',
                               external_email='',
                               user_name='',
                               is_active=False):
        cud = { 'OrgDefinedId': org_defined_id,
                'FirstName': first_name,
                'MiddleName': middle_name,
                'LastName': last_name,
                'ExternalEmail': external_email,
                'UserName': user_name,
                'Activation': { 'IsActive': is_active }
            }
        return UpdateUserData(cud)

    OrgDefinedId = property(_get_string_prop('OrgDefinedId'),_set_string_prop('OrgDefinedId'))
    FirstName = property(_get_string_prop('FirstName'), _set_string_prop('FirstName'))
    MiddleName = property(_get_string_prop('MiddleName'), _set_string_prop('MiddleName'))
    LastName = property(_get_string_prop('LastName'), _set_string_prop('LastName'))
    ExternalEmail = property(_get_string_prop('ExternalEmail'), _set_string_prop('ExternalEmail'))
    UserName = property(_get_string_prop('UserName'), _set_string_prop('UserName'))

    @property
    def Activation(self):
        return self.props['Activation']

    @Activation.setter
    def Activation(self,new_activation):
        self.props['Activation'] = new_activation

    @property
    def IsActive(self):
        return self.props['Activation']['IsActive']

    @IsActive.setter
    def IsActive(self,new_activation_status):
        self.props['Activation']['IsActive'] = bool(new_activation_status)

class UserData(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    OrgId = property(_get_number_prop('OrgId'))
    UserId = property(_get_number_prop('UserId'))
    FirstName = property(_get_string_prop('FirstName'))
    MiddleName = property(_get_string_prop('MiddleName'))
    LastName = property(_get_string_prop('LastName'))
    UserName = property(_get_string_prop('UserName'))
    ExternalEmail = property(_get_string_prop('ExternalEmail'))
    OrgDefinedId = property(_get_string_prop('OrgDefinedId'))
    UniqueIdentifier = property(_get_string_prop('UniqueIdentifier'))

    @property
    def Activation(self):
        return self.props['Activation']

    @property
    def IsActive(self):
        return self.props['Activation']['IsActive']

class WhoAmIUser(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Identifier = property(_get_string_prop('Identifier'))
    FirstName = property(_get_string_prop('FirstName'))
    LastName = property(_get_string_prop('LastName'))
    UniqueName = property(_get_string_prop('UniqueName'))
    ProfileIdentifier = property(_get_string_prop('ProfileIdentifier'))

class UserProfile(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Nickname = property(_get_string_prop('Nickname'), _set_string_prop('Nickname'))
    HomeTown = property(_get_string_prop('HomeTown'), _set_string_prop('HomeTown'))
    Email = property(_get_string_prop('Email'), _set_string_prop('Email'))
    HomePage = property(_get_string_prop('HomePage'), _set_string_prop('HomePage'))
    HomePhone = property(_get_string_prop('HomePhone'), _set_string_prop('HomePhone'))
    BusinessPhone = property(_get_string_prop('BusinessPhone'), _set_string_prop('BusinessPhone'))
    MobilePhone = property(_get_string_prop('MobilePhone'), _set_string_prop('MobilePhone'))
    FaxNumber = property(_get_string_prop('FaxNumber'), _set_string_prop('FaxNumber'))
    Address1 = property(_get_string_prop('Address1'), _set_string_prop('Address1'))
    Address2 = property(_get_string_prop('Address2'), _set_string_prop('Address2'))
    City = property(_get_string_prop('City'), _set_string_prop('City'))
    Province = property(_get_string_prop('Province'), _set_string_prop('Province'))
    PostalCode = property(_get_string_prop('PostalCode'), _set_string_prop('PostalCode'))
    Country = property(_get_string_prop('Country'), _set_string_prop('Country'))
    Company = property(_get_string_prop('Company'), _set_string_prop('Company'))
    JobTitle = property(_get_string_prop('JobTitle'), _set_string_prop('JobTitle'))
    HighSchool = property(_get_string_prop('HighSchool'), _set_string_prop('HighSchool'))
    University = property(_get_string_prop('University'), _set_string_prop('University'))
    Hobbies = property(_get_string_prop('Hobbies'), _set_string_prop('Hobbies'))
    FavMusic = property(_get_string_prop('FavMusic'), _set_string_prop('FavMusic'))
    FavTVShows = property(_get_string_prop('FavTVShows'), _set_string_prop('FavTVShows'))
    FavMovies = property(_get_string_prop('FavMovies'), _set_string_prop('FavMovies'))
    FavBooks = property(_get_string_prop('FavBooks'), _set_string_prop('FavBooks'))
    FavQuotations = property(_get_string_prop('FavQuotations'), _set_string_prop('FavQuotations'))
    FavWebSites = property(_get_string_prop('FavWebSites'), _set_string_prop('FavWebSites'))
    FutureGoals = property(_get_string_prop('FutureGoals'), _set_string_prop('FutureGoals'))
    FavMemory = property(_get_string_prop('FavMemory'), _set_string_prop('FavMemory'))

    @property
    def Birthday(self):
        return self.props['Birthday']

    @Birthday.setter
    def Birthday(self, new_birthday):
        self.props['Birthday'] = new_birthday

    def update_birthday(self, new_month, new_day):
        self.props['Birthday'] = {'Month': int(new_month), 'Day': int(new_day)}

    @property
    def BirthdayMonth(self):
        return self.props['Birthday']['Month']

    @BirthdayMonth.setter
    def BirthdayMonth(self,new_birthdaymonth):
        self.props['Birthday']['Month'] = new_birthdaymonth

    @property
    def BirthdayDay(self):
        return self.props['Birthday']['Day']

    @BirthdayMonth.setter
    def BirthdayDay(self,new_birthdayday):
        self.props['Birthday']['Day'] = new_birthdayday

    @property
    def SocialMediaUrls(self):
        return self.props['SocialMediaUrls']

    @SocialMediaUrls.setter
    def SocialMediaUrls(self, new_socialmediaurl_list):
        """Replace the SocialMediaUrls block with an entierly new array of
        social media URL dicts."""
        self.props['SocialMediaUrls'] = new_socialmediaurl_list

    def find_social_media_url(self, name):
        result = []
        for i in range(len(self.props['SocialMediaUrls'])):
            if name in self.props['SocialMediaUrls'][i]['Name']:
                result.append(self.props['SocialMediaUrls'][i])
        return result

    def add_social_media_url(self, name='', url=''):
        """Append a new social media Name/URL pair to the list. """
        self.props['SocialMediaUrls'].append({'Name': str(name), 'Url': str(url)})

    def remove_social_media_url_by_name(self, name):
        """Remove all social media entries from the list that match the given
        name. """
        for i in range(len(self.props['SocialMediaUrls'])):
            if name in self.props['SocialMediaUrls'][i]['Name']:
                del self.props['SocialMediaUrls'][i]

    def remove_social_media_url_by_url(self, url):
        """Remove all social media entries from the list that match the given
        URL. """
        for i in range(len(self.props['SocialMediaUrls'])):
            if url in self.props['SocialMediaUrls'][i]['Url']:
                del self.props['SocialMediaUrls'][i]

    def update_social_media_url_by_name(self, name, url):
        """Find all entries matching name, and update their URL as provided."""
        for i in range(len(self.props['SocialMediaUrls'])):
            if name in self.props['SocialMediaUrls'][i]['Name']:
                self.props['SocialMediaUrls'][i]['Url'] = str(url)

    def update_social_media_url_by_url(self, name, url):
        """Find all entries matching the URL, and update their names as
        provided."""
        for i in range(len(self.props['SocialMediaUrls'])):
            if url in self.props['SocialMediaUrls'][i]['Urls']:
                self.props['SocialMediaUrls'][i]['Name'] = str(name)

class Role(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Identifier = property(_get_string_prop('Identifier'))
    DisplayName = property(_get_string_prop('DisplayName'))
    Code = property(_get_string_prop('Code'))

## Org unit structure concrete classes
class OrgUnitType(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Id = property(_get_number_prop('Id'))
    Code = property(_get_string_prop('Code'))
    Name = property(_get_string_prop('Name'))
    Description = property(_get_string_prop('Description'))
    SortOrder = property(_get_number_prop('SortOrder'))
    CanEdit = property(_get_boolean_prop('CanEdit'))
    CanDelete = property(_get_boolean_prop('CanDelete'))

class OrgUnitTypeInfo(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Id = property(_get_number_prop('Id'))
    Code = property(_get_string_prop('Code'))
    Name = property(_get_string_prop('Name'))

## Course offering concrete classes
class BasicOrgUnit(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Identifier = property(_get_string_prop('Identifier'))
    Name = property(_get_string_prop('Name'))
    Code = property(_get_string_prop('Code'))

class CourseOffering(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Name = property(_get_string_prop('Name'))
    Code = property(_get_string_prop('Code'))
    Identifier = property(_get_string_prop('Identifier'))
    IsActive = property(_get_boolean_prop('IsActive'))
    Path = property(_get_string_prop('Path'))
    StartDate = property(_get_string_prop('StartDate'))
    EndDate = property(_get_string_prop('EndDate'))

    @property
    def CourseTempate(self):
        return self.props['CourseTemplate']

    @property
    def Semester(self):
        return self.props['Semester']

    @property
    def Department(self):
        return self.props['Department']

class CourseOfferingInfo(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    @staticmethod
    def fashion_CourseOfferingInfo(name='',
                                   code='',
                                   start_date=None,
                                   end_date=None,
                                   is_active=False):
        coi = {'Name': name,
               'Code': code,
               'StartDate': start_date,
               'EndDate': end_date,
               'IsActive': is_active }
        return CourseOfferingInfo(coi)

    Name = property(_get_string_prop('Name'), _set_string_prop('Name'))
    Code = property(_get_string_prop('Code'), _set_string_prop('Code'))
    StartDate = property(_get_string_prop('StartDate'), _set_string_prop('StartDate'))
    EndDate = property(_get_string_prop('EndDate'), _set_string_prop('EndDate'))
    IsActive = property(_get_boolean_prop('IsActive'), _set_boolean_prop('IsActive'))

class CreateCourseOffering(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    @staticmethod
    def fashion_CreateCourseOffering(name='',
                                     code='',
                                     path='',
                                     course_template_id='',
                                     semester_id=None,
                                     start_date=None,
                                     end_date=None,
                                     locale_id=None,
                                     force_locale=False,
                                     show_address_book=False):

        cco = {'Name': name,
               'Code': code,
               'CourseTemplateId': course_template_id,
               'SemesterId': semester_id,
               'StartDate': start_date,
               'EndDate': end_date,
               'LocaleId': locale_id,
               'ForceLocale': force_locale,
               'ShowAddressBook': show_address_book }
        return CreateCourseOffering(cco)

    Name = property(_get_string_prop('Name'), _set_string_prop('Name'))
    Code = property(_get_string_prop('Code'), _set_string_prop('Code'))
    Path = property(_get_string_prop('Path'), _set_string_prop('Path'))
    CourseTemplateId = property(_get_number_prop('CourseTemplateId'), _set_number_prop('CourseTemplateId'))
    SemesterId = property(_get_number_prop('SemesterId'), _set_number_prop('SemesterId'))
    StartDate = property(_get_string_prop('StartDate'), _set_string_prop('StartDate'))
    EndDate = property(_get_string_prop('EndDate'), _set_string_prop('EndDate'))
    LocaleId = property(_get_number_prop('LocaleId'), _get_number_prop('LocaleId'))
    ForceLocale = property(_get_boolean_prop('ForceLocale'), _set_boolean_prop('ForceLocale'))
    ShowAddressBook = property(_get_boolean_prop('ShowAddressBook'), _set_boolean_prop('ShowAddressBook'))

class CourseTemplate(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Identifier = property(_get_string_prop('Identifier'))
    Code = property(_get_string_prop('Code'))
    Name = property(_get_string_prop('Name'))
    Path = property(_get_string_prop('Path'))

class CourseTemplateInfo(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    @staticmethod
    def fashion_CourseTemplateInfo(name='',
                                   code=''):
        cti = {'Name': name, 'Code': code }
        return CourseTemplateInfo(cti)

    Name = property(_get_string_prop('Name'), _set_string_prop('Name'))
    Code = property(_get_string_prop('Code'), _set_string_prop('Code'))

class CreateCourseTemplate(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    @staticmethod
    def fashion_CreateCourseTemplateInfo(name='',
                                         code='',
                                         path='',
                                         parent_org_unit_id_list=()):
        cct = {'Name': name, 'Code': code, 'Path': path, 'ParentOrgUnitIds': parent_org_unit_id_list}
        return CreateCourseTemplate(cct)

    Name = property(_get_string_prop('Name'), _set_string_prop('Name'))
    Code = property(_get_string_prop('Code'), _set_string_prop('Code'))
    Path = property(_get_string_prop('Path'), _set_string_prop('Path'))

    @property
    def ParentOrgUnitIds(self):
        return self.props['ParentOrgUnitIds']

    @ParentOrgUnitIds.setter
    def ParentOrgUnitIds(self,parent_org_unit_id_list):
        self.props['ParentOrgUnitIds'] = parent_org_unit_id_list

class CourseSchemaElement(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    IsNotAllowed = property(_get_boolean_prop('IsNotAllowed'))
    IsRequired = property(_get_boolean_prop('IsRequired'))

    @property
    def Type(self):
        return self.props['Type']


## Enrollment concrete classes
class ClasslistUser(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Identifier = property(_get_string_prop('Identifier'))
    ProfileIdentifier = property(_get_string_prop('ProfileIdentifier'))
    DisplayName = property(_get_string_prop('DisplayName'))
    UserName = property(_get_string_prop('UserName'))
    OrgDefinedId = property(_get_string_prop('OrgDefinedId'))
    Email = property(_get_string_prop('Email'))

class MyOrgUnitInfo(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    @property
    def OrgUnit(self):
        # return OrgUnitInfo(self.props['OrgUnit']
        return self.props['OrgUnit']

    @property
    def AccessInfo(self):
        return self.props['AccessInfo']

    @property
    def IsActive(self):
        return self.props['AccessInfo']['IsActive']

    @property
    def StartDate(self):
        return self.props['AccessInfo']['StartDate']

    @property
    def EndDate(self):
        return self.props['AccessInfo']['EndDate']


    @property
    def CanAccess(self):
        return self.props['AccessInfo']['EndDate']

class OrgUnitInfo(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Id = property(_get_number_prop('Id'))
    Name = property(_get_string_prop('Name'))
    Code = property(_get_string_prop('Code'))

    @property
    def Type(self):
        # return OrgUnitTypeInfo(self.props['Type'])
        return self.props['Type']

## Grades concrete classes
class GradeObject(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    # These two props should be read-only on every instance
    Id = property(_get_number_prop('Id'))
    GradeType = property(_get_string_prop('GradeType'))

    Name = property(_get_string_prop('Name'), _set_string_prop('Name'))
    ShortName = property(_get_string_prop('ShortName'), _set_string_prop('ShortName'))
    CategoryId = property(_get_number_prop('Category'), _set_string_prop('CategoryId'))

    @property
    def Description(self):
        return self.props['Description']

    def update_description(self, descr, is_html=False):
        t = 'Text'
        if is_html:
            t = 'HTML'
        self.props['Description'] = {'Content': descr, 'Type': t }

class GradeObjectNumeric(GradeObject):
    def __init__(self,json_dict):
        GradeObject.__init__(self,json_dict)
        self.props['GradeType'] = 'Numeric'

    MaxPoints = property(_get_number_prop('MaxPoints'), _set_number_prop('MaxPoints'))
    CanExceedMaxPoints = property(_get_boolean_prop('CanExceedMaxPoints'),
                                  _set_boolean_prop('CanExceedMaxPoints'))
    IsBonus = property(_get_boolean_prop('IsBonus'), _set_boolean_prop('IsBonus'))
    ExcludeFromFinalGradeCalculation = property(_get_boolean_prop('ExcludeFromFinalGradeCalculation'),
                                                _set_boolean_prop('ExcludeFromFinalGradeCalculation'))
    GradeSchemeId = property(_get_number_prop('GradeSchemeId'), _set_number_prop('GradeSchemeId'))

class GradeObjectPassFail(GradeObject):
    def __init__(self,json_dict):
        GradeObject.__init__(self,json_dict)
        self.props['GradeType'] = 'PassFail'

    MaxPoints = property(_get_number_prop('MaxPoints'), _set_number_prop('MaxPoints'))
    IsBonus = property(_get_boolean_prop('IsBonus'), _set_boolean_prop('IsBonus'))
    ExcludeFromFinalGradeCalculation = property(_get_boolean_prop('ExcludeFromFinalGradeCalculation'),
                                                _set_boolean_prop('ExcludeFromFinalGradeCalculation'))
    GradeSchemeId = property(_get_number_prop('GradeSchemeId'), _set_number_prop('GradeSchemeId'))

class GradeObjectSelectBox(GradeObject):
    def __init__(self,json_dict):
        GradeObject.__init__(self,json_dict)
        self.props['GradeType'] = 'SelectBox'

    MaxPoints = property(_get_number_prop('MaxPoints'), _set_number_prop('MaxPoints'))
    IsBonus = property(_get_boolean_prop('IsBonus'), _set_boolean_prop('IsBonus'))
    ExcludeFromFinalGradeCalculation = property(_get_boolean_prop('ExcludeFromFinalGradeCalculation'),
                                                _set_boolean_prop('ExcludeFromFinalGradeCalculation'))
    GradeSchemeId = property(_get_number_prop('GradeSchemeId'), _set_number_prop('GradeSchemeId'))

class GradeObjectText(GradeObject):
    def __init__(self,json_dict):
        GradeObject.__init__(self,json_dict)
        self.props['GradeType'] = 'Text'


class GradeValue(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    DisplayedGrade = property(_get_string_prop('DisplayedGrade'))
    GradeObjectIdentifier = property(_get_string_prop('GradeObjectIdentifier'))
    GradeObjectName = property(_get_string_prop('GradeObjectName'))
    GradeObjectType = property(_get_number_prop('GradeObjectType'))
    GradeObjectTypeName = property(_get_string_prop('GradeObjectTypeName'))

class GradeValueComputable(GradeValue):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    PointsNumerator = property(_get_number_prop('PointsNumerator'))
    PointsDenominator = property(_get_number_prop('PointsDenominator'))
    WeightedNumerator = property(_get_number_prop('WeightedNumerator'))
    WeightedDenominator = property(_get_number_prop('WeightedDenominator'))


## Locker concrete classes
class LockerItem(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Name = property(_get_string_prop('Name'))
    Description = property(_get_string_prop('Description'))
    Type = property(_get_number_prop('Type'))
    Size = property(_get_number_prop('Size'))
    LastModified = property(_get_string_prop('LastModified'))

class LockerFolder(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Name = property(_get_string_prop('Name'))

    @property
    def Contents(self):
        return self.props['Contents']

    def find_locker_item(self,name):
        result = []
        for i in range(len(self.props['Contents'])):
            if name in self.props['Contents'][i]['Name']:
                result.append(self.props['Contents'][i])
        return result

class GroupLocker(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    HasLocker = property(_get_boolean_prop('HasLocker'))

## Discussion fora concrete classes
class Forum(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    ForumId = property(_get_number_prop('ForumId'))
    StartDate = property(_get_string_prop('StartDate'))
    EndDate = property(_get_string_prop('EndDate'))
    PostStartDate = property(_get_string_prop('PostStartDate'))
    PostEndDate = property(_get_string_prop('PostEndDate'))
    Name = property(_get_string_prop('Name'))
    AllowAnonymous = property(_get_boolean_prop('AllowAnonymous'))
    IsLocked = property(_get_boolean_prop('IsLocked'))
    IsHidden = property(_get_boolean_prop('IsHidden'))
    RequiresApproval = property(_get_boolean_prop('RequiresApproval'))

    @property
    def Description(self):
        return self.props['Description']

class ForumData(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    @staticmethod
    def fashion_ForumData(name='',
                          text_descr='',
                          html_descr='',
                          start_date=None,
                          end_date=None,
                          post_start_date=None,
                          post_end_date=None,
                          allow_anonymous=False,
                          is_locked=False,
                          is_hidden=False,
                          requires_approval=False):
        fd = {'Name': name,
               'Description': {'Text': text_descr, 'HTML': html_descr },
               'StartDate': start_date, 'EndDate': end_date,
               'PostStartDate': post_start_date, 'PostEndDate': post_end_date,
               'AllowAnonymous': allow_anonymous,
               'IsLocked': is_locked,
               'IsHidden': is_hidden,
               'RequiresApproval': requires_approval }
        return ForumData(fd)

    Name = property(_get_string_prop('Name'), _set_string_prop('Name'))
    StartDate = property(_get_string_prop('StartDate'), _set_string_prop('StartDate'))
    EndDate = property(_get_string_prop('EndDate'), _set_string_prop('EndDate'))
    PostStartDate = property(_get_string_prop('PostStartDate'), _set_string_prop('PostStartDate'))
    PostEndDate = property(_get_string_prop('PostEndDate'), _set_string_prop('PostEndDate'))
    AllowAnonymous = property(_get_boolean_prop('AllowAnonymous'), _set_boolean_prop('AllowAnonymous'))
    IsLocked = property(_get_boolean_prop('IsLocked'), _set_boolean_prop('IsLocked'))
    IsHidden = property(_get_boolean_prop('IsHidden'), _set_boolean_prop('IsHidden'))
    RequiresApproval = property(_get_boolean_prop('RequiresApproval'), _set_boolean_prop('RequiresApproval'))

    @property
    def Description(self):
        return self.props['Description']

    def update_description(self, text_descr='', html_descr=''):
        self.props['Description'] = {'Text': text_descr, 'HTML': html_descr }

class ForumUpdateData(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    @staticmethod
    def fashion_ForumUpdateData(name='',
                                text_descr='',
                                html_descr='',
                                allow_anonymous=False,
                                is_locked=False,
                                is_hidden=False,
                                requires_approval=False):
        fud = {'Name': name,
               'Description': {'Text': text_descr, 'HTML': html_descr },
               'AllowAnonymous': allow_anonymous,
               'IsLocked': is_locked,
               'IsHidden': is_hidden,
               'RequiresApproval': requires_approval }
        return ForumUpdateData(fud)

    Name = property(_get_string_prop('Name'), _set_string_prop('Name'))
    AllowAnonymous = property(_get_boolean_prop('AllowAnonymous'), _set_boolean_prop('AllowAnonymous'))
    IsLocked = property(_get_boolean_prop('IsLocked'), _set_boolean_prop('IsLocked'))
    IsHidden = property(_get_boolean_prop('IsHidden'), _set_boolean_prop('IsHidden'))
    RequiresApproval = property(_get_boolean_prop('RequiresApproval'), _set_boolean_prop('RequiresApproval'))

    @property
    def Description(self):
        return self.props['Description']

    def update_description(self, text_descr='', html_descr=''):
        self.props['Description'] = {'Text': text_descr, 'HTML': html_descr }

class Topic(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    ForumId = property(_get_number_prop('ForumId'))
    TopicId = property(_get_number_prop('TopicId'))
    Name = property(_get_string_prop('Name'))
    StartDate = property(_get_string_prop('StartDate'))
    EndDate = property(_get_string_prop('EndDate'))
    UnlockStartDate = property(_get_string_prop('UnlockStartDate'))
    UnlockEndDate = property(_get_string_prop('UnlockEndDate'))
    IsLocked = property(_get_boolean_prop('IsLocked'))
    AllowAnonymousPosts = property(_get_boolean_prop('AllowAnonymousPosts'))
    RequiresApproval = property(_get_boolean_prop('RequiresApproval'))
    UnApprovedPostCount = property(_get_number_prop('UnApprovedPostCount'))
    PinnedPostCount = property(_get_number_prop('PinnedPostCount'))
    ScoringType = property(_get_string_prop('ScoringType'))
    IsAutoScore = property(_get_boolean_prop('IsAutoScore'))
    ScoreOutOf = property(_get_number_prop('ScoreOutOf'))
    IncludeNonScoredValues = property(_get_boolean_prop('IncludeNonScoredValues'))
    ScoredCount = property(_get_number_prop('ScoredCount'))
    RatingsSum = property(_get_number_prop('RatingsSum'))
    RatingsCount = property(_get_number_prop('RatingsCount'))
    IsHidden = property(_get_boolean_prop('IsHidden'))
    MustPostToParticipate = property(_get_boolean_prop('MustPostToParticipate'))

    @property
    def Description(self):
        return self.props['Description']

class CreateTopicData(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    @staticmethod
    def fashion_CreateTopicData(name='',
                                descr='', is_html=False,
                                allow_anonymous_posts=False,
                                start_date=None,
                                end_date=None,
                                is_hidden=False,
                                unlock_start_date=None,
                                unlock_end_date=None,
                                requires_approval=False,
                                score_out_of=None,
                                is_auto_score=False,
                                include_non_scored_values=False,
                                scoring_type=None,
                                is_locked=False,
                                must_post_to_participate=False):

        t = 'Text'
        if is_html:
            t = 'HTML'
        ctd = {'Name': name,
               'Description': {'Content': descr, 'Type': t},
               'AllowAnonymousPosts': allow_anonymous_posts,
               'StartDate': start_date,
               'EndDate': end_date,
               'IsHidden': is_hidden,
               'UnlockStartDate': unlock_start_date,
               'UnlockEndDate': unlock_end_date,
               'RequiresApproval': requires_approval,
               'ScoreOutOf': score_out_of,
               'IsAutoScore': is_auto_score,
               'IncludeNonScoredValues': include_non_scored_values,
               'ScoringType': scoring_type,
               'IsLocked': is_locked,
               'MustPostToParticipate': must_post_to_participate }
        return CreateTopicData(ctd)

    Name = property(_get_string_prop('Name'), _set_string_prop('Name'))
    AllowAnonymousPosts = property(_get_boolean_prop('AllowAnonymousPosts'), _set_boolean_prop('AllowAnonymousPosts'))
    StartDate = property(_get_string_prop('StartDate'), _set_string_prop('StartDate'))
    EndDate = property(_get_string_prop('EndDate'), _set_string_prop('EndDate'))
    IsHidden = property(_get_boolean_prop('IsHidden'), _set_boolean_prop('IsHidden'))
    UnlockStartDate = property(_get_string_prop('UnlockStartDate'), _set_string_prop('UnlockStartDate'))
    UnlockEndDate = property(_get_string_prop('UnlockEndDate'), _set_string_prop('UnlockEndDate'))
    RequiresApproval = property(_get_boolean_prop('RequiresApproval'), _set_boolean_prop('RequiresApproval'))
    ScoreOutOf = property(_get_number_prop('ScoreOutOf'), _set_number_prop('ScoreOutOf'))
    IsAutoScore = property(_get_boolean_prop('IsAutoScore'), _set_boolean_prop('IsAutoScore'))
    IncludeNonScoredValues = property(_get_boolean_prop('IncludeNonScoredValues'), _set_boolean_prop('IncludeNonScoredValues'))
    ScoringType = property(_get_string_prop('ScoringType'), _set_string_prop('ScoringType'))
    IsLocked = property(_get_boolean_prop('IsLocked'), _set_boolean_prop('IsLocked'))
    MustPostToParticipate = property(_get_boolean_prop('MustPostToParticipate'), _set_boolean_prop('MustPostToParticipate'))

    @property
    def Description(self):
        return self.props['Description']

    def update_description(self, descr, is_html=False):
        t = 'Text'
        if is_html:
            t = 'HTML'
        self.props['Description'] = {'Content': descr, 'Type': t }

class Post(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    ForumId = property(_get_number_prop('ForumId'))
    TopicId = property(_get_number_prop('TopicId'))
    PostId = property(_get_number_prop('PostId'))
    PostingUserId = property(_get_number_prop('PostingUserId'))
    ThreadId = property(_get_number_prop('ThreadId'))
    ParentPostId = property(_get_number_prop('ParentPostId'))
    Subject = property(_get_string_prop('Subject'))
    DatePosted = property(_get_string_prop('DatePosted'))
    IsAnonymous = property(_get_boolean_prop('IsAnonymous'))
    RequiresApproval = property(_get_boolean_prop('RequiresApproval'))
    IsDeleted = property(_get_boolean_prop('IsDeleted'))
    LastEditedDate = property(_get_string_prop('LastEditedDate'))
    LastEditedBy = property(_get_number_prop('LastEditedBy'))
    CanRate = property(_get_boolean_prop('CanRate'))

    @property
    def Message(self):
        return self.props['Message']

    def ReplyPostIds(self):
        return self.props['ReplyPostIds']

class CreatePostData(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    @staticmethod
    def fashion_CreatePostData(parent_post_id=None,
                               subject='',
                               message='', is_html=False,
                               is_anonymous=False):
        t = 'Text'
        if is_html:
            t = 'HTML'
        cpd = {'ParentPostId': parent_post_id,
                'Subject': subject,
                'Message': {'Content': message, 'Type': t},
                'IsAnonymous': is_anonymous }
        return CreatePostData(cpd)

    ParentPostId = property(_get_number_prop('ParentPostId'), _set_number_prop('ParentPostId'))
    Subject = property(_get_string_prop('Subject'), _set_string_prop('Subject'))
    IsAnonymous = property(_get_boolean_prop('IsAnonymous'), _set_boolean_prop('IsAnonymous'))

    @property
    def Message(self):
        return self.props['Message']

    def update_message(self, descr, is_html=False):
        t = 'Text'
        if is_html:
            t = 'HTML'
        self.props['Message'] = {'Content': descr, 'Type': t }

class UpdatePostData(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    @staticmethod
    def fashion_UpdatePostData(subject='',
                               message='', is_html=False):
        t = 'Text'
        if is_html:
            t = 'HTML'
        upd = {'Subject': subject,
               'Message': {'Content': message, 'Type': t} }
        return UpdatePostData(upd)

    Subject = property(_get_string_prop('Subject'), _set_string_prop('Subject'))

    @property
    def Message(self):
        return self.props['Message']

    def update_message(self, descr, is_html=False):
        t = 'Text'
        if is_html:
            t = 'HTML'
        self.props['Message'] = {'Content': descr, 'Type': t }


class GroupRestriction(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    @staticmethod
    def fashion_GroupRestriction(group_id):
        gr = { 'GroupRestriction': {'GroupId': group_id}}
        return GroupRestriction(gr)

    @property
    def GroupRestriction(self):
        return self.props['GroupRestriction']

    def update_group_restriction(self,group_id):
        self.props['GroupRestriction'] = {'GroupId':group_id}

class ApprovalData(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    @staticmethod
    def fashion_ApprovalData(is_approved=False):
        ad = {'IsApproved': is_approved}
        return ApprovalData(ad)

    IsApproved = property(_get_boolean_prop('IsApproved'), _set_boolean_prop('IsApproved'))

class FlagData(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    @staticmethod
    def fashion_FlagData(is_flagged=False):
        ad = {'IsFlagged': is_flagged}
        return FlagData(ad)

    IsFlagged = property(_get_boolean_prop('IsFlagged'), _set_boolean_prop('IsFlagged'))

class RatingData(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    CanRate = property(_get_boolean_prop('CanRate'))
    RatingsSum = property(_get_number_prop('RatingsSum'))
    RatingsCount = property(_get_number_prop('RatingsCount'))
    RatingsAverage = property(_get_number_prop('RatingsAverage'))

    @property
    def UserRating(self):
        return self.props['UserRating']

    @property
    def Rating(self):
        return self.props['UserRating']['Rating']

class UserRatingData(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    @staticmethod
    def _choose_rating(rating):
        _ratings = ['one','two','three','four','five']
        r = None
        if isinstance( rating, str):
            if rating.lower() in _ratings:
                r = _ratings.index(rating.lower()) + 1
            else:
                raise ValueError('Bad rating: must be in ' + str(_ratings) + ' or equivalent integer value')
        else:
            try:
                r = int(rating)
                r = 1 if r < 1 else 5 if r > 5 else r
            except TypeError:
                raise ValueError('Bad rating: must be in ' + str(_ratings) + ' or equivalent integer value')
        return r

    @staticmethod
    def fashion_UserRatingData(value):
        r = UserRatingData._choose_rating(value)
        return UserRatingData({'Rating': r})

    @property
    def Rating(self):
        return self.props['Rating']

    @Rating.setter
    def UserRating(self, value):
        r = _choose_rating(value)
        self.props['Rating'] = r


class ReadStatusData(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    @staticmethod
    def fashion_ReadStatusData(is_read=False):
        rsd = {'IsRead': is_read}
        return ReadStatusData(rsd)

    IsRead = property(_get_boolean_prop('IsRead'), _set_boolean_prop('IsRead'))

## Content concrete classes
class ContentObjectModule(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    ModuleStartDate = property(_get_string_prop('ModuleStartDate'))
    ModuleEndDate = property(_get_string_prop('ModuleEndDate'))
    IsHidden = property(_get_boolean_prop('IsHidden'))
    IsLocked = property(_get_boolean_prop('IsLocked'))
    Id = property(_get_number_prop('Id'))
    Title = property(_get_string_prop('Title'))
    ShortTitle = property(_get_string_prop('ShortTitle'))
    Type = property(_get_number_prop('Type'))

    @property
    def Structure(self):
        return self.props['Structure']

class ContentObjectTopic(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    TopicType = property(_get_number_prop('TopicType'))
    Url = property(_get_string_prop('Url'))
    StartDate = property(_get_string_prop('StartDte'))
    EndDate = property(_get_string_prop('EndDate'))
    IsHidden = property(_get_boolean_prop('IsHidden'))
    IsLocked = property(_get_boolean_prop('IsLocked'))
    Id = property(_get_number_prop('Id'))
    Title = property(_get_string_prop('Title'))
    ShortTitle = property(_get_string_prop('ShortTitle'))
    Type = property(_get_number_prop('Type'))

class ContentObjectModuleData(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    @staticmethod
    def fashion_ContentObjectModuleData(module_start_date=None,
                                        module_end_date=None,
                                        is_hidden=False,
                                        is_locked=False,
                                        title='',
                                        short_title=''):
        comd = {'ModuleStartDate': module_start_date,
                'ModuleEndDate': module_end_date,
                'IsHidden': is_hidden,
                'IsLocked': is_locked,
                'Title': title,
                'ShortTitle': short_title,
                'Type': 0 }
        return ContentObjectModuleData(comd)

    ModuleStartDate = property(_get_string_prop('ModuleStartDate'),_set_string_prop('ModuleStartDate'))
    ModuleEndDate = property(_get_string_prop('ModuleEndDate'),_set_string_prop('ModuleEndDate'))
    IsHidden = property(_get_boolean_prop('IsHidden'),_set_boolean_prop('IsHidden'))
    IsLocked = property(_get_boolean_prop('IsLocked'),_set_boolean_prop('IsLocked'))
    Title = property(_get_string_prop('Title'),_set_string_prop('Title'))
    ShortTitle = property(_get_string_prop('ShortTitle'),_set_string_prop('ShortTitle'))
    Type = property(_get_number_prop('Type'))

class ContentObjectTopicData(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    @staticmethod
    def fashion_ContentObjectTopicData(topic_type='',
                                       url='',
                                       start_date=None,
                                       end_date=None,
                                       is_hidden=False,
                                       is_locked=False,
                                       title='',
                                       short_title=''):
        cotd = {'TopicType': topic_type,
                'Url': url,
                'StartDate': start_date,
                'EndDate': end_date,
                'IsHidden': is_hidden,
                'IsLocked': is_locked,
                'Title': title,
                'ShortTitle': short_title,
                'Type': 1 }
        return ContentObjectTopicData(cotd)

    TopicType = property(_get_number_prop('TopicType'),_set_number_prop('TopicType'))
    Url = property(_get_string_prop('Url'),_set_string_prop('Url'))
    StartDate = property(_get_string_prop('StartDte'),_set_string_prop('StartDate'))
    EndDate = property(_get_string_prop('EndDate'),_set_string_prop('EndDate'))
    IsHidden = property(_get_boolean_prop('IsHidden'),_set_boolean_prop('IsHidden'))
    IsLocked = property(_get_boolean_prop('IsLocked'),_set_boolean_prop('IsLocked'))
    Title = property(_get_string_prop('Title'),_set_string_prop('Title'))
    ShortTitle = property(_get_string_prop('ShortTitle'),_set_string_prop('ShortTitle'))
    Type = property(_get_number_prop('Type'),_set_number_prop('Type'))


## Learning repository concrete classes
class LRWSBaseResult(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    ExecutionMessage = property(_get_string_prop('ExecutionMessage'))
    ExecutionStatus = property(_get_number_prop('ExecutionStatus'))

class LRWSObjectProperties(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Description = property(_get_string_prop('Description'))
    ExecutionMessage = property(_get_string_prop('ExecutionMessage'))
    ExecutionStatus = property(_get_number_prop('ExecutionStatus'))
    HiddenFromSearchResults = property(_get_boolean_prop('HiddenFromSearchResults'))
    IdentId = property(_get_number_prop('IdentId'))
    OwnerId = property(_get_number_prop('OwnerId'))
    PublicallyAvailable = property(_get_boolean_prop('PublicallyAvailable'))
    RepositoryId = property(_get_number_prop('RepositoryId'))
    Status = property(_get_number_prop('Status'))
    Title = property(_get_string_prop('Title'))
    Type = property(_get_number_prop('Type'))
    URL = property(_get_string_prop('URL'))
    Version = property(_get_number_prop('Version'))

    @property
    def Keywords(self):
        return self.props['Keywords']

class LRWSObjectPropertiesInput(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Description = property(_get_string_prop('Description'),_set_string_prop('Description'))
    HiddenFromSearchResults = property(_get_boolean_prop('HiddenFromSearchResults'),_set_boolean_prop('HiddenFromSearchResults'))
    OwnerId = property(_get_number_prop('OwnerId'),_set_number_prop('OwnerId'))
    PublicallyAvailable = property(_get_boolean_prop('PublicallyAvailable'),_set_boolean_prop('PublicallyAvailable'))
    RepositoryId = property(_get_number_prop('RepositoryId'),_set_number_prop('RepositoryId'))
    Status = property(_get_number_prop('Status'),_set_number_prop('Status'))
    Title = property(_get_string_prop('Title'),_set_string_prop('Title'))

    @property
    def Keywords(self):
        return self.props['Keywords']

    @Keywords.setter
    def Keywords(self, new_keywords_list):
        self.props['Keywords'] = new_keywords_list


class LRWSObjectLink(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    ExecutionMessage = property(_get_string_prop('ExecutionMessage'))
    ExecutionStatus = property(_get_string_prop('ExecutionStatus'))
    URL = property(_get_string_prop('URL'))

class LRWSPublishResult(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    ExecutionMessage = property(_get_string_prop('ExecutionMessage'))
    ExecutionStatus = property(_get_string_prop('ExecutionStatus'))
    IdentId = property(_get_number_prop('IdentId'))
    Version = property(_get_number_prop('Version'))

class LRWSPublishStatusResult(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    PublishStatus = property(_get_number_prop('PublishStatus'))
    ErrorMessage = property(_get_string_prop('ErrorMessage'))
    LoUrl = property(_get_string_prop('LoUrl'))

class LRWSSearchResult(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    IdentId = property(_get_number_prop('IdentId'))
    RepositoryId = property(_get_number_prop('RepositoryId'))
    Version = property(_get_number_prop('Version'))

class LRWSSearchResultCollection(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    ExecutionMessage = property(_get_string_prop('ExecutionMessage'))
    ExecutionStatus = property(_get_string_prop('ExecutionStatus'))
    TotalResults = property(_get_number_prop('TotalResults'))

    @property
    def Results(self):
        return self.props['Results']

    def find_result_by_object_id(self,object_id):
        result = []
        for i in range(len(self.props['Results'])):
            if object_id in self.props['Results'][i]['IdentId']:
                result.append(LRWSSearchResult(self.props['Results'][i]))

        return result
