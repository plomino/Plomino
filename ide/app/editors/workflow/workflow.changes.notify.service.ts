import { Injectable } from '@angular/core';
import { Observable } from 'rxjs/Rx';
import { Subject } from 'rxjs/Subject';

@Injectable()
export class PlominoWorkflowChangesNotifyService {
  changesDetector: Subject<KVChangeEvent> = new Subject<KVChangeEvent>();
  onChangesDetect$: Observable<KVChangeEvent> = this.changesDetector.asObservable();
  constructor() { }
}
