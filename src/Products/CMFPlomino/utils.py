# -*- coding: utf-8 -*-
import cgi
import csv
import decimal as std_decimal
import htmlentitydefs
import logging
import Missing
import re
import transaction
import urllib

from cStringIO import StringIO
from datetime import datetime
from dateutil.parser import parse
from email.Header import Header
from email import message_from_string
from jsonutil import jsonutil as json
from types import StringTypes
from zope import component

from AccessControl import ClassSecurityInfo
from AccessControl.unauthorized import Unauthorized
try:
    from AccessControl.class_init import InitializeClass
except ImportError:
    from App.class_init import InitializeClass
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import normalizeString as utils_normalizeString

try:
    from plone.app.upgrade import v40  # noqa: ignore=F401
    HAS_PLONE40 = True
except ImportError:
    HAS_PLONE40 = False

from Products.CMFPlomino.config import TIMEZONE, SCRIPT_ID_DELIMITER
from Products.CMFPlomino.interfaces import IPlominoSafeDomains

logger = logging.getLogger('Plomino')

severity_map = {
    'info': logging.INFO,
    'warning': logging.WARNING,
    'debug': logging.DEBUG
}


def Log(message, summary='', severity='info', exc_info=False):
    """Write a message to the event log. Useful from formulas.

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
    """Return the date as string using the given format.

    Pass in database object to use default format.
    """
    if not format:
        if db:
            format = db.datetime_format
        if not format:
            format = '%Y-%m-%d'
    return d.toZone(TIMEZONE).strftime(format)


def StringToDate(str_d, format='%Y-%m-%d', db=None):
    """Parse the string using the given format and return the date.

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
    except ValueError as e:
        # XXX: Just let DateTime guess.
        dt = parse(DateTime(str_d).ISO())
        logger.info('StringToDate> %s, %s, %s, guessed: %s' % (
            str(str_d),
            format,
            repr(e),
            repr(dt)))
    return DateTime(dt).toZone(TIMEZONE)


def DateRange(d1, d2):
    """Return all the dates from ``d1`` to ``d2`` (inclusive).

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
    """Current date and time"""
    return DateTime()


def DatetimeToJS(python_format, split=False):
    """Convert python datetime format to js format

    :param python_format: python datetime format

    Python  JS Time format
    -       d	    Date of the month	1 – 31
    %d      dd	    Date of the month with a leading zero	01 – 31
    %a      ddd	    Day of the week in short form	Sun – Sat
    %A      dddd	Day of the week in full form	Sunday – Saturday
    -       m	    Month of the year	1 – 12
    %m      mm	    Month of the year with a leading zero	01 – 12
    %b      mmm     Month name in short form	Jan – Dec
    %B      mmmm    Month name in full form	January – December
    %y      yy	    Year in short form *	00 – 99
    %Y      yyyy	Year in full form	2000 – 2999

    Python  JS Time format
    -       h	    Hour in 12-hour format	1 – 12
    %I      hh	    Hour in 12-hour format with a leading zero	01 – 12
    -       H	    Hour in 24-hour format	0 – 23
    %H      HH	    Hour in 24-hour format with a leading zero	00 – 23
    %M      i	    Minutes	00 – 59
    -       a	    Day time period	a.m. / p.m.
    %p      A	    Day time period in uppercase	AM / PM

    :param split: split the string into data and time strings

    :return: js datetime format in one string or two strings
    """
    replacements = {
        r'%d': 'dd',
        r'%a': 'ddd',
        r'%A': 'dddd',
        r'%m': 'mm',
        r'%b': 'mmm',
        r'%B': 'mmmm',
        r'%y': 'yy',
        r'%Y': 'yyyy',
        r'%I': 'hh',
        r'%H': 'HH',
        r'%M': 'i',
        r'%p': 'A',
    }

    def conversion(input):
        output = input
        for key, value in replacements.items():
            while key in output:
                output = output.replace(key, value)
        return output

    if not python_format:
        return ''

    datetime_format = python_format

    if split:
        got_date = False
        date_header = ''
        got_time = False
        time_header = ''

        if '%d' in datetime_format:
            got_date = True
            date_header = '%d'
        elif '%m' in datetime_format:
            got_date = True
            date_header = '%m'
        elif '%b' in datetime_format:
            got_date = True
            date_header = '%b'
        elif '%B' in datetime_format:
            got_date = True
            date_header = '%B'
        elif '%y' in datetime_format:
            got_date = True
            date_header = '%y'
        elif '%Y' in datetime_format:
            got_date = True
            date_header = '%Y'
        date_header_index = datetime_format.find(date_header)

        if '%I' in datetime_format:
            got_time = True
            time_header = '%I'
        elif '%H' in datetime_format:
            got_time = True
            time_header = '%H'
        time_header_index = datetime_format.find(time_header)

        if got_date and got_time:
            if date_header_index < time_header_index:
                date_split = datetime_format[:time_header_index]
                time_split = datetime_format[time_header_index:]
            else:
                if '%p' in datetime_format:
                    time_header_index = datetime_format.find('%p')
                elif '%M' in datetime_format:
                    time_header_index = datetime_format.find('%M')
                time_split = datetime_format[:time_header_index + 2]
                date_split = datetime_format[time_header_index + 2:]
            date_format = conversion(date_split.strip())
            time_format = conversion(time_split.strip())
            datetime_format = (date_format, time_format)
        elif got_date:
            date_format = conversion(datetime_format)
            datetime_format = (date_format, '')
        elif got_time:
            time_format = conversion(datetime_format)
            datetime_format = ('', time_format)
        else:
            datetime_format = ('', '')
    else:
        datetime_format = conversion(datetime_format)

    return datetime_format


def sendMail(
    db,
    recipients,
    title,
    message_in,
    sender=None,
    cc=None,
    bcc=None,
    immediate=False,
    msg_format='html'
):
    """Send an email"""
    host = getToolByName(db, 'MailHost')
    mtype = 'html'
    if msg_format == 'html':
        message = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"' \
            ' "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'
        message = message + "<html>"
        message = message + message_in
        message = message + "</html>"
    elif msg_format == 'text':
        mtype = 'plain'
        message = message_in
    else:
        raise Exception('Invalid message format')

    if not sender:
        sender = db.getCurrentMember().getProperty("email")

    mail_message = message_from_string(asUnicode(message).encode('utf-8'))
    mail_message.set_charset('utf-8')
    mail_message.set_type("text/%s" % mtype)
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
            msg_type='text/%s' % mtype,
            immediate=immediate
        )
    else:
        host.secureSend(
            message,
            recipients,
            sender,
            subject=title,
            subtype=mtype,
            charset='utf-8'
        )


def userFullname(db, userid):
    """Try to return user fullname, else return userid.

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
    """Return user object."""
    return getToolByName(db, 'portal_membership').getMemberById(userid)


def PlominoTranslate(msgid, context, domain='CMFPlomino'):
    """Look up the translation for ``msgid`` in the current language."""
    translation_service = getToolByName(context, 'translation_service')
    # When will message be an exception?
    if isinstance(msgid, Exception):
        logging.info("msgid is an Exception: %s" % msgid)
        try:
            msgid = msgid[0]
        except (TypeError, IndexError):
            logging.exception(
                "Couldn't subscript msgid: %s" % msgid, exc_info=True)
            pass

    msg = translation_service.utranslate(
        msgid=msgid,
        domain=domain,
        context=context
    )
    # this converts unicode to site encoding:
    return translation_service.encode(msg)


def htmlencode(s):
    """Replace characters with their corresponding HTML entities."""
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
    """Call urllib.urlencode

    (Encode a sequence of two-element tuples or dictionary into a URL query
    string, does quoting.)
    """
    # TODO(ivanteoh): consider doseq parameter
    return urllib.urlencode(h)


def urlquote(s):
    """Call urllib.quote

    (quote('abc def') -> 'abc%20def')
    """
    return urllib.quote(s)


def cgi_escape(s):
    return cgi.escape(s)


def normalizeString(text, context=None, encoding=None):
    return utils_normalizeString(text, context, encoding)


def asList(x):
    """If not list, return x in a single-element list.

    .. note:: This will wrap falsy values like ``None`` or ``''`` in a list,
              making them truthy.
    """
    if isinstance(x, (list, tuple)):
        return x
    return [x]


def asUnicode(s):
    """Make sure ``s`` is unicode;

    Decode according to site encoding if needed.
    """
    if not isinstance(s, basestring):
        return unicode(s)
    from Products.CMFPlone.utils import safe_unicode
    return safe_unicode(s)
    # Doesn't work unless utils becomes a persistent tool.
    # translation_service = getToolByName(context, 'translation_service')
    # return translation_service.asunicodetype(s)


def csv_to_array(csvcontent, delimiter='\t', quotechar='"'):
    """``csvcontent`` may be a string or a file."""
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
    """Convert ``array`` (a list of lists) to a CSV string."""
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
    """Retrieve content from url"""
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
        f = urllib.urlopen(url, data)
        if asFile:
            return f.fp
        else:
            return f.read()
    else:
        raise Unauthorized(url)


def MissingValue():
    """Useful to test search results value

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


# From http://lsimons.wordpress.com/2011/03/17/stripping-illegal-characters-out-of-xml-in-python/  # noqa: ignore=E501
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
    """Expose the standard library's Decimal class. Useful for finances."""
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
    """Return the actual path from the request

    Useful in portlet context
    """
    if not hasattr(context, "REQUEST"):
        return None
    url = context.REQUEST.get("ACTUAL_URL")
    return context.REQUEST.physicalPathFromURL(url)


def actual_context(context, search="PlominoDocument"):
    """Return the actual context from the request

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
    """Translate content, if possible."""
    # TODO(ivanteoh): translate non-string content? Like dates?
    if not isinstance(content, basestring):
        return content

    request = getattr(context, 'REQUEST', None)
    if request and request.get("translation") == "off":
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
    """Return rowdata for a datagrid on a modal popup

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
        mapped_field_ids = [f.strip() for f in field.field_mapping.split(',')]
    rowdata_json = getattr(REQUEST, 'Plomino_datagrid_rowdata', None)
    if rowdata_json:
        rowdata = json.loads(
            urllib.unquote(rowdata_json).decode('raw_unicode_escape'))
    return mapped_field_ids, rowdata


def save_point():
    txn = transaction.get()
    txn.savepoint(optimistic=True)


def _expandIncludes(context, formula):
    """Recursively expand include statements"""
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
            except Exception:
                logger.warning(
                    "expandIncludes> %s not found in resources" % scriptname)
                script_code = (
                    "#ALERT: %s not found in resources" % scriptname)

            formula = exact_r.sub(script_code, formula)

        matches = r.findall(formula)

    return formula


def set_attr(obj, attr, value):
    return setattr(obj, attr, value)
