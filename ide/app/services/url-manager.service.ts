import { PlominoTabsManagerService } from './tabs-manager/index';
import { TabsService } from './tabs.service';
import { LogService } from './log.service';
import { Injectable } from '@angular/core';

@Injectable()
export class URLManagerService {

  constructor(
    private log: LogService,
    private tabsManagerService: PlominoTabsManagerService,
  ) { }

  rebuildURL(openedTabs: PlominoTabUnit[]): void {
    const url = openedTabs.map((tab) => tab.url.split('/').pop()).join(',');
    this.setURL(url);
  }

  restoreTabsFromURL(): void {
    const urlItems = this.parseURLString();

    if (urlItems.length) {
      for (let urlItem of urlItems) {
        window['materialPromise']
          .then(() => {
            const $resource = $(`.tree-node--name:contains("${ urlItem }")`)
              .filter((i, node: HTMLElement) => $(node).text().trim() === urlItem);
            $resource.click();
            setTimeout(() => {
              const $resource = $(`.tree-node--name:contains("${ urlItem }")`)
                .filter((i, node: HTMLElement) => $(node).text().trim() === urlItem);
              $resource.click();
            }, 100);
          });
      }
    }
  }

  parseURLString(): string[] {
    const result = window.location.hash.replace('#t=', '').split(',');
    return result.length && Boolean(result[0]) ? result : [];
  }

  private setURL(url: string): void {
    window.location.hash = url ? `#t=${ url }` : '';
  }
}
