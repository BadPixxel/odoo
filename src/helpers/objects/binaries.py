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

from splashpy import const
from splashpy.componants import FieldFactory, Files
from splashpy.helpers import FilesHelper, ImagesHelper
from splashpy.core.framework import Framework
from odoo.addons.splashsync.models.configuration import ResConfigSettings


class BinaryFields():

    __BinaryTypes__ = {
        "binary": const.__SPL_T_IMG__,
    }

    __BinaryFields__ = None

    def get_binary_fields_list(self):
        """Build & Store List of Binary Fields Definitions"""
        # List already in cache
        if self.__BinaryFields__ is not None:
            return self.__BinaryFields__
        # Init List Cache
        self.__BinaryFields__ = {}
        # Walk on Model Fields Definitions
        for fieldId in self.getModel().fields_get():
            # Get Fields Definitions
            field = self.getModel().fields_get([fieldId])
            # Filter on ID Field
            if fieldId == "id":
                continue
            # Filter on Binary Fields Types
            if field[fieldId]["type"] not in self.__BinaryTypes__.keys():
                continue
            # Add Definition to Cache
            self.__BinaryFields__[fieldId] = field[fieldId]

        return self.__BinaryFields__

    def buildBinaryFields(self):
        # Walk on Model Binary Fields Definitions
        for fieldId, field in self.get_binary_fields_list().items():
            # Build Splash Field Definition
            FieldFactory.create(self.__BinaryTypes__[field["type"]], fieldId, field["string"])
            if field["required"] or fieldId in self.get_required_fields():
                FieldFactory.isRequired()
            if field["readonly"]:
                FieldFactory.isReadOnly()
            if 'help' in field:
                FieldFactory.description(field["help"])

    def getBinaryFields(self, index, field_id):
        # Load Binary Fields Definitions
        fields_def = self.get_binary_fields_list()
        # Check if this field is Binary...
        if field_id not in fields_def.keys():
            return

        self._out[field_id] = self.encode(field_id)
        self._in.__delitem__(index)

    def setBinaryFields( self, field_id, field_data ):
        # Load Binary Fields Definitions
        fields_def = self.get_binary_fields_list()
        # Check if this field is Binary...
        if field_id not in fields_def.keys():
            return
        # ====================================================================#
        # Empty Value Received
        if not isinstance(field_data, dict) or field_data is None:
            self.setSimple(field_id, None)

            return
        # ====================================================================#
        # Compare Md5
        if field_data['md5'] == FilesHelper.md5(getattr(self.object, field_id), True):
            self._in.__delitem__(field_id)

            return
        # ====================================================================#
        # Read File from Server
        new_file = Files.getFile(field_data['path'], field_data['md5'])
        if isinstance(new_file, dict) and "raw" in new_file:
            self.setSimple(field_id, new_file["raw"])
            Framework.log().warn("File contents updated")
        else:
            Framework.log().error("Unable to read file from Server")

    def encode(self, field_id):
        """Encode Odoo Binary to Splash Field Data"""
        # ====================================================================#
        # Fetch Binary raw Contents
        base64_contents = getattr(self.object, field_id)
        if not isinstance(base64_contents, bytes):
            return None

        self.decode_file_path(self.encode_file_path(field_id))


        # ====================================================================#
        # Fetch Field Definition
        field = self.__BinaryFields__[field_id]
        # ====================================================================#
        # Detect Images
        if ImagesHelper.is_image(base64_contents, True):
            # ====================================================================#
            # Encode as Splash Images
            return ImagesHelper.encodeFromRaw(
                base64_contents,
                field["string"],
                field_id + "." + str(ImagesHelper.get_extension(base64_contents, True)),
                self.encode_file_path(field_id),
                self.get_image_url(field_id),
                True
            )
        # ====================================================================#
        # Encode as Splash File
        return FilesHelper.encodeFromRaw(
            base64_contents,
            field["string"],
            field_id,
            self.encode_file_path(field_id),
            True
        )



    def get_image_url(self, field_id):
        """Get Public Image Preview Url"""
        url = ResConfigSettings.get_base_url()
        url += "/web/image?model=" + self.getDomain()
        url += "&id=" + str(self.object['id']) + "&field=" + str(field_id)

        return url

    # ====================================================================#
    #  Object FILES Management
    # ====================================================================#

    def encode_file_path(self, field_id):
        """Build Virtual File Path for this Binary File"""
        return self.getType() + "::" + str(self.object['id']) + "::" + field_id

    def decode_file_path(self, path):
        """Decode Virtual File Path for this Binary File"""
        # Try to Explode Virtual Path
        try:
            splited = path.split('::')
            object_type, object_id, field_id = list(splited)
        except Exception:
            return None
        # Check if Virtual Path Point to Current Object Type
        if object_type != self.getType():
            return None
        # Return Path Info
        return {
            "type": object_type,
            "id": int(object_id),
            "field": field_id
        }

    def getFile(self, path, md5):
        """
        Custom Reading of a File from Local System (Database or any else)
        """
        # Decode Path Info
        info = self.decode_file_path(path)
        if info is None or info["field"] not in self.get_binary_fields_list().keys():
            return None
        # Load Object by Id
        self.object = self.load(info["id"])
        if self.object is False:
            return None
        # Encode Splash File
        splashFile = self.encode(info["field"])
        if splashFile is None or not isinstance(splashFile, dict):
            return None
        # Add Raw Contents to Splash File
        splashFile["raw"] = getattr(self.object, info["field"])

        return splashFile

