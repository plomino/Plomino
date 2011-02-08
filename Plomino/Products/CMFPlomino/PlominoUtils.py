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
import csv
from cStringIO import StringIO
import Missing

def DateToString(d, format='%Y-%m-%d'):
    """return the date as string using the given format, default is '%Y-%m-%d'
    """
    #return DateTime(*d[0:6]).strftime(format)
    return d.strftime(format)

def StringToDate(str_d, format='%Y-%m-%d'):
    """parse the string using the given format (default is '%Y-%m-%d') and return the date 
    """
    dt = strptime(str_d, format)
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

def sendMail(db, recipients, title, html_message, sender=None):
    """Send an email
    """
    host = getToolByName(db, 'MailHost')
    plone_tools = getToolByName(db, 'plone_utils')
    encoding = plone_tools.getSiteEncoding()
    message = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'
    message = message + "<html>"
    message = message + html_message
    message = message + "</html>"
    if sender is None:
        sender = db.getCurrentUser().getProperty("email")
    # secureSend is deprecated in Plone 4 but as it takes care to produce
    # the email.MIMEText.MIMEText and set headers etc. by itself, it remains
    # for now the most robust approach
    host.secureSend(message, recipients,
        sender, subject=title,
        subtype='html', charset=encoding)
    
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
    msg = translation_service.translate(msgid=message, domain=domain)
    return msg.encode(encoding) # convert unicode to site encoding

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
