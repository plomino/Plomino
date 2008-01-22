# -*- coding: utf-8 -*-
#
# File: PlominoFile.py
#
# Copyright (c) 2008 by Eric BREHAULT (ebrehault@gmail.com)
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """Eric BREHAULT <ebrehault@gmail.com>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.file import ATFile
from Products.CMFPlomino.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PlominoFile_schema = getattr(ATFile, 'schema', Schema(())).copy() + \
	schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlominoFile(ATFile):
	"""
	"""
	security = ClassSecurityInfo()
	__implements__ = (getattr(ATFile,'__implements__',()),)

	# This name appears in the 'add' box
	archetype_name = 'PlominoFile'

	meta_type = 'PlominoFile'
	portal_type = 'PlominoFile'
	allowed_content_types = [] + list(getattr(ATFile, 'allowed_content_types', []))
	filter_content_types = 0
	global_allow = 0
	immediate_view = 'base_view'
	default_view = 'base_view'
	suppl_views = ()
	typeDescription = "PlominoFile"
	typeDescMsgId = 'description_edit_PlominoFile'

	_at_rename_after_creation = True

	schema = PlominoFile_schema

	##code-section class-header #fill in your manual code here
	##/code-section class-header

    # Methods


registerType(PlominoFile, PROJECTNAME)
# end of class PlominoFile

##code-section module-footer #fill in your manual code here
##/code-section module-footer



