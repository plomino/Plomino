# -*- coding: utf-8 -*-
#
# File: HttpUtils.py
#
# Copyright (c) 2007 by ['[Eric BREHAULT]']
#
# Zope Public License (ZPL)
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

__author__ = """[Eric BREHAULT] <[ebrehault@gmail.com]>"""
__docformat__ = 'plaintext'

import urllib, urllib2, httplib, urlparse, mimetypes
from base64 import encodestring
from string import replace

def authenticateAndLoadURL(targetURL, username, password):
    """ Authenticate and return URL page content
    """
    urlparts = urlparse.urlsplit(targetURL)
    # Normally, characters like '/' are safe in URLs. Not in passwords.
    username = urllib.quote(username, safe='')
    password = urllib.quote(password, safe='')
    u=urlparts[0]+"://"+username+":"+password+"@"+urlparts[1]+urlparts[2]+"?"+urlparts[3]
    f=urllib.urlopen(u)
    return f


def authenticateAndPostToURL(targetURL, username, password, filename, filecontent):
    """ authenticate and post files to URL
    """
    content_type, body = encode_file(filename, filecontent)
    urlparts = urlparse.urlsplit(targetURL)

    conn = httplib.HTTPConnection(urlparts[1])
    headers = {'content-type': content_type,
               'content-length': str(len(body)),
               "AUTHORIZATION": "Basic %s" % replace(encodestring("%s:%s" % (username, password)),"\012", "")
               }
    conn.request("POST",urlparts[2], None, headers)
    conn.send(body)
    response = conn.getresponse()
    return (response.status, response.reason)

def encode_file(filename, filecontent):
    """ (based on Wade Leftwich's post on aspn.activestate.com)
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    L.append('--' + BOUNDARY)
    L.append('Content-Disposition: form-data; name="file"; filename="%s"' % filename)
    L.append('Content-Type: %s' % get_content_type(filename))
    L.append('')
    L.append(filecontent)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
