import { URLManagerService } from './url-manager.service';
import { Injectable } from '@angular/core';

@Injectable()
export class PlominoApplicationLoaderService {

  private shouldBeLoaded: string[] = ['app.component', 'material'];
  private isLoaded: boolean = false;

  constructor(private urlManager: URLManagerService) {
    window['materialPromise'].then(() => {
      this.markLoaded('material');
    });
  }

  markLoaded(key: string) {
    if (!this.isLoaded) {
      this.shouldBeLoaded = this.shouldBeLoaded.filter((e) => e !== key);
  
      if (!this.shouldBeLoaded.length) {
        this.onLoad();
      }
    }
  }

  private onLoad() {
    this.isLoaded = true;
    setTimeout(() => {
      $('#application-loader').remove();
      this.urlManager.restoreTabsFromURL();
    }, 300);
  }
}
