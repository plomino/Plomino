import { Injectable } from '@angular/core';

@Injectable()
export class PlominoDBService {

  constructor() { }

  getDBLink() {
    return `${ 
      window.location.pathname
      .replace('++resource++Products.CMFPlomino/ide/', '')
      .replace('/index.html', '')
    }`;
  }
}
