from AccessControl import ClassSecurityInfo
from AccessControl.requestmethod import postonly
import base64
import codecs
import csv
from DateTime import DateTime
import glob
import json
import logging
import os
import transaction
from ZPublisher.HTTPRequest import FileUpload

from .config import (
    CREATE_PERMISSION,
    EDIT_PERMISSION,
    READ_PERMISSION,
    REMOVE_PERMISSION,
    MSG_SEPARATOR,
)
from .exceptions import PlominoReplicationException
from .utils import StringToDate, DateToString

logger = logging.getLogger("Replication")

PLOMINO_IMPORT_SEPARATORS = {
    'semicolon (;)': ';',
    'comma (,)': ',',
    'tabulation': '\t',
    'white space': ' ',
    'end of line': '\n',
    'dash (-)': '-',
}


class ReplicationManager:
    """ Plomino document import/export features
    """

    security = ClassSecurityInfo()

    security.declareProtected(EDIT_PERMISSION, 'manage_importation')

    def manage_importation(self, REQUEST=None):
        """ CSV import form manager.
        """
        error = False
        actionType = REQUEST.get('actionType', None)
        self.resetReport()

        if actionType == 'import':
            # get file name
            try:
                infoMsg = self.processImport(REQUEST)
            except PlominoReplicationException, e:
                infoMsg = 'error while importing: %s%s' % (
                    e, MSG_SEPARATOR)
                error = True
        else:
            infoMsg = '%s: unmanaged action%s' % (
                actionType, MSG_SEPARATOR)
            error = True

        self.writeMessageOnPage(infoMsg, REQUEST, error)
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/DatabaseReplication')

    security.declarePublic('getSeparators')

    def getSeparators(self):
        """ Returns the separator list
        """
        return PLOMINO_IMPORT_SEPARATORS

    security.declareProtected(EDIT_PERMISSION, 'processImport')

    @postonly
    def processImport(self, REQUEST):
        """ Process the importation.
        """
        if not REQUEST:
            return 'REQUEST required'

        formName = REQUEST.get('formSelected', None)
        separatorName = REQUEST.get('separator', None)
        fileToImport = REQUEST.get('import_file', None)
        file_encoding = REQUEST.get('file_encoding', "utf-8")

        # form name
        if not formName:
            raise PlominoReplicationException('form required')

        # form obj
        form = self.getForm(formName)
        if not form:
            raise PlominoReplicationException(
                "Form '%s' not found" % formName)

        # separator
        separator = PLOMINO_IMPORT_SEPARATORS.get(separatorName)
        if not separator:
            raise PlominoReplicationException('separator not found')

        # file
        if not fileToImport:
            raise PlominoReplicationException('file required')

        # check type
        if not isinstance(fileToImport, FileUpload):
            raise PlominoReplicationException('unrecognized file uploaded')

        # parse
        fileContent = self.parseFile(
            fileToImport, formName, separator, file_encoding)

        nbDocDone, nbDocFailed = self.importCsv(fileContent)

        infoMsg = ("%s processed: %s document(s) imported, "
            "%s document(s) failed." % (
                fileToImport.filename,
                nbDocDone,
                nbDocFailed))

        return infoMsg

    security.declareProtected(EDIT_PERMISSION, 'processImport')

    def processImportAPI(
        self,
        formName,
        separator,
        fileToImport,
        file_encoding='utf-8'
    ):
        """ Process import API method.
        """
        # form name
        if not formName:
            raise PlominoReplicationException('form required')

        # form obj
        formObj = self.getForm(formName)
        if not formObj:
            raise PlominoReplicationException(
                'form %s not found' % formName)

        # separator
        if not separator:
            raise PlominoReplicationException('separator required')

        # file
        if not fileToImport:
            raise PlominoReplicationException('file required')

        # parse and import
        fileContent = self.parseFile(fileToImport, formName, separator,
                file_encoding)

        nbDocDone, nbDocFailed = self.importCsv(fileContent)
        logger.info(
            'Import processed: %s document(s) imported, '
            '%s document(s) failed.' % (nbDocDone, nbDocFailed))

    security.declareProtected(EDIT_PERMISSION, 'parseFile')

    def parseFile(
        self, fileToImport, formName, separator, file_encoding='utf-8'
    ):
        """ Read CSV file.
        Assume that we have a header line.
        Each line represents a document. Set `Form` to formName.
        """
        result = []
        try:
            if not fileToImport:
                raise PlominoReplicationException('file not set')

            if not separator:
                raise PlominoReplicationException('separator not set')

            # Use the python CSV module
            if not isinstance(fileToImport, basestring):
                fileToImport = fileToImport.readlines()
            reader = csv.DictReader(
                fileToImport,
                delimiter=separator)

            # Add the form name and copy reader values
            for line in reader:
                docInfos = {}

                # add form name
                docInfos['Form'] = formName

                # copy col values
                for col in line:
                    v = line[col]
                    if not v:
                        v = u''
                    docInfos[col] = v.decode(file_encoding)

                # add doc infos to result
                result.append(docInfos)

            return result

        except PlominoReplicationException, e:
            raise PlominoReplicationException(
                'error while parsing file (%s)' % (e)
            )

    security.declareProtected(EDIT_PERMISSION, 'importCsv')

    def importCsv(self, fileContent):
        """ Import CSV from content parsed.
        """
        nbDocDone = 0
        nbDocFailed = 0

        i = 2
        logger.info("Documents count: %d" % len(fileContent))
        txn = transaction.get()
        for docInfos in fileContent:
            try:
                # create doc
                doc = self.createDocument()
                # fill it
                form = self.getForm(docInfos['Form'])
                form.readInputs(
                    doc,
                    docInfos,
                    process_attachments=False,
                    applyhidewhen=False)
                doc.setItem('Form', docInfos['Form'])
                # add items that don't correspond to any field
                computedItems = doc.getItems()
                for info in docInfos:
                    if info not in computedItems:
                        v = docInfos[info]
                        if isinstance(v, str):
                            v.decode('utf-8')
                        doc.setItem(info, v)
                doc.save(creation=True, refresh_index=True)
                # count
                nbDocDone = nbDocDone + 1

            except PlominoReplicationException, e:
                nbDocFailed = nbDocFailed + 1
                self.addToReport(i, e, True)

            # next
            i = i + 1
            if not nbDocDone % 100:
                txn.savepoint(optimistic=True)
                logger.info(
                    "%d documents imported successfully, "
                    "%d errors(s) ...(still running)" % (
                        nbDocDone, nbDocFailed))
        txn.commit()
        logger.info(
            "Importation finished: %d documents imported successfully, "
            "%d document(s) not imported" % (nbDocDone, nbDocFailed))

        # result sent
        return (nbDocDone, nbDocFailed)

    security.declarePublic('getReport')

    def getReport(self):
        """ Returns last importation report
        """
        if not (hasattr(self, 'importReport')):
            self.importReport = None
        return self.importReport

    security.declareProtected(EDIT_PERMISSION, 'resetReport')

    def resetReport(self):
        """ Clears report
        """
        self.importReport = None

    security.declareProtected(EDIT_PERMISSION, 'addToReport')

    def addToReport(self, lineNumber, infoMessage, error=False):
        """ Adds entry to report
        """
        if not self.getReport():
            self.importReport = []
        if error:
            state = 'error'
        else:
            state = 'success'

        self.importReport.append({
            'line': lineNumber,
            'state': state,
            'infoMsg': infoMessage})

    security.declareProtected(READ_PERMISSION, 'manage_exportAsJSON')

    def manage_exportAsJSON(self, REQUEST):
        """
        """
        restricttoview = REQUEST.get("restricttoview", "")
        if restricttoview:
            v = self.getView(restricttoview)
            docids = [b.id for b in v.getAllDocuments(getObject=False)]
        else:
            docids = None
        if REQUEST.get('targettype') == "file":
            REQUEST.RESPONSE.setHeader('content-type', 'application/json')
            if restricttoview:
                label = restricttoview
            else:
                label = "all"
            REQUEST.RESPONSE.setHeader(
                "Content-Disposition",
                "attachment; filename=%s-%s-documents.json" % (
                    self.id, label))
        return self.exportAsJSON(docids, REQUEST=REQUEST)

    security.declareProtected(READ_PERMISSION, 'exportAsJSON')

    def exportAsJSON(
        self, docids=None, targettype='file', targetfolder='', REQUEST=None
    ):
        """ Export documents to JSON.
        The targettype can be file or folder.
        If supplied, the values on REQUEST override keyword parameters.
        """
        if REQUEST:
            targettype = REQUEST.get('targettype', 'file')
            targetfolder = REQUEST.get('targetfolder')
            str_docids = REQUEST.get("docids")
            if str_docids:
                docids = str_docids.split("@")

        if docids:
            docs = [self.getDocument(i) for i in docids]
        else:
            docs = self.getAllDocuments()

        if targettype == 'file':
            data = []
            for doc in docs:
                data.append(self.exportDocumentAsJSON(doc))

            if REQUEST is not None:
                REQUEST.RESPONSE.setHeader('content-type', 'application/json')
            return json.dumps(data)

        if targettype == 'folder':
            if REQUEST:
                targetfolder = REQUEST.get('targetfolder')

            exportpath = os.path.join(targetfolder, self.id)
            if os.path.isdir(exportpath):
                # remove previous export
                for f in glob.glob(os.path.join(exportpath, "*.json")):
                    os.remove(f)
            else:
                os.makedirs(exportpath)

            for doc in docs:
                docfilepath = os.path.join(exportpath, (doc.id + '.json'))
                logger.info("Exporting %s" % docfilepath)
                data = self.exportDocumentAsJSON(doc)
                self.saveFile(docfilepath, json.dumps(data))

    @staticmethod
    def saveFile(path, content):
        fileobj = codecs.open(path, "w", "utf-8")
        fileobj.write(content)
        fileobj.close()

    security.declareProtected(READ_PERMISSION, 'exportDocumentAsJSON')

    def exportDocumentAsJSON(self, doc):
        """
        """
        data = {
            'id': doc.id,
            'lastmodified': doc.getLastModified(asString=True),
        }
        # export items
        items_data = {}
        for (id, value) in doc.items.items():
            classname = value.__class__.__name__
            if classname == "DateTime":
                value = DateToString(value, format="%Y-%m-%dT%H:%M:%S")
            items_data[id] = {
                'class': classname,
                'value': value,
            }
        data['items'] = items_data

        # export attached files
        files = []
        for f in doc.getFilenames():
            attached_file = doc.getfile(f)
            if not attached_file:
                continue
            file_data = {
                'id': f,
                'contenttype': getattr(attached_file, 'content_type', ''),
                'data': str(attached_file).encode('base64'),
            }
            files.append(file_data)
        data['files'] = files

        return data

    security.declareProtected(REMOVE_PERMISSION, 'manage_importFromJSON')

    @postonly
    def manage_importFromJSON(self, REQUEST):
        """
        """
        (imports, errors) = self.importFromJSON(REQUEST=REQUEST)
        self.writeMessageOnPage(
            "%d documents imported successfully, "
            "%d document(s) not imported" % (
                imports, errors),
            REQUEST, error=False)
        REQUEST.RESPONSE.redirect(self.absolute_url() + "/DatabaseReplication")

    security.declareProtected(REMOVE_PERMISSION, 'importFromJSON')

    @postonly
    def importFromJSON(
        self,
        jsonstring=None,
        sourcetype='sourceFile',
        from_file=None,
        from_folder=None,
        REQUEST=None
    ):
        """ Import documents from JSON.

        The documents can be provided in a number of ways:
        - As a single JSON string ('jsonstring' parameter). If supplied,
          this governs.
        - As a source file (default).
          - If 'REQUEST=None', the file should be supplied via the
            'from_file' parameter.
          - Otherwise, REQUEST is checked for a 'filename' key, and the file
            is looked for under this key.
          - If there is no 'filename' key, we look for the file under the
            'file' key.
        - As a directory on the server ('source_type=folder'). In this case,
          the 'from_folder' parameter needs to be specified.
        """
        # TODO: This calling protocol is too complicated.
        logger.info("Start documents import")
        self.setStatus("Importing documents (0%)")
        txn = transaction.get()
        json_sources = []
        if jsonstring:
            jsonstring_arg = True
            json_sources = [jsonstring]
        else:
            jsonstring_arg = False
            if REQUEST:
                sourcetype = REQUEST.get('sourcetype', sourcetype)
            if sourcetype == 'sourceFile':
                if REQUEST:
                    filename = REQUEST.get('filename')
                    if filename:
                        # exportDocumentPush
                        filecontent = REQUEST.get(filename)
                    else:
                        # DatabaseReplication.pt input:
                        filecontent = REQUEST.get('file')
                    json_sources = [filecontent]
                elif from_file:
                    json_sources = [from_file]
            elif sourcetype == 'folder':
                if REQUEST:
                    from_folder = REQUEST.get("from_folder")
                json_sources = glob.glob(os.path.join(from_folder, '*.json'))

        files_counter = 0
        errors = 0
        imports = 0

        # json_sources contains either:
        # - a string, or
        # - FileUpload objects and/or filenames.
        for source in json_sources:
            if jsonstring_arg:
                jsonstring = source
            else:
                if hasattr(source, 'read'):
                    cte = source.headers.get('content-transfer-encoding')
                    if cte == 'base64':
                        jsonstring = base64.decodestring(source.read())
                    else:
                        jsonstring = source.read()
                else:
                    fileobj = codecs.open(source, 'r', 'utf-8')
                    jsonstring = fileobj.read().encode('utf-8')

            documents = json.loads(jsonstring)
            total_docs = len(documents)
            if total_docs > 1:
                logger.info("Documents count: %d" % total_docs)
            docs_counter = 0
            files_counter = files_counter + 1

            for docdata in documents:
                docid = docdata['id']
                try:
                    if docid in self.documents:
                        self.documents._delOb(docid)
                    self.importDocumentFromDict(docdata)
                    imports = imports + 1
                except PlominoReplicationException, e:
                    logger.info('error while importing %s (%s)' % (docid, e))
                    errors = errors + 1
                docs_counter = docs_counter + 1
                if docs_counter == 100:
                    self.setStatus("Importing documents (%d%%)" %
                            (100 * docs_counter / total_docs))
                    txn.savepoint(optimistic=True)
                    docs_counter = 0
                    logger.info("%d documents imported successfully, "
                            "%d errors(s) ... (still running)" % (
                                imports, errors))
            if files_counter == 100:
                self.setStatus("Importing documents (%s)" % files_counter)
                txn.savepoint(optimistic=True)
                files_counter = 0
                logger.info("%d documents imported successfully, "
                        "%d errors(s) ... (still running)" % (
                            imports, errors))

        self.setStatus("Ready")
        logger.info("Importation finished: "
                "%d documents imported successfully, "
                "%d document(s) not imported" % (imports, errors))
        txn.commit()

        return (imports, errors)

    security.declareProtected(CREATE_PERMISSION, 'importDocumentFromDict')

    def importDocumentFromDict(self, data):
        docid = data['id'].encode('ascii')
        lastmodified = DateTime(data['lastmodified'])
        doc = self.createDocument(docid)

        # restore items
        items_data = data['items']
        for key in items_data.keys():
            classname = items_data[key]['class']
            value = items_data[key]['value']
            if classname == 'DateTime':
                value = StringToDate(value[:19], format="%Y-%m-%dT%H:%M:%S")
            doc.setItem(key, value)

        # restore files
        for file_data in data["files"]:
            filename = file_data['id']
            contenttype = file_data['contenttype']
            doc.setfile(
                file_data['data'].decode('base64'),
                filename=filename,
                overwrite=True,
                contenttype=contenttype)

        doc.save(onSaveEvent=False)
        doc.plomino_modification_time = lastmodified
