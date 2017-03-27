import { Injectable } from '@angular/core';

@Injectable()
export class URLManagerService {

  constructor() { }

  rebuildURL(openedTabs: PlominoTab[]): void {
    const url = openedTabs.map((tab) => tab.url.split('/').pop()).join(',');
    this.setURL(url);
  }

  restoreTabsFromURL(): void {
    for (let urlItem of this.parseURLString()) {
      $(`.tree-node--name:contains("${ urlItem }")`)
        .filter((i, node: HTMLElement) => $(node).text().trim() === urlItem)
        .click();
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
