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
def get_string_prop(p):
    def func(self):
        return str(self.props[p])
    return func
def set_string_prop(p):
    def func(self,v):
        self.props[p] = str(v)
    return func

def get_number_prop(p):
    def func(self):
        return int(self.props[p])
    return func
def set_number_prop(p):
    def func(self,v):
        self.props[p] = int(v)
    return func

def get_boolean_prop(p):
    def func(self):
        return bool(self.props[p])
    return func
def set_boolean_prop(p):
    def func(self,v):
        self.props[p] = bool(v)
    return func

## Base class
class D2LStructure():
    def __init__(self,json_dict):
        self.props = {}
        self.props.update(json_dict)

    def __repr__(self):
        return str(self.props)

    def as_json(self):
        return json.dumps(self.props)

    def as_dict(self):
        return copy.deepcopy(self.props)

## Utility classes
class PagedResultSet(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

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
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

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

    Name = property(get_string_prop('Name'),set_string_prop('Name'))
    ContentType = property(get_string_prop('ContentType'),set_string_prop('ContentType'))


class D2LLockerFile(D2LFile):
    def __init__(self,json_dict):
        D2LFile.__init__(self,json_dict)

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


## API Properties concrete classes
class BulkSupportedVersionResponse(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Supported = property(get_boolean_prop('Supported'))

    @property
    def Versions(self):
        return self.props['Versions']

class ApiVersion(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Version = property(get_string_prop('Version'))
    ProductCode = property(get_string_prop('ProductCode'))

class ProductVersions(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    ProductCode = property(get_string_prop('ProductCode'))
    LatestVersion = property(get_string_prop('LatestVersion'))

    @property
    def SupportedVersions(self):
        return self.props['SupportedVersions']

class SupportedVersion(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Supported = property(get_boolean_prop('Supported'))
    LatestVersion = property(get_string_prop('LatestVersion'))

class SupportedVersionRequest(D2LStructure):
    def __init__(self,productCode,version):
        self.props = {'ProductCode':productCode, 'Version':version}

    ProductCode = property(get_string_prop('ProductCode'), set_string_prop('ProductCode'))
    Version = property(get_string_prop('Version'), set_string_prop('Version'))

## User concrete classes
class User(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Identifier = property(get_string_prop('Identifier'))
    DisplayName = property(get_string_prop('DisplayName'))
    EmailAddress = property(get_string_prop('EmailAddress'))
    OrgDefinedId = property(get_string_prop('OrgDefinedId'))
    ProfileBadgeUrl = property(get_string_prop('ProfileBadgeUrl'))
    ProfileIdentifier = property(get_string_prop('ProfileIdentifier'))

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

    OrgDefinedId = property(get_string_prop('OrgDefinedId'),set_string_prop('OrgDefinedId'))
    FirstName = property(get_string_prop('FirstName'), set_string_prop('FirstName'))
    MiddleName = property(get_string_prop('MiddleName'), set_string_prop('MiddleName'))
    LastName = property(get_string_prop('LastName'), set_string_prop('LastName'))
    ExternalEmail = property(get_string_prop('ExternalEmail'), set_string_prop('ExternalEmail'))
    UserName = property(get_string_prop('UserName'), set_string_prop('UserName'))
    RoleId = property(get_number_prop('RoleId'), set_number_prop('RoleId'))
    IsActive = property(get_boolean_prop('IsActive'), set_boolean_prop('IsActive'))
    SendCreationEmail = property(get_boolean_prop('SendCreationEmail'), set_boolean_prop('IsActive'))

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

    OrgDefinedId = property(get_string_prop('OrgDefinedId'),set_string_prop('OrgDefinedId'))
    FirstName = property(get_string_prop('FirstName'), set_string_prop('FirstName'))
    MiddleName = property(get_string_prop('MiddleName'), set_string_prop('MiddleName'))
    LastName = property(get_string_prop('LastName'), set_string_prop('LastName'))
    ExternalEmail = property(get_string_prop('ExternalEmail'), set_string_prop('ExternalEmail'))
    UserName = property(get_string_prop('UserName'), set_string_prop('UserName'))

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

    OrgId = property(get_number_prop('OrgId'))
    UserId = property(get_number_prop('UserId'))
    FirstName = property(get_string_prop('FirstName'))
    MiddleName = property(get_string_prop('MiddleName'))
    LastName = property(get_string_prop('LastName'))
    UserName = property(get_string_prop('UserName'))
    ExternalEmail = property(get_string_prop('ExternalEmail'))
    OrgDefinedId = property(get_string_prop('OrgDefinedId'))
    UniqueIdentifier = property(get_string_prop('UniqueIdentifier'))

    @property
    def Activation(self):
        return self.props['Activation']

    @property
    def IsActive(self):
        return self.props['Activation']['IsActive']

class WhoAmIUser(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Identifier = property(get_string_prop('Identifier'))
    FirstName = property(get_string_prop('FirstName'))
    LastName = property(get_string_prop('LastName'))
    UniqueName = property(get_string_prop('UniqueName'))
    ProfileIdentifier = property(get_string_prop('ProfileIdentifier'))

class UserProfile(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Nickname = property(get_string_prop('Nickname'), set_string_prop('Nickname'))
    HomeTown = property(get_string_prop('HomeTown'), set_string_prop('HomeTown'))
    Email = property(get_string_prop('Email'), set_string_prop('Email'))
    HomePage = property(get_string_prop('HomePage'), set_string_prop('HomePage'))
    HomePhone = property(get_string_prop('HomePhone'), set_string_prop('HomePhone'))
    BusinessPhone = property(get_string_prop('BusinessPhone'), set_string_prop('BusinessPhone'))
    MobilePhone = property(get_string_prop('MobilePhone'), set_string_prop('MobilePhone'))
    FaxNumber = property(get_string_prop('FaxNumber'), set_string_prop('FaxNumber'))
    Address1 = property(get_string_prop('Address1'), set_string_prop('Address1'))
    Address2 = property(get_string_prop('Address2'), set_string_prop('Address2'))
    City = property(get_string_prop('City'), set_string_prop('City'))
    Province = property(get_string_prop('Province'), set_string_prop('Province'))
    PostalCode = property(get_string_prop('PostalCode'), set_string_prop('PostalCode'))
    Country = property(get_string_prop('Country'), set_string_prop('Country'))
    Company = property(get_string_prop('Company'), set_string_prop('Company'))
    JobTitle = property(get_string_prop('JobTitle'), set_string_prop('JobTitle'))
    HighSchool = property(get_string_prop('HighSchool'), set_string_prop('HighSchool'))
    University = property(get_string_prop('University'), set_string_prop('University'))
    Hobbies = property(get_string_prop('Hobbies'), set_string_prop('Hobbies'))
    FavMusic = property(get_string_prop('FavMusic'), set_string_prop('FavMusic'))
    FavTVShows = property(get_string_prop('FavTVShows'), set_string_prop('FavTVShows'))
    FavMovies = property(get_string_prop('FavMovies'), set_string_prop('FavMovies'))
    FavBooks = property(get_string_prop('FavBooks'), set_string_prop('FavBooks'))
    FavQuotations = property(get_string_prop('FavQuotations'), set_string_prop('FavQuotations'))
    FavWebSites = property(get_string_prop('FavWebSites'), set_string_prop('FavWebSites'))
    FutureGoals = property(get_string_prop('FutureGoals'), set_string_prop('FutureGoals'))
    FavMemory = property(get_string_prop('FavMemory'), set_string_prop('FavMemory'))

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

    Identifier = property(get_string_prop('Identifier'))
    DisplayName = property(get_string_prop('DisplayName'))
    Code = property(get_string_prop('Code'))

## Org unit structure concrete classes
class OrgUnitType(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Id = property(get_number_prop('Id'))
    Code = property(get_string_prop('Code'))
    Name = property(get_string_prop('Name'))
    Description = property(get_string_prop('Description'))
    SortOrder = property(get_number_prop('SortOrder'))
    CanEdit = property(get_boolean_prop('CanEdit'))
    CanDelete = property(get_boolean_prop('CanDelete'))

class OrgUnitTypeInfo(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Id = property(get_number_prop('Id'))
    Code = property(get_string_prop('Code'))
    Name = property(get_string_prop('Name'))

## Enrollment concrete classes
class ClasslistUser(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Identifier = property(get_string_prop('Identifier'))
    ProfileIdentifier = property(get_string_prop('ProfileIdentifier'))
    DisplayName = property(get_string_prop('DisplayName'))
    UserName = property(get_string_prop('UserName'))
    OrgDefinedId = property(get_string_prop('OrgDefinedId'))
    Email = property(get_string_prop('Email'))

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

    Id = property(get_number_prop('Id'))
    Name = property(get_string_prop('Name'))
    Code = property(get_string_prop('Code'))

    @property
    def Type(self):
        # return OrgUnitTypeInfo(self.props['Type'])
        return self.props['Type']

## Grades concrete classes
class GradeObject(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    # These two props should be read-only on every instance
    Id = property(get_number_prop('Id'))
    GradeType = property(get_string_prop('GradeType'))

    Name = property(get_string_prop('Name'), set_string_prop('Name'))
    ShortName = property(get_string_prop('ShortName'), set_string_prop('ShortName'))
    CategoryId = property(get_number_prop('Category'), set_string_prop('CategoryId'))

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

    MaxPoints = property(get_number_prop('MaxPoints'), set_number_prop('MaxPoints'))
    CanExceedMaxPoints = property(get_boolean_prop('CanExceedMaxPoints'),
                                  set_boolean_prop('CanExceedMaxPoints'))
    IsBonus = property(get_boolean_prop('IsBonus'), set_boolean_prop('IsBonus'))
    ExcludeFromFinalGradeCalculation = property(get_boolean_prop('ExcludeFromFinalGradeCalculation'),
                                                set_boolean_prop('ExcludeFromFinalGradeCalculation'))
    GradeSchemeId = property(get_number_prop('GradeSchemeId'), set_number_prop('GradeSchemeId'))

class GradeObjectPassFail(GradeObject):
    def __init__(self,json_dict):
        GradeObject.__init__(self,json_dict)
        self.props['GradeType'] = 'PassFail'

    MaxPoints = property(get_number_prop('MaxPoints'), set_number_prop('MaxPoints'))
    IsBonus = property(get_boolean_prop('IsBonus'), set_boolean_prop('IsBonus'))
    ExcludeFromFinalGradeCalculation = property(get_boolean_prop('ExcludeFromFinalGradeCalculation'),
                                                set_boolean_prop('ExcludeFromFinalGradeCalculation'))
    GradeSchemeId = property(get_number_prop('GradeSchemeId'), set_number_prop('GradeSchemeId'))

class GradeObjectSelectBox(GradeObject):
    def __init__(self,json_dict):
        GradeObject.__init__(self,json_dict)
        self.props['GradeType'] = 'SelectBox'

    MaxPoints = property(get_number_prop('MaxPoints'), set_number_prop('MaxPoints'))
    IsBonus = property(get_boolean_prop('IsBonus'), set_boolean_prop('IsBonus'))
    ExcludeFromFinalGradeCalculation = property(get_boolean_prop('ExcludeFromFinalGradeCalculation'),
                                                set_boolean_prop('ExcludeFromFinalGradeCalculation'))
    GradeSchemeId = property(get_number_prop('GradeSchemeId'), set_number_prop('GradeSchemeId'))

class GradeObjectText(GradeObject):
    def __init__(self,json_dict):
        GradeObject.__init__(self,json_dict)
        self.props['GradeType'] = 'Text'


class GradeValue(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    DisplayedGrade = property(get_string_prop('DisplayedGrade'))
    GradeObjectIdentifier = property(get_string_prop('GradeObjectIdentifier'))
    GradeObjectName = property(get_string_prop('GradeObjectName'))
    GradeObjectType = property(get_number_prop('GradeObjectType'))
    GradeObjectTypeName = property(get_string_prop('GradeObjectTypeName'))

class GradeValueComputable(GradeValue):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    PointsNumerator = property(get_number_prop('PointsNumerator'))
    PointsDenominator = property(get_number_prop('PointsDenominator'))
    WeightedNumerator = property(get_number_prop('WeightedNumerator'))
    WeightedDenominator = property(get_number_prop('WeightedDenominator'))


## Locker concrete classes
class LockerItem(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Name = property(get_string_prop('Name'))
    Description = property(get_string_prop('Description'))
    Type = property(get_number_prop('Type'))
    Size = property(get_number_prop('Size'))
    LastModified = property(get_string_prop('LastModified'))

class LockerFolder(D2LStructure):
    def __init__(self,json_dict):
        D2LStructure.__init__(self,json_dict)

    Name = property(get_string_prop('Name'))

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

    HasLocker = property(get_boolean_prop('HasLocker'))
