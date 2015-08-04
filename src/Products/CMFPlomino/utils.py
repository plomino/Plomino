# -*- coding: utf-8 -*-

from cStringIO import StringIO
from datetime import datetime
from dateutil.parser import parse
from email.Header import Header
from email import message_from_string
from types import StringTypes
import cgi
import csv
import decimal as std_decimal
import Globals
import htmlentitydefs
import Missing
import re
import urllib
import transaction
from jsonutil import jsonutil as json
from AccessControl import ClassSecurityInfo
from AccessControl.unauthorized import Unauthorized
try:
    from AccessControl.class_init import InitializeClass
except ImportError:
    from App.class_init import InitializeClass
from DateTime import DateTime
from zope import component
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import normalizeString as utils_normalizeString

from .interfaces import IPlominoSafeDomains
from .config import TIMEZONE, SCRIPT_ID_DELIMITER

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
        exc_info=exc_info
    )


def DateToString(d, format=None, db=None):
    """ Return the date as string using the given format.

    Pass in database object to use default format.
    """
    if not format:
        if db:
            format = db.datetime_format
        if not format:
            format = '%Y-%m-%d'
    return d.toZone(TIMEZONE).strftime(format)


def StringToDate(str_d, format='%Y-%m-%d', db=None):
    """ Parse the string using the given format and return the date.

    With StringToDate, it's best to have a fixed default format,
    as it is easier for formulas to control the input date string than the
    portal date format.

    Pass `format=None` to allow StringToDate to guess.
    """
    try:
        if db:
            format = db.datetime_format
        if format:
            dt = datetime.strptime(str_d, format)
        else:
            dt = parse(str_d)
    except ValueError, e:
        # XXX: Just let DateTime guess.
        dt = parse(DateTime(str_d).ISO())
        logger.info('StringToDate> %s, %s, %s, guessed: %s' % (
            str(str_d),
            format,
            repr(e),
            repr(dt)))
    return DateTime(dt).toZone(TIMEZONE)


def DateRange(d1, d2):
    """ Return all the dates from ``d1`` to ``d2`` (inclusive).
    Dates are ``DateTime`` instances.
    """
    duration = int(d2 - d1)
    result = []
    current = d1
    for d in range(duration + 1):
        result.append(current)
        current = current + 1
    return result


def Now():
    """ current date and tile
    """
    return DateTime()


def sendMail(
    db,
    recipients,
    title,
    html_message,
    sender=None,
    cc=None,
    bcc=None,
    immediate=False
):
    """Send an email
    """
    host = getToolByName(db, 'MailHost')

    message = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'
    message = message + "<html>"
    message = message + html_message
    message = message + "</html>"
    if not sender:
        sender = db.getCurrentMember().getProperty("email")

    mail_message = message_from_string(asUnicode(message).encode('utf-8'))
    mail_message.set_charset('utf-8')
    mail_message.set_type("text/html")
    if cc:
        mail_message['CC'] = Header(cc)
    if bcc:
        mail_message['BCC'] = Header(bcc)
    if HAS_PLONE40:
        host.send(
            mail_message,
            recipients,
            sender,
            asUnicode(title).encode('utf-8'),
            msg_type='text/html',
            immediate=immediate
        )
    else:
        host.secureSend(
            message,
            recipients,
            sender,
            subject=title,
            subtype='html',
            charset='utf-8'
        )


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
    translation_service = getToolByName(context, 'translation_service')
    # When will message be an exception?
    if isinstance(msgid, Exception):
        logging.info("msgid is an Exception: %s" % msgid)
        try:
            msgid = msgid[0]
        except (TypeError, IndexError):
            logging.exception("Couldn't subscript msgid: %s" % msgid, exc_info=True)
            pass

    msg = translation_service.utranslate(
        msgid=msgid,
        domain=domain,
        context=context
    )
    # this converts unicode to site encoding:
    return translation_service.encode(msg)


def htmlencode(s):
    """ Replace characters with their corresponding HTML entities.
    """
    t = ""
    if type(s) != unicode:
        from Products.CMFPlone.utils import safe_unicode
        s = safe_unicode(s)
        # The following doesn't work unless utils becomes a persistent tool:
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

    (Encode a sequence of two-element tuples or dictionary into a URL query
    string, does quoting.)
    """
    # TODO: consider doseq parameter
    return urllib.urlencode(h)


def urlquote(s):
    """ Call urllib.quote

    (quote('abc def') -> 'abc%20def')
    """
    return urllib.quote(s)


def cgi_escape(s):
    return cgi.escape(s)


def normalizeString(text, context=None, encoding=None):
    return utils_normalizeString(text, context, encoding)


def asList(x):
    """ If not list, return x in a single-element list.

    .. note:: This will wrap falsy values like ``None`` or ``''`` in a list,
              making them truthy.
    """
    if isinstance(x, (list, tuple)):
        return x
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
    if isinstance(csvcontent, basestring):
        csvfile = StringIO(csvcontent)
    elif hasattr(csvcontent, 'blob'):
        csvfile = csvcontent.blob.open()
    else:
        csvfile = csvcontent
    # XXX: why not just return the list-like ``_csv.reader`` object?
    return [l for l in csv.reader(
        csvfile, delimiter=delimiter, quotechar=quotechar)]


def array_to_csv(array, delimiter='\t', quotechar='"'):
    """ Convert ``array`` (a list of lists) to a CSV string.
    """
    s = StringIO()
    writer = csv.writer(
        s,
        delimiter=delimiter,
        quotechar=quotechar,
        quoting=csv.QUOTE_NONNUMERIC
    )
    writer.writerows(array)
    return s.getvalue()


def open_url(url, asFile=False, data=None):
    """ retrieve content from url
    """
    safe_domains = []
    for safedomains_utils in component.getUtilitiesFor(IPlominoSafeDomains):
        safe_domains += safedomains_utils[1].domains
    is_safe = False
    for domain in safe_domains:
        if (url.startswith(domain)
            or url.split("//")[1].split("/")[0].split('@')[-1] == domain):
            is_safe = True
            break
    if is_safe:
        if data and not isinstance(data, basestring):
            data = urllib.urlencode(data)
        f=urllib.urlopen(url, data)
        if asFile:
            return f.fp
        else:
            return f.read()
    else:
        raise Unauthorized(url)


def MissingValue():
    """ Useful to test search results value
    (as ``Missing.Value`` cannot be imported in scripts).
    """
    return Missing.Value


def isDocument(doc):
    if doc:
        if hasattr(doc, 'isDocument'):
            return doc.isDocument()
    return False


def json_dumps(data):
    return json.dumps(data)


def json_loads(json_string):
    return json.loads(json_string)


# From http://lsimons.wordpress.com/2011/03/17/stripping-illegal-characters-out-of-xml-in-python/
_illegal_xml_chars_RE = re.compile(
    u'[\x00-\x08\x0b\x0c\x0e-\x1F\uD800-\uDFFF\uFFFE\uFFFF]')
def escape_xml_illegal_chars(val, replacement='?'):
    """Filter out characters that are illegal in XML.
    Looks for any character in val that is not allowed in XML
    and replaces it with replacement ('?' by default).
    """
    return _illegal_xml_chars_RE.sub(replacement, val)


class plomino_decimal(std_decimal.Decimal):
    security = ClassSecurityInfo()
    security.declareObjectPublic()
    security.declarePublic('as_tuple')
    security.declarePublic('quantize')

InitializeClass(plomino_decimal)


def decimal(v='0'):
    """ Expose the standard library's Decimal class. Useful for finances.
    """
    if not v:
        v = '0'
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
    while len(path) > 0 and current_context.__class__.__name__ != search:
        path = path[:-1]
        current_context = context.unrestrictedTraverse(path)
    if current_context.__class__.__name__ == search:
        return current_context
    else:
        return None


def is_email(email):
    if re.match(
            '^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.'
            '([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$', email):
        return True
    else:
        return False


def translate(context, content, i18n_domain=None):
    """ Translate content, if possible. 
    """
    # TODO: translate non-string content? Like dates?
    if not isinstance(content, basestring):
        return content

    request = getattr(context, 'REQUEST', None)
    if request and request.get("translation")=="off":
        return content

    def translate_token(match):
        translation = PlominoTranslate(
                match.group(1),
                context,
                domain=i18n_domain
                )
        translation = asUnicode(translation)
        return translation

    content = re.sub(
            "__(?P<token>.+?)__",
            translate_token,
            content
            )
    return content


def getDatagridRowdata(context, REQUEST):
    """ Return rowdata for a datagrid on a modal popup

    In the context of a modal datagrid popup, return the rowdata 
    on the REQUEST.
    """
    # This is currently just used during creation of TemporaryDocument,
    # but may possibly be useful in formulas. I won't publish it yet though.
    if not REQUEST:
        return [], []

    mapped_field_ids = []
    rowdata = []
    form_id = getattr(REQUEST, 'Plomino_Parent_Form', None)
    field_id = getattr(REQUEST, 'Plomino_Parent_Field', None)
    if form_id and field_id:
        form = context.getParentDatabase().getForm(form_id)
        field = form.getFormField(field_id)
        settings = field.getSettings()
        mapped_field_ids = [f.strip() for f in settings.field_mapping.split(',')]
    rowdata_json = getattr(REQUEST, 'Plomino_datagrid_rowdata', None)
    if rowdata_json:
        rowdata = json.loads(
                urllib.unquote(rowdata_json).decode('raw_unicode_escape'))
    return mapped_field_ids, rowdata

def save_point():
    txn = transaction.get()
    txn.savepoint(optimistic=True)


def _expandIncludes(context, formula):
    """ Recursively expand include statements
    """
    # First, we match any includes
    r = re.compile('^#Plomino (import|include) (.+)$', re.MULTILINE)

    matches = r.findall(formula)
    seen = []
    while matches:
        for include, scriptname in matches:

            scriptname = scriptname.strip()
            # Now, we match only *this* include; don't match script names
            # that are prefixes of other script names
            exact_r = re.compile(
                    '^#Plomino %s %s\\b' % (include, scriptname),
                    re.MULTILINE)

            if scriptname in seen:
                # Included already, blank the include statement
                formula = exact_r.sub('', formula)
                continue

            seen.append(scriptname)
            try:
                db = context.getParentDatabase()
                script_code = db.resources._getOb(scriptname).read()
            except:
                logger.warning("expandIncludes> %s not found in resources" % scriptname)
                script_code = (
                        "#ALERT: %s not found in resources" % scriptname)

            formula = exact_r.sub(script_code, formula)

        matches = r.findall(formula)

    return formula

