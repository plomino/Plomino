# -*- coding: utf-8 -*-
#
# File: base.py
#
# Copyright (c) 2008 by ['Eric BREHAULT']
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.org>"""
__docformat__ = 'plaintext'

# 3rd party
from jsonutil import jsonutil as json

# Zope
from zope.interface import Interface, implements
from zope.annotation.interfaces import IAnnotations
from Acquisition import aq_base
try:
    from five.formlib.formbase import EditForm
except:
    #PLONE 3
    from Products.Five.formlib.formbase import EditForm
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# Plomino
from Products.CMFPlomino.PlominoUtils import asUnicode

import logging
_logger = logging.getLogger('Plomino')


class IBaseField(Interface):
    """
    """


class BaseField(object):
    """
    """
    implements(IBaseField)

    def __init__(self, context):
        """Initialize adapter."""
        self.context = context
        # get annotation to store param values
        annotations = IAnnotations(context)
        self.parameters = annotations.get("PLOMINOFIELDCONFIG", None)
        # allow access
        self.__allow_access_to_unprotected_subobjects__ = True

    def validate(self, strValue):
        """
        """
        errors = []
        return errors

    def processInput(self, strValue):
        """
        """
        if type(strValue) == str:
            strValue = strValue.decode('utf-8')
        return strValue

    def getSelectionList(self, doc):
        """
        """
        return None

    def getFieldValue(self, form, doc=None, editmode_obsolete=False,
            creation=False, request=None):
        """ Return the field as rendered by ``form`` on ``doc``.

        We may be called on:
        - a blank form, e.g. while creating a document;
        - an existing document;
        - a TemporaryDocument used during datagrid editing.

        - If EDITABLE, look for the field value:
          - are we creating a doc or editing a datagrid row?
            - do we have a request?
              - if we're being used for a datagrid,
                - get field value from `getDatagridRowdata`,
                - or compute a default value;
              - otherwise look for `request[fieldName]`;
              - otherwise look for `request[fieldName+'_querystring']`;
            - otherwise compute a default value.
          - otherwise just `getItem`
        - if DISPLAY/COMPUTED:
          - if DISPLAY and doc and no formula: `getItem`.
          - else compute
        - if CREATION
          - compute or `getItem`
        - if COMPUTEDONSAVE and doc: `getItem`
        - otherwise, give up.
        """
        # XXX: The editmode_obsolete parameter is unused.
        fieldName = self.context.id
        mode = self.context.getFieldMode()

        db = self.context.getParentDatabase()
        if doc:
            target = doc
        else:
            target = form

        fieldValue = None
        if mode == "EDITABLE":
            # if (not doc) or creation:
            if doc:
                fieldValue = doc.getItem(fieldName)
                #DBG _logger.info('BaseField.getFieldValue> 1 got doc') 
    
            if (not fieldValue) and self.context.Formula():
                # This implies that if a falsy fieldValue is possible, 
                # Formula needs to take it into account, e.g. using hasItem
                fieldValue = form.computeFieldValue(fieldName, target)
                #DBG _logger.info('BaseField.getFieldValue> 2 default formula') 
            elif (not fieldValue) and request:
                # if no doc context and no default formula, we accept
                # value passed in the REQUEST so we look for 'fieldName'
                # but also for 'fieldName_querystring' which allows to
                # pass value via the querystring without messing the
                # POST content
                request_value = request.get(fieldName, '')
                #DBG _logger.info('BaseField.getFieldValue> 3 request') 
                if not request_value:
                    request_value = request.get(fieldName + '_querystring', '')
                    #DBG _logger.info('BaseField.getFieldValue> 3 request _querystring') 
                fieldValue = asUnicode(request_value)
            if not fieldValue:
                #DBG _logger.info('BaseField.getFieldValue> 4 blank') 
                fieldValue = ""

        elif mode in ["DISPLAY", "COMPUTED"]:
            if mode == "DISPLAY" and not self.context.Formula() and doc:
                fieldValue = doc.getItem(fieldName)
            else:
                fieldValue = form.computeFieldValue(fieldName, target)

        elif mode == "CREATION":
            if creation or not doc:
                # Note: on creation, there is no doc, we use form as target
                # in formula, and we do the same when no doc (e.g. with tojson)
                fieldValue = form.computeFieldValue(fieldName, form)
            else:
                fieldValue = doc.getItem(fieldName)

        elif mode == "COMPUTEDONSAVE" and doc:
            fieldValue = doc.getItem(fieldName)

        if fieldValue is None:
            fieldValue = ""

        #DBG _logger.info('BaseField.getFieldValue> doc: %s, fieldName: %s, fieldValue: %s, creation: %s' % (`doc`, `fieldName`, `fieldValue`[:20], creation)) 
        return fieldValue


class BaseForm(EditForm):
    """
    """

    template = ViewPageTemplateFile('settings_edit.pt')
