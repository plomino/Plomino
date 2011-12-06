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

from DateTime import DateTime
from time import strptime
from Products.CMFCore.utils import getToolByName
import htmlentitydefs as entity
import urllib
import cgi
import csv
from cStringIO import StringIO
import Missing
from email import message_from_string
from email.Header import Header

try:
   from plone.app.upgrade import v40
   HAS_PLONE40 = True
except ImportError:
   HAS_PLONE40 = False

import logging
logger = logging.getLogger('Plomino')

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
        dt = strptime(DateTime(str_d).ISO(), '%Y-%m-%d %H:%M:%S')
        logger.info('StringToDate> %s, %s, %s, guessed: %s'%(str(str_d), format, `e`, `dt`))
    if len(dt)>=5:
        return DateTime(dt[0], dt[1], dt[2], dt[3], dt[4])
    else:
        return DateTime(dt[0], dt[1], dt[2])

def DateRange(d1, d2):
    """return all the days from the d1 date to the d2 date (included)
    """
    duration = int(d2-d1)
    result=[]
    current=d1
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
    """ return user fullname if exist, else return userid, and return Unknown if user not found
    """
    user=getToolByName(db, 'portal_membership').getMemberById(userid)
    if not(user is None):
        fullname=user.getProperty('fullname')
        if fullname=='':
            return userid
        else:
            return fullname
    else:
        return "Unknown"

def userInfo(db, userid):
    """ return user object
    """
    user=getToolByName(db, 'portal_membership').getMemberById(userid)
    return user

def PlominoTranslate(message, context, domain='CMFPlomino'):
    """
    """
    plone_tools = getToolByName(context, 'plone_utils')
    encoding = plone_tools.getSiteEncoding()
    translation_service = getToolByName(context, 'translation_service')
    if isinstance(message, Exception):
        try:
            message = message[0]
        except (TypeError, IndexError):
            pass
    msg = translation_service.utranslate(domain=domain, msgid=message, context=context)
    return translation_service.encode(msg) # convert unicode to site encoding

def htmlencode(s):
    """ replace unicode characters with their corresponding html entities
    """

    t=""
    for i in s:
        if ord(i) in entity.codepoint2name:
            name = entity.codepoint2name.get(ord(i))
            entityCode = entity.name2codepoint.get(name)
            t +="&#" + str(entityCode)
        else:
            t+=i
    return t

def urlencode(h):
    """ call urllib.urlencode
    """
    return urllib.urlencode(h)

def asList(x):
    """ if not list, return x in a single-element list
    XXX: Don't call asList if x may be None, as [None] probably is not what you
    want.
    """
    if hasattr(x, 'append'):
        return x
    else:
        return [x]

def asUnicode(x):
    """
    """
    if type(x) is str:
        return x.decode('utf-8')
    if type(x) is unicode:
        return x
    return unicode(x)

def csv_to_array(csvcontent, delimiter='\t', quotechar='"'):
    """ csvcontent might be a string or a file
    """
    if csvcontent is None:
        return []
    if type(csvcontent) is str:
        csvfile = StringIO(csvcontent)
    elif hasattr(csvcontent, 'blob'):
        csvfile = csvcontent.blob.open()
    else:
        csvfile = csvcontent
    return [l for l in csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)]

def array_to_csv(values, delimiter='\t', quotechar='"'):
    """
    """
    s = StringIO()
    writer = csv.writer(s, delimiter=delimiter, quotechar=quotechar, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerows(values)
    return s.getvalue()

def open_url(url, asFile=False):
    """ retrieve content from url
    """
    f=urllib.urlopen(url)
    if asFile:
        return f.fp
    else:
        return f.read()

def MissingValue():
    """ Useful to test search results value (as Missing.Value cannot be imported in scripts)
    """
    return Missing.Value

def isDocument(doc):
    if doc:
        if hasattr(doc, 'isDocument'):
            return doc.isDocument()
    return False

def cgi_escape(s):
    return cgi.escape(s)
