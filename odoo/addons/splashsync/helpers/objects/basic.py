# -*- coding: utf-8 -*-
#
#  This file is part of SplashSync Project.
#
#  Copyright (C) 2015-2019 Splash Sync  <www.splashsync.com>
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  For the full copyright and license information, please view the LICENSE
#  file that was distributed with this source code.
#

from collections import OrderedDict
from splashpy import const, Framework
from splashpy.componants.fieldfactory import FieldFactory


class BasicFields():

    __BasicTypes__ = {
        "boolean": const.__SPL_T_BOOL__,
        "char": const.__SPL_T_VARCHAR__,
        "text": const.__SPL_T_VARCHAR__,
        "integer": const.__SPL_T_INT__,
        "float": const.__SPL_T_DOUBLE__,
        "date": const.__SPL_T_DATE__,
        "datetime": const.__SPL_T_DATETIME__,
    }

    __BasicFields__ = None

    def get_basic_fields_list(self):
        """Build & Store List of Basic Fields Definitions"""
        # List already in cache
        if self.__BasicFields__ is not None:
            return OrderedDict(sorted(self.__BasicFields__.items()))
        # Init List Cache
        self.__BasicFields__ = {}
        # Walk on Model Fields Definitions
        for fieldId in self.getModel().fields_get():
            # Get Fields Definitions
            field = self.getModel().fields_get([fieldId])
            # Filter Not Allowed Field
            if fieldId in self.get_composite_fields():
                continue
            # Filter on Basic Fields Types
            if field[fieldId]["type"] not in self.__BasicTypes__.keys():
                continue
            # Add Definition to Cache
            self.__BasicFields__[fieldId] = field[fieldId]

        return OrderedDict(sorted(self.__BasicFields__.items()))

    def buildBasicFields(self):
        # Walk on Model Basic Fields Definitions
        for fieldId, field in self.get_basic_fields_list().items():
            # Build Splash Field Definition
            FieldFactory.create(self.__BasicTypes__[field["type"]], fieldId, field["string"])
            FieldFactory.group("Others")
            # FieldFactory.isReadOnly()

            if field["required"] or fieldId in self.get_required_fields():
                FieldFactory.isRequired()
            if field["readonly"]:
                FieldFactory.isReadOnly()
            if 'help' in field:
                FieldFactory.description(field["help"])
            if fieldId in self.get_listed_fields():
                FieldFactory.isListed()

            # Force Urls generator options
            if field["type"] is "char":
                FieldFactory.addOption("Url_Prefix", "http://")

    def getCoreFields(self, index, field_id):
        # Load Basic Fields Definitions
        fields_def = self.get_basic_fields_list()
        # Check if this field is Basic...
        if field_id not in fields_def.keys():
            return
        # Collect field value...
        field_type = fields_def[field_id]['type']
        if field_type in ['char', 'text']:
            self.getSimpleStr(index, field_id)

        elif field_type in ['boolean', 'integer', 'float']:
            self.getSimple(index, field_id)

        elif field_type in ['date']:
            self.getSimpleDate(index, field_id)

        elif field_type in ['datetime']:
            self.getSimpleDateTime(index, field_id)

    def setCoreFields(self, field_id, field_data):
        # Load Basic Fields Definitions
        fields_def = self.get_basic_fields_list()
        # Check if this field is Basic...
        if field_id not in fields_def.keys():
            return
        # Update field value...
        field_type = fields_def[field_id]['type']

        if field_type in ['char', 'text', 'integer', 'float']:
            self.setSimple(field_id, field_data)

        if field_type in ['boolean']:
            self.setSimpleBool(field_id, field_data)

        if field_type in ['date']:
            self.setSimpleDate(field_id, field_data)

        if field_type in ['datetime']:
            self.setSimpleDateTime(field_id, field_data)

    def collectRequiredCoreFields(self):
        """
        Collect All Required Core Fields from Inputs
        :return: False|hash
        """
        # Init List of required Fields
        reqFields = {}
        # Walk on Model Basic Fields Definitions
        for fieldId, field in self.get_basic_fields_list().items():
            # Check if Field is Required for Creation
            if not field["required"] and fieldId not in self.get_required_fields():
                continue
            # Ensure Field is In Inputs Values
            if fieldId not in self._in:
                Framework.log().error("Fields "+fieldId+" is required.")

                return False
            # Add Field Value to Model Data
            reqFields[fieldId] = self._in[fieldId]

        return reqFields
