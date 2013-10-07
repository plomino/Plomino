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

from base64 import encodestring
from string import replace
from zope.contenttype import guess_content_type
import email.mime.application
import email.mime.multipart
import email.mime.text
import email.generator
import httplib
import io
import urllib
import urlparse


def authenticateAndLoadURL(targetURL, username, password):
    """ Authenticate and return URL page content
    """

    # scheme://netloc/path;parameters?query#fragment
    urlparts = urlparse.urlsplit(targetURL)
    scheme, netloc, path, query, fragment = urlparts

    # Normally, characters like '/' are safe in URLs. Not in passwords.
    username = urllib.quote(username, safe='')
    password = urllib.quote(password, safe='')
    u = '%(scheme)s://%(user)s:%(password)s@%(netloc)s%(path)s?%(query)s' % {
            'scheme': scheme,
            'user': username,
            'password': password,
            'netloc': netloc,
            'path': path,
            'query': query,
            }
    f = urllib.urlopen(u)
    return f

def authenticateAndPostToURL(targetURL, username, password, filename=None, filecontent=None, parameters={}):
    """ Authenticate and post (files) to URL

    Either both or neither filename and filecontent should be submitted.
    """

    # content_type, body = encode_file(filename, filecontent)
    formdata = FormData()

    if filename:
        content_type, encoding = guess_content_type(filename, filecontent)
        formdata.setFile(filename, filecontent, content_type)
        parameters['filename'] = filename

    for name, value in parameters.items():
        formdata.setText(name, value)

    body = formdata.http_body()
    boundary = body.splitlines()[0].split('"')[1]
    http_content_type = 'multipart/form-data; boundary=%s' % boundary 

    # scheme://netloc/path;parameters?query#fragment
    urlparts = urlparse.urlsplit(targetURL)
    scheme, netloc, path, query, fragment = urlparts

    conn = httplib.HTTPConnection(netloc)
    headers = {'content-type': http_content_type,
               'content-length': str(len(body)),
               "AUTHORIZATION": "Basic %s" % replace(
                   encodestring("%s:%s" % (username, password)),
                   "\012", "")
               }
    conn.request("POST", path, None, headers)
    conn.send(body)
    response = conn.getresponse()
    return (response.status, response.reason)


# Adapted from http://stackoverflow.com/questions/13514713/properly-format-multipart-form-data-body
class FormData(email.mime.multipart.MIMEMultipart):

    def __init__(self):
        email.mime.multipart.MIMEMultipart.__init__(self, 'form-data')

    def setText(self, name, value):
        part = email.mime.text.MIMEText(value, _charset='utf-8')
        part.add_header('Content-Disposition', 'form-data', name=name)
        self.attach(part)
        return part

    def setFile(self, name, value, filename, mimetype=None):
        part = email.mime.application.MIMEApplication(value)
        part.add_header('Content-Disposition', 'form-data',
                        name=name, filename=filename)
        if mimetype is not None:
            part.set_type(mimetype)
        self.attach(part)
        return part

    def http_body(self):
        b = io.BytesIO()
        gen = email.generator.Generator(b, False, 0)
        gen.flatten(self, False)
        b.write(b'\r\n')
        b = b.getvalue()
        return b
        # pos = b.find(b'\r\n\r\n')
        # assert pos >= 0
        # return b[pos + 4:]

# fd = FormData()
# fd.setText('foo', 'bar')
# fd.setText('täst', 'Täst')
# fd.setFile('file', b'abcdef'*50, 'Täst.txt')
# sys.stdout.buffer.write(fd.http_body())


# def encode_file(filename, filecontent):
#     """ (based on Wade Leftwich's post on aspn.activestate.com)
#     """
# 
# 
#     BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
#     CRLF = '\r\n'
#     L = []
#     L.append('--' + BOUNDARY)
#     L.append('Content-Disposition: form-data; name="file"; filename="%s"' % filename)
#     L.append('Content-Type: %s' % get_content_type(filename))
#     L.append('')
#     L.append(filecontent)
#     L.append('--' + BOUNDARY + '--')
#     L.append('')
#     body = CRLF.join(L)
#     content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
#     return content_type, body
# 
# def get_content_type(filename):
#     return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
