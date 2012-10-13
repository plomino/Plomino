# -*- coding: utf-8 -*-
#
# File: PlominoAccessControl.py
#
# Copyright (c) 2008 by ['Eric BREHAULT']
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.com>"""
__docformat__ = 'plaintext'

# From the standard library
from cStringIO import StringIO
from email.Header import Header
from email import message_from_string
from time import strptime
from types import NoneType, StringTypes
import cgi
import csv
import decimal as std_decimal
import Globals
import htmlentitydefs
import Missing
import re
import urllib

# 3rd party Python 
from jsonutil import jsonutil as json

# Zope
from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
from DateTime import DateTime

# Plone
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import normalizeString as utils_normalizeString

try:
   from plone.app.upgrade import v40
   HAS_PLONE40 = True
except ImportError:
   HAS_PLONE40 = False

import logging
logger = logging.getLogger('Plomino')

severity_map = {
        'info': logging.INFO,
        'warning': logging.WARNING,
        'debug': logging.DEBUG
        }


def Log(message, summary='', severity='info', exc_info=False):
    """ Write a message to the event log. Useful from formulas.
    Optionally include a traceback.
    """
    # Pass in severity as a string, because we don't want to import
    # ``logging`` from scripts.
    logger.log(
            severity_map.get(severity, 'info'),
            'App: %s\n%s',
            summary,
            message,
            exc_info=exc_info)

def DateToString(d, format='%Y-%m-%d'):
    """ Return the date as string using the given format
    """
    # XXX: Should use db.getDateTimeFormat
    return d.strftime(format)

def StringToDate(str_d, format='%Y-%m-%d'):
    """ Parse the string using the given format and return the date 
    """
    # XXX: Should use db.getDateTimeFormat
    try:
        dt = strptime(str_d, format)
    except ValueError, e:
        # XXX: Just let DateTime guess.
        dt = strptime(DateTime(str_d).ISO(), '%Y-%m-%dT%H:%M:%S')
        logger.info('StringToDate> %s, %s, %s, guessed: %s'%(str(str_d), format, `e`, `dt`))
    if len(dt) >= 5:
        return DateTime(dt[0], dt[1], dt[2], dt[3], dt[4])
    else:
        return DateTime(dt[0], dt[1], dt[2])

def DateRange(d1, d2):
    """ Return all the dates from ``d1`` to ``d2`` (inclusive).
    Dates are ``DateTime`` instances.
    """
    duration = int(d2-d1)
    result = []
    current = d1
    for d in range(duration+1):
        result.append(current)
        current = current+1
    return result

def Now():
    """ current date and tile
    """
    return DateTime()

def sendMail(db, recipients, title, html_message, sender=None, cc=None, bcc=None, immediate=False):
    """Send an email
    """
    host = getToolByName(db, 'MailHost')
    plone_tools = getToolByName(db, 'plone_utils')

    message = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'
    message = message + "<html>"
    message = message + html_message
    message = message + "</html>"
    if sender is None:
        sender = db.getCurrentUser().getProperty("email")

    mail_message = message_from_string(asUnicode(message).encode('utf-8'))
    mail_message.set_charset('utf-8')
    mail_message.set_type("text/html")
    if cc:
        mail_message['CC']= Header(cc)
    if bcc:
        mail_message['BCC']= Header(bcc)
    if HAS_PLONE40:
        host.send(mail_message, recipients, sender, asUnicode(title).encode('utf-8'), msg_type='text/html', immediate=immediate)
    else:
        host.secureSend(message, recipients,
                        sender, subject=title,
                        subtype='html', charset='utf-8')


def userFullname(db, userid):
    """ Try to return user fullname, else return userid.
    Return "Unknown" if user not found.
    """
    user = getToolByName(db, 'portal_membership').getMemberById(userid)

    if not user:
        return "Unknown"

    fullname = user.getProperty('fullname')
    if fullname:
        return fullname
    else:
        return userid


def userInfo(db, userid):
    """ Return user object.
    """
    return getToolByName(db, 'portal_membership').getMemberById(userid)


def PlominoTranslate(msgid, context, domain='CMFPlomino'):
    """ Look up the translation for ``msgid`` in the current language.
    """
    plone_tools = getToolByName(context, 'plone_utils')
    encoding = plone_tools.getSiteEncoding()
    translation_service = getToolByName(context, 'translation_service')
    # When will message be an exception?
    if isinstance(msgid, Exception):
        try:
            msgid = msgid[0]
        except (TypeError, IndexError):
            pass
    if HAS_PLONE40:
        msg = translation_service.utranslate(domain=domain, msgid=msgid, context=context)
    else:
        msg = translation_service.utranslate(msgid=msgid, domain=domain, context=context)
    return translation_service.encode(msg) # convert unicode to site encoding

def htmlencode(s):
    """ Replace characters with their corresponding HTML entities.
    """
    t = ""
    if type(s) != unicode:
        from Products.CMFPlone.utils import safe_unicode
        s = safe_unicode(s)
        # Doesn't work unless utils becomes a persistent tool.
        # translation_service = getToolByName(context, 'translation_service')
        # s = translation_service.asunicodetype(s)
    for c in s:
        name = htmlentitydefs.codepoint2name.get(ord(c))
        if name:
            t += "&%s;" % name
        else:
            t += c
    return t

def urlencode(h):
    """ Call urllib.urlencode
    """
    return urllib.urlencode(h)

def cgi_escape(s):
    return cgi.escape(s)

def normalizeString(text, context=None, encoding=None):
    return utils_normalizeString(text, context, encoding)

def asList(x):
    """ If not list, return x in a single-element list.
    .. note:: If ``x`` is ``None``, this will return ``[None]``.
    """
    if hasattr(x, 'append'):
        return x
    else:
        return [x]


def asUnicode(s):
    """ Make sure ``s`` is unicode; decode according to site encoding if
    needed.
    """
    if not isinstance(s, basestring):
        return unicode(s)
    from Products.CMFPlone.utils import safe_unicode
    return safe_unicode(s)
    # Doesn't work unless utils becomes a persistent tool.
    # translation_service = getToolByName(context, 'translation_service')
    # return translation_service.asunicodetype(s)


def csv_to_array(csvcontent, delimiter='\t', quotechar='"'):
    """ ``csvcontent`` may be a string or a file.
    """
    if not csvcontent:
        return []
    if type(csvcontent) is str:
        csvfile = StringIO(csvcontent)
    elif hasattr(csvcontent, 'blob'):
        csvfile = csvcontent.blob.open()
    else:
        csvfile = csvcontent
    # XXX: why not just return the list-like ``_csv.reader`` object?
    return [l for l in csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)]


def array_to_csv(array, delimiter='\t', quotechar='"'):
    """ Convert ``array`` (a list of lists) to a CSV string.
    """
    s = StringIO()
    writer = csv.writer(s, delimiter=delimiter, quotechar=quotechar, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerows(array)
    return s.getvalue()


def open_url(url, asFile=False):
    """ Retrieve content from ``url``.
    """
    f = urllib.urlopen(url)
    if asFile:
        return f.fp
    else:
        return f.read()

def MissingValue():
    """ Useful to test search results value (as ``Missing.Value`` cannot be imported in scripts).
    """
    return Missing.Value

def isDocument(doc):
    if doc:
        if hasattr(doc, 'isDocument'):
            return doc.isDocument()
    return False

def json_dumps(obj):
    return json.dumps(obj)

def json_loads(json_string):
    return json.loads(json_string)

# From http://lsimons.wordpress.com/2011/03/17/stripping-illegal-characters-out-of-xml-in-python/
_illegal_xml_chars_RE = re.compile(u'[\x00-\x08\x0b\x0c\x0e-\x1F\uD800-\uDFFF\uFFFE\uFFFF]')
def escape_xml_illegal_chars(val, replacement='?'):
    """Filter out characters that are illegal in XML.
    Looks for any character in val that is not allowed in XML
    and replaces it with replacement ('?' by default).
    """
    return _illegal_xml_chars_RE.sub(replacement, val)

class plomino_decimal(std_decimal.Decimal, Implicit):
    security = ClassSecurityInfo()
    security.declareObjectPublic()
    security.declarePublic('as_tuple')
    security.declarePublic('quantize')

Globals.InitializeClass(plomino_decimal)

def decimal(v='0'):
    """ Expose the standard library's Decimal class. Useful for finances.
    """
    if type(v) not in StringTypes:
        v = str(v)
    try:
        v = plomino_decimal(v)
        return v
    except std_decimal.InvalidOperation:
        return 'ERROR'

def actual_path(context):
    """ return the actual path from the request
    Useful in portlet context
    """
    if not hasattr(context, "REQUEST"):
        return None
    url = context.REQUEST.get("ACTUAL_URL")
    return context.REQUEST.physicalPathFromURL(url)

def actual_context(context, search="PlominoDocument"):
    """ return the actual context from the request
    Useful in portlet context
    """
    path = actual_path(context)
    if not path:
        return None
    current_context = context.unrestrictedTraverse(path)
    while len(path)>0 and current_context.__class__.__name__!=search:
        path = path[:-1]
        current_context = context.unrestrictedTraverse(path)
    if current_context.__class__.__name__ == search:
        return current_context
    else:
        return None