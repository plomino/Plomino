import { PlominoHTTPAPIService } from './http-api.service';
import { Injectable } from '@angular/core';
import { Response } from '@angular/http';
import { BehaviorSubject } from 'rxjs/BehaviorSubject';
import { Observable } from 'rxjs/Observable';

@Injectable()
export class TreeService {
    latestId: number = 1;
    private tree$: BehaviorSubject<any> = new BehaviorSubject(null);

    constructor(private http: PlominoHTTPAPIService) { 
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
            this.latestId = id;
        });

        return data;
    }

    updateTree() {
      return this.http
      .get("../../@@designtree")
      .map((res: Response) => {
        if (res.url && res.url.indexOf('came_from=') !== -1) {
          /**
           * the user is not authorised
           * redirect to auth
           */
          let redirectURL = res.url.replace(/(came_from=).+?$/, '$1');
          window.location.href = `${ redirectURL }${ encodeURIComponent(window.location.href) }`;
        }
        return res.json();
      })
      .forEach((response: any) => {
        this.tree$.next(this.addUniqueIdsForForms(response));
      });
    }
}
