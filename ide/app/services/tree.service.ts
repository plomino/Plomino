import { PlominoHTTPAPIService } from './http-api.service';
import { Injectable } from '@angular/core';
import { Response } from '@angular/http';
import { BehaviorSubject } from 'rxjs/BehaviorSubject';
import { Observable } from 'rxjs/Observable';

@Injectable()
export class TreeService {
    // latestId: number = 1;
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

        // let id = 1;

        data[0].children.forEach((item:any) => {
          item.formUniqueId = this.generateHash(
            item.url + item.type
          );
            // item.formUniqueId = id++;
            // this.latestId = id;
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

    private generateHash(str: string): number {
      var hash = 0, i, chr;
      if (str.length === 0) return hash;
      for (i = 0; i < str.length; i++) {
        chr   = str.charCodeAt(i);
        hash  = ((hash << 5) - hash) + chr;
        hash |= 0; // Convert to 32bit integer
      }
      return hash;
    }
}
