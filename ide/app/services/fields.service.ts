import { Http, Response } from '@angular/http';
import { Injectable } from '@angular/core';

import { Subject } from 'rxjs/Subject';
import { Observable } from 'rxjs/Observable';

@Injectable()
export class FieldsService {
  private insertionStream$: Subject<any> = new Subject();
  private updatesStream$: Subject<any> = new Subject();
  
  constructor(private http: Http) { }
  
  insertField(field: any) {
    console.info('insertField', field);
    this.insertionStream$.next(field);
  }

  updateField(fieldData: any, newFieldData: any, id: any) {
    this.updatesStream$.next({
      fieldData: fieldData,
      newData: newFieldData,
      newId: id
    });
  }

  listenToUpdates(): Observable<any> {
    return this.updatesStream$.asObservable();
  }

  getTemplate(formUrl: string, widgetType: string) {
    return this.http.get(`${formUrl}/@@tinyform/example_widget?widget_type=${widgetType}`)
    .map((response: Response) => {
      return response.json();
    });
  }

  getInsertion(): Observable<any> {
    return this.insertionStream$.asObservable();
  }
}
