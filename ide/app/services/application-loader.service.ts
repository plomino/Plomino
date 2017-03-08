import { Injectable } from '@angular/core';

@Injectable()
export class PlominoApplicationLoaderService {

  private shouldBeLoaded: string[] = ['app.component', 'material'];

  constructor() {
    window['materialPromise'].then(() => {
      this.markLoaded('material');
    });
  }

  markLoaded(key: string) {
    this.shouldBeLoaded = this.shouldBeLoaded.filter((e) => e !== key);

    if (!this.shouldBeLoaded.length) {
      this.onLoad();
    }
  }

  private onLoad() {
    setTimeout(() => {
      $('#application-loader').remove();

      const splitHash = window.location.hash.split('form=');
      const formLink = splitHash.pop();
      
      if (splitHash.length && formLink && formLink !== 'form=') {
        $(`.tree-node--name:contains("${ formLink }")`).click();
      }
    }, 300);
  }
}
