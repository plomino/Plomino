import { Injectable } from "@angular/core";
import { Observable } from "rxjs/Rx";
import { Subject } from "rxjs/Subject";

@Injectable()
export class PlominoWorkflowChangesNotifyService {
    changesDetector: Subject<KVChangeEvent> = new Subject<KVChangeEvent>();
    onChangesDetect$: Observable<KVChangeEvent> = this.changesDetector.asObservable();
    runAdd: Subject<string> = new Subject<string>();
    runAdd$: Observable<string> = this.runAdd.asObservable();
    needSave: Subject<any> = new Subject<any>();
    needSave$: Observable<any> = this.needSave.asObservable();
    constructor() {}
}
