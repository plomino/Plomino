import gviz_api

def getGoogleDataSourceContent(plominoview, paths=None):
    """ return google.visualization.Query response content
    """
    description = {"docurl": ('string', '')}
    columns = plominoview.getColumns()
    for col in columns:
        description[col.id] = ('string', col.Title())
    
    data = []
    docs = plominoview.getAllDocuments()
    if paths is not None:
        docs = [doc for doc in docs if doc.getPath() in paths]
    for doc in docs:
        row = {}
        row['docurl'] = doc.getPath()
        for col in columns:
            row[col.id] = str(getattr(doc,"PlominoViewColumn_%s_%s" % (plominoview.id, col.id)))
        data.append(row)
    
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)
    
    return data_table.ToJSonResponse(columns_order=['docurl']+[col.id for col in columns])
