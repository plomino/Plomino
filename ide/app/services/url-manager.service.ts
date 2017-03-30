import { LogService } from './log.service';
import { Injectable } from '@angular/core';

@Injectable()
export class URLManagerService {

  constructor(private log: LogService) { }

  rebuildURL(openedTabs: PlominoTab[]): void {
    const url = openedTabs.map((tab) => tab.url.split('/').pop()).join(',');
    this.setURL(url);
  }

  restoreTabsFromURL(): void {
    for (let urlItem of this.parseURLString()) {
      const $resource = $(`.tree-node--name:contains("${ urlItem }")`)
        .filter((i, node: HTMLElement) => $(node).text().trim() === urlItem);

      if ($resource.parent().hasClass('tree-node--is-view')) {
        $resource.parent().get(0).dispatchEvent(new Event('mousedown'));
        this.log.info('opening view...', urlItem);
      }
      else {
        $resource.click();
        this.log.info('opening form...', urlItem);
      }
    }
  }

  private parseURLString(): string[] {
    const result = window.location.hash.replace('#t=', '').split(',');
    return result.length && Boolean(result[0]) ? result : [];
  }

  private setURL(url: string): void {
    window.location.hash = url ? `#t=${ url }` : '';
  }
}
