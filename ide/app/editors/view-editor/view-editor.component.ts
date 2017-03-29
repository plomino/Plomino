import { PlominoBlockPreloaderComponent } from './../../utility/block-preloader';
import { FieldsService } from './../../services/fields.service';
import { TabsService } from './../../services/tabs.service';
import { DomSanitizationService, SafeHtml } from '@angular/platform-browser';
import { LogService } from './../../services/log.service';
import { Component, Input, ViewEncapsulation, OnInit, NgZone } from '@angular/core';
import { PlominoViewsAPIService } from './views-api.service';

@Component({
  selector: 'plomino-view-editor',
  template: require('./plomino-view-editor.component.html'),
  styles: [`
  .view-editor {
    position: relative;
  }

  .view-editor__inner {
    overflow: auto;
    position: absolute;
    max-width: 95%;
    padding-bottom: 20px;
  }

  .view-editor__actions {
    margin-bottom: 15px;
  }

  .view-editor__column-header {
    cursor: pointer;
    user-select: none;
    -webkit-user-select: none;
  }

  .view-editor__column-header:hover,
  .view-editor__column-header--selected {
    background: rgb(63,81,181);
    color: white !important;
  }

  .view-editor__column-header--selected,
  .view-editor__column-header--drop-target,
  .view-editor__action--selected {
    outline: dotted 2px gray;
  }
  `],
  providers: [PlominoViewsAPIService],
  directives: [PlominoBlockPreloaderComponent],
  encapsulation: ViewEncapsulation.None,
})
export class PlominoViewEditorComponent implements OnInit {
  @Input() item: PlominoTab;
  viewSourceTable: SafeHtml;
  loading: boolean = true;
  
  constructor(
    private api: PlominoViewsAPIService,
    private log: LogService,
    private fieldsService: FieldsService,
    private tabsService: TabsService,
    private zone: NgZone,
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
      .subscribe((response: AddFieldResponse) => {
        if (response.parent['@id'] === this.item.url) {
          this.reloadView();
        }
      });
  }

  reloadView() {
    this.loading = true;
    this.api.fetchViewTableHTML(this.item.url)
      .subscribe((html: string) => {
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
          columnElement.dataset.index = (i + 1).toString();
        });

        $html.find('.actionButtons input[type="button"]')
          .addClass('mdl-button mdl-js-button mdl-button--primary mdl-button--raised')
          .removeAttr('onclick');

        $html.find('.actionButtons input[type="button"]:not([id])')
          .attr('disabled', 'disabled');
        
        $html.find('table')
          .removeAttr('class')
          .prepend('<thead></thead>');

        this.viewSourceTable = this.sanitizer.bypassSecurityTrustHtml($html.html());
        
        setTimeout(() => {
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
              + 'mdl-data-table--selectable mdl-shadow--2dp');

          this.zone.runOutsideAngular(() => {
            try {
              componentHandler.upgradeDom();
            } catch (e) {}
          });
        }, 200);

        let draggable: HTMLElement = null;

        setTimeout(() => {
          const subsetIds: string[] = [];
          $(`[data-url="${ this.item.url }"] .view-editor__column-header`)
          .each((i, columnElement: HTMLElement) => {
            subsetIds.push(columnElement.dataset.column);
            
            columnElement.ondragstart = (ev: DragEvent) => {
              $('.view-editor__column-header--drop-target')
                .removeClass('view-editor__column-header--drop-target');
              ev.dataTransfer.setData('text', 'c:' 
                + (<HTMLElement> ev.target).dataset.column);
              draggable = columnElement;
              return true;
            };
            
            columnElement.ondrop = (ev: DragEvent) => {
              const transfer = ev.dataTransfer.getData('text');

              if (transfer.indexOf('c:') === -1) {
                /* seems that column is dragged */
                return true;
              }

              this.loading = true;
              
              this.api.dragColumn(this.item.url,
                draggable.dataset.column, 
                parseInt(columnElement.dataset.index, 10) - 
                parseInt(draggable.dataset.index, 10),
                subsetIds
              ).subscribe(() => {
                this.reloadView();
              });
              return true;
            };
            columnElement.ondragover = (ev: DragEvent) => {
              ev.preventDefault();
            };
            columnElement.ondragenter = (ev: DragEvent) => {
              $('.view-editor__column-header--drop-target')
                .removeClass('view-editor__column-header--drop-target');
              columnElement.classList.add('view-editor__column-header--drop-target');
              return true;
            };
            columnElement.ondragleave = (ev: DragEvent) => {
              columnElement.classList.remove('view-editor__column-header--drop-target');
              return true;
            };
          });

          this.loading = false;
        }, 300);
      });
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
