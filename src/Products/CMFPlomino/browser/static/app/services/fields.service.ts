import { Injectable } from '@angular/core';

import { Subject } from 'rxjs/Subject';
import { Observable } from 'rxjs/Observable';

@Injectable()
export class FieldsService {
  insertionStream$: Subject<any> = new Subject();
  
  constructor() { }
  
  insertField(field: any) {
    this.insertionStream$.next(field);
  }

  getInsertion(): Observable<any> {
    return this.insertionStream$.asObservable();
  }
}