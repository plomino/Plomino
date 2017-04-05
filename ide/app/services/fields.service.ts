import { LogService } from './log.service';
import { PlominoHTTPAPIService } from './http-api.service';
import { Response } from '@angular/http';
import { Injectable } from '@angular/core';

import { Subject } from 'rxjs/Subject';
import { Observable } from 'rxjs/Observable';

@Injectable()
export class FieldsService {
  viewColumnInserted: Subject<string> = new Subject<string>();
  viewActionInserted: Subject<string> = new Subject<string>();
  private insertionStream$: Subject<InsertFieldEvent> 
    = new Subject<InsertFieldEvent>();
  private updatesStream$: Subject<PlominoFieldUpdatesStreamEvent> 
    = new Subject<PlominoFieldUpdatesStreamEvent>();
  
  constructor(private http: PlominoHTTPAPIService, private log: LogService) { }

  onNewColumn() {
    return this.viewColumnInserted.asObservable();
  }

  onNewAction() {
    return this.viewActionInserted.asObservable();
  }
  
  insertField(field: InsertFieldEvent) {
    this.log.info('insertField', field);
    this.insertionStream$.next(field);
  }

  updateField(
    fieldData: PlominoFieldRepresentationObject,
    newFieldData: PlominoFieldSettingsFormDataObject,
    id: string
  ) {
    this.updatesStream$.next(<PlominoFieldUpdatesStreamEvent> {
      fieldData: fieldData,
      newData: newFieldData,
      newId: id
    });
  }

  listenToUpdates(): Observable<PlominoFieldUpdatesStreamEvent> {
    return this.updatesStream$.asObservable();
  }

  getTemplate(formUrl: string, widgetType: string) {
    return this.http.get(
      `${formUrl}/@@tinyform/example_widget?widget_type=${widgetType}`,
      'fields.service.ts getTemplate'
    )
    .map((response: Response) => {
      return response.json();
    });
  }

  getInsertion(): Observable<InsertFieldEvent> {
    return this.insertionStream$.asObservable();
  }
}
