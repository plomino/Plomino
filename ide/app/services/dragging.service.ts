import { Injectable } from '@angular/core';

import { Subject } from 'rxjs/Subject';
import { Observable } from 'rxjs/Observable';

@Injectable()
export class DraggingService {
  draggingData$: Subject<any> = new Subject<any>();

  constructor() { }
  
  setDragging(data: any): void {
    this.draggingData$.next(data);
  }

  getDragging(): Observable<any> {
    return this.draggingData$.asObservable();
  }
}