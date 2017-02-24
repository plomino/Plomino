import {
    Injectable
} from '@angular/core';

import {
    Http,
    Response
} from '@angular/http';

import { BehaviorSubject } from 'rxjs/BehaviorSubject';
import { Observable } from 'rxjs/Observable';

@Injectable()
export class TreeService {
    private tree$: BehaviorSubject<any> = new BehaviorSubject(null);

    constructor(private http: Http) { 
        this.updateTree();
    }
    
    getTree(): Observable<any> {
        return this.tree$.asObservable();
    }

    addUniqueIdsForForms(data:any) {
        if(!Array.isArray(data) || !data[0])
            return data;

        let id = 1;

        data[0].children.forEach((item:any) => {
            item.formUniqueId = id++;
        });

        return data;
    }

    updateTree() {
      return this.http
      .get("../../@@designtree")
      .map((res: Response) => res.json())
      .forEach((response) => {
        this.tree$.next(this.addUniqueIdsForForms(response));
      });
    }
}
