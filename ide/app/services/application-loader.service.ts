import { LogService } from './log.service';
import { URLManagerService } from './url-manager.service';
import { Injectable } from '@angular/core';

@Injectable()
export class PlominoApplicationLoaderService {

  private shouldBeLoaded: string[] = ['app.component', 'material'];
  private isLoaded = false;

  constructor(
    private urlManager: URLManagerService,
    private log: LogService,
  ) {
    window['materialPromise'].then(() => {
      this.markLoaded('material');
      this.log.info('material design received on the page');
    });
  }

  markLoaded(key: string) {
    this.log.info(key, 'is loaded');
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
