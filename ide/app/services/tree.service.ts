import { Subject } from 'rxjs/Rx';
import { LogService } from './log.service';
import { PlominoHTTPAPIService } from './http-api.service';
import { Injectable } from '@angular/core';
import { Response } from '@angular/http';
// import { BehaviorSubject } from 'rxjs/BehaviorSubject';
import { Observable } from 'rxjs/Observable';

@Injectable()
export class TreeService {
    // latestId: number = 1;
    // private tree$: BehaviorSubject<any> = new BehaviorSubject(null);
    private tree$: Subject<any> = new Subject();

    constructor(
      private http: PlominoHTTPAPIService,
      private log: LogService,
    ) { 
        this.updateTree();
    }
    
    getTree(): Observable<any> {
        return this.tree$.asObservable();
    }

    addUniqueIdsForForms(data: any) {
        if(!Array.isArray(data) || !data[0])
            return data;

        // let id = 1;

        data[0].children.forEach((item: any) => {
          item.formUniqueId = this.generateHash(
            item.url + item.type
          );
            // item.formUniqueId = id++;
            // this.latestId = id;
        });

        return data;
    }

    updateTree(): Promise<any> {
      this.log.info('calling designtree...');

      const call$ = this.http.get("../../@@designtree").map((res: Response) => {
        this.log.info('http response from designtree received', res);
        if (res.url && res.url.indexOf('came_from=') !== -1) {
          /**
           * the user is not authorised
           * redirect to auth
           */
          let redirectURL = res.url.replace(/(came_from=).+?$/, '$1');
          redirectURL = `${ redirectURL }${ encodeURIComponent(window.location.href) }`; 
          this.log.info('redirect to', redirectURL);
          window.location.href = redirectURL;
        }
        return res.json();
      });

      return new Promise((resolve, reject) => {
        call$.catch((err: any) => {
          this.log.warn('REJECTED PROMISE', err);
          reject(err);
          throw err;
        })
        .subscribe((response: any) => {
          this.log.info('work with prepared http response from designtree', response);
          const ids = this.addUniqueIdsForForms(response);
          this.log.info('sending to subscribers unique ids', ids);
          this.tree$.next(ids);
          resolve(ids);
        });
      });
    }

    private generateHash(str: string): number {
      let hash = 0, i, chr;
      if (str.length === 0) return hash;
      for (i = 0; i < str.length; i++) {
        chr   = str.charCodeAt(i);
        hash  = ((hash << 5) - hash) + chr;
        hash |= 0; // Convert to 32bit integer
      }
      return hash;
    }
}
