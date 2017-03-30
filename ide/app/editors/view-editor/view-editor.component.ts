import { DraggingService } from './../../services/dragging.service';
import { PlominoBlockPreloaderComponent } from './../../utility/block-preloader';
import { FieldsService } from './../../services/fields.service';
import { TabsService } from './../../services/tabs.service';
import { DomSanitizationService, SafeHtml } from '@angular/platform-browser';
import { LogService } from './../../services/log.service';
import { Component, Input, ViewEncapsulation, OnInit, NgZone, ChangeDetectorRef } from '@angular/core';
import { PlominoViewsAPIService } from './views-api.service';

@Component({
  selector: 'plomino-view-editor',
  template: require('./plomino-view-editor.component.html'),
  styles: [require('./plomino-view-editor.css')],
  providers: [PlominoViewsAPIService],
  directives: [PlominoBlockPreloaderComponent],
  encapsulation: ViewEncapsulation.None,
})
export class PlominoViewEditorComponent implements OnInit {
  @Input() item: PlominoTab;
  viewSourceTable: SafeHtml;
  loading: boolean = true;
  subsetIds: string[] = [];
  
  constructor(
    private api: PlominoViewsAPIService,
    private log: LogService,
    private fieldsService: FieldsService,
    private tabsService: TabsService,
    private zone: NgZone,
    private dragService: DraggingService,
    private changeDetector: ChangeDetectorRef,
    protected sanitizer: DomSanitizationService,
  ) { }

  ngOnInit() {

    $('body').undelegate(
      `[data-url="${ this.item.url }"] .actionButtons input[type="button"]`,
      'click'
    );

    $('body').undelegate(
      `[data-url="${ this.item.url }"] .view-editor__column-header`,
      'click'
    );

    $('body').delegate(
      `[data-url="${ this.item.url }"] .actionButtons input[type="button"]`,
      'click', (event: JQueryMouseEventObject) => {
        this.onActionClick(event.target);
      });

    $('body').delegate(
      `[data-url="${ this.item.url }"] .view-editor__column-header`,
      'click', (event: JQueryMouseEventObject) => {
        this.onColumnClick(<HTMLElement> event.target);
      });

    this.reloadView();

    this.fieldsService.onNewColumn()
      .subscribe((response: string) => {
        if (response === this.item.url) {
          this.reloadView();
        }
      });
  }

  reloadView() {
    this.subsetIds = [];
    this.loading = true;

    this.api.fetchViewTable(this.item.url)
      .subscribe((fetchResult: [string, PlominoVocabularyViewData]) => {
        const html = fetchResult[0];
        const json = fetchResult[1];

        this.subsetIds = json.results.map(r => r.id);

        let $html = $(html);
        $html = $html.find('article');

        const $h1 = $html.find('.documentFirstHeading');
        $h1.replaceWith(`<h3>${ $h1.html() }</h3>`);

        $html.find('.formControls')
          .addClass('view-editor__actions')
          .removeClass('formControls');

        $html.find('th[data-column]').each((i, columnElement: HTMLElement) => {
          columnElement.classList.add('view-editor__column-header');
          columnElement.draggable = true;
        });

        $html.find('.actionButtons input[type="button"]')
          .addClass('mdl-button mdl-js-button mdl-button--primary mdl-button--raised')
          .attr('draggable', true)
          .removeAttr('onclick');

        $html.find('.actionButtons input[type="button"]:not([id])')
          .attr('disabled', 'disabled');
        
        $html.find('table')
          .removeAttr('class')
          .prepend('<thead></thead>');

        this.viewSourceTable = this.sanitizer
          .bypassSecurityTrustHtml($html.html());
        
        setTimeout(() => {

          /* attach indexes */
          json.results.forEach((result, index) => {
            (() => {
              if (result.Type === 'PlominoColumn') {
                return $(
                  `[data-url="${ this.item.url }"] th[data-column="${ result.id }"]`
                );
              }
              else if (result.Type === 'PlominoAction') {
                return $(
                  `[data-url="${ this.item.url }"] input#${ result.id }`
                );
              }
            })()
            .get(0).dataset.index = (index + 1).toString();
          });

          const $thead = $(`[data-url="${ this.item.url }"] table thead`);
          const $headRow = $(`[data-url="${ this.item.url }"] .header-row:first`);
          const totalColumns = $headRow.find('th').length;

          $headRow.appendTo($thead);

          $(`[data-url="${ this.item.url }"] table tbody tr`).each((t, trElement) => {
            const missed = totalColumns - $(trElement).find('td').length;

            if (missed) {
              for (let i = 0; i < missed; i++) {
                $(trElement).append('<td></td>');
              }
            }
          });

          $(`[data-url="${ this.item.url }"] table`)
            .addClass('mdl-data-table mdl-js-data-table ' 
              + 'mdl-shadow--2dp');

          this.zone.runOutsideAngular(() => {
            try {
              componentHandler.upgradeDom();
            } catch (e) {}
          });
        }, 200);

        setTimeout(() => this.afterLoad(), 300);
      });
  }

  afterLoad() {
    let draggable: HTMLElement = null;

    $(`[data-url="${ this.item.url }"] .view-editor__column-header`
        + `, [data-url="${ this.item.url }"] ` 
        + `.actionButtons input[type="button"]`)
      .each((i, element: HTMLElement) => {
        if (element.tagName === 'INPUT' && element.id) {
          /* action button */
          const actionElement = <HTMLInputElement> element;
          
          actionElement.ondragstart = (ev: DragEvent) => {
            $('.view-editor__action--drop-target')
              .removeClass('view-editor__action--drop-target');
            ev.dataTransfer.setData('text', 'a:' 
              + (<HTMLElement> ev.target).id);
            draggable = actionElement;

            this.dragService.followDNDType('existing-action');

            return true;
          };

          actionElement.ondrop = (ev: DragEvent) => {
            const dndType = this.dragService.dndType;
            if (dndType !== 'action' && dndType !== 'existing-action') {
              return true;
            }
            if (dndType === 'action') {
              /* insert action and do some math */
              const currentIndex = parseInt(actionElement.dataset.index, 10);
              const delta = (this.subsetIds.length - currentIndex) * -1;
              
              this.loading = true;
              this.api.addNewAction(this.item.url)
                .subscribe((response) => {
                  this.subsetIds.push(response.id);
                  this.api.reOrderItem(this.item.url, response.id, delta, this.subsetIds)
                    .subscribe(() => {
                      this.reloadView();
                    });
                })
            }
            const transfer = ev.dataTransfer.getData('text');

            if (transfer.indexOf('a:') !== -1) {
              this.loading = true;
              
              this.api.reOrderItem(this.item.url,
                draggable.id, 
                parseInt(actionElement.dataset.index, 10) - 
                parseInt(draggable.dataset.index, 10),
                this.subsetIds
              ).subscribe(() => {
                this.reloadView();
              });
            }

            return true;
          };

          actionElement.ondragover = (ev: DragEvent) => {
            ev.preventDefault();
          };

          actionElement.ondragenter = (ev: DragEvent) => {
            const dndType = this.dragService.dndType;
            if (dndType !== 'action' && dndType !== 'existing-action') {
              return true;
            }
            if (dndType === 'action') {
              /* insert shadow column after this btn */
              const $btn = $(ev.target);
              $btn.after(
                ` <input class="context mdl-button mdl-js-button
                  view-editor__action--drop-preview
                  mdl-button--primary mdl-button--raised"
                  value="default-action"
                  type="button">`
              );
            }
            $('.view-editor__action--drop-target')
              .removeClass('view-editor__action--drop-target');
            actionElement.classList.add('view-editor__action--drop-target');
            return true;
          };

          actionElement.ondragleave = (ev: DragEvent) => {
            const dndType = this.dragService.dndType;
            if (dndType !== 'action' && dndType !== 'existing-action') {
              return true;
            }
            if (dndType === 'action') {
              /* remove shadow action after this btn */
              const $btn = $(ev.target);
              $btn.next().remove();
            }
            actionElement.classList.remove('view-editor__action--drop-target');
            return true;
          };
        }
        else {
          /* view column */
          const columnElement = element;
          
          columnElement.ondragstart = (ev: DragEvent) => {
            $('.view-editor__column-header--drop-target')
              .removeClass('view-editor__column-header--drop-target');
            ev.dataTransfer.setData('text', 'c:' 
              + (<HTMLElement> ev.target).dataset.column);
            draggable = columnElement;

            this.dragService.followDNDType('existing-column');

            return true;
          };
          
          columnElement.ondrop = (ev: DragEvent) => {
            const dndType = this.dragService.dndType;
            if (dndType !== 'column' && dndType !== 'existing-column') {
              return true;
            }
            if (dndType === 'column') {
              /* insert column and do some math */
              const currentIndex = parseInt(columnElement.dataset.index, 10);
              const delta = (this.subsetIds.length + 1 - currentIndex) * -1;
              
              this.loading = true;
              this.api.addNewColumn(this.item.url)
                .subscribe((newId: string) => {
                  this.subsetIds.push(newId);
                  this.api.reOrderItem(this.item.url, newId, delta, this.subsetIds)
                    .subscribe(() => {
                      this.reloadView();
                    });
                })
            }
            const transfer = ev.dataTransfer.getData('text');

            if (transfer.indexOf('c:') !== -1) {
              this.loading = true;
              
              this.api.reOrderItem(this.item.url,
                draggable.dataset.column, 
                parseInt(columnElement.dataset.index, 10) - 
                parseInt(draggable.dataset.index, 10),
                this.subsetIds
              ).subscribe(() => {
                this.reloadView();
              });
            }

            return true;
          };

          columnElement.ondragover = (ev: DragEvent) => {
            ev.preventDefault();
          };

          columnElement.ondragenter = (ev: DragEvent) => {
            const dndType = this.dragService.dndType;
            if (dndType !== 'column' && dndType !== 'existing-column') {
              return true;
            }
            if (dndType === 'column') {
              /* insert shadow column after this td */
              const $td = $(ev.target);
              $td.after(
                `<td class="view-editor__column-header--drop-preview">
                  default-column
                </td>`
              );
            }
            $('.view-editor__column-header--drop-target')
              .removeClass('view-editor__column-header--drop-target');
            columnElement.classList.add('view-editor__column-header--drop-target');
            return true;
          };

          columnElement.ondragleave = (ev: DragEvent) => {
            const dndType = this.dragService.dndType;
            if (dndType !== 'column' && dndType !== 'existing-column') {
              return true;
            }
            if (dndType === 'column') {
              /* remove shadow column after this td */
              const $td = $(ev.target);
              $td.next().remove();
            }
            columnElement.classList.remove('view-editor__column-header--drop-target');
            return true;
          };
        }
      });
  
    this.loading = false;
    // this.changeDetector.markForCheck();
    // this.changeDetector.detectChanges();
  }

  onActionClick(actionElement: Element) {
    $('.view-editor__column-header--selected')
      .removeClass('view-editor__column-header--selected');
    $('.view-editor__action--selected')
      .removeClass('view-editor__action--selected');
    actionElement.classList.add('view-editor__action--selected');
    this.log.info('view action selected', actionElement);
    this.tabsService.selectField({
      id: `${ this.item.url.split('/').pop() }/${ actionElement.id }`,
      type: 'PlominoAction',
      parent: this.getDBLink()
    })
  }

  onColumnClick(columnElement: HTMLElement) {
    $('.view-editor__column-header--selected')
      .removeClass('view-editor__column-header--selected');
    $('.view-editor__action--selected')
      .removeClass('view-editor__action--selected');
    columnElement.classList.add('view-editor__column-header--selected');
    this.log.info('view column selected', columnElement);
    this.tabsService.selectField({
      id: `${ this.item.url.split('/').pop() }/${ columnElement.dataset.column }`,
      type: 'PlominoColumn',
      parent: this.getDBLink()
    })
  }

  private getDBLink() {
    return `${ 
      window.location.pathname
      .replace('++resource++Products.CMFPlomino/ide/', '')
      .replace('/index.html', '')
    }`;
  }
}
