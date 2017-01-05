import { Injectable } from '@angular/core';

import { Subject } from 'rxjs/Subject';
import { Observable } from 'rxjs/Observable';

@Injectable()
export class FieldsService {
  private insertionStream$: Subject<any> = new Subject();
  private updatesStream$: Subject<any> = new Subject();
  
  constructor() { }
  
  insertField(field: any) {
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

  getInsertion(): Observable<any> {
    return this.insertionStream$.asObservable();
  }
}