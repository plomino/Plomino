import { PlominoActiveEditorService } from './../../services/active-editor.service';
import {
    Component,
    Input,
    Output,
    EventEmitter,
    OnInit,
    OnChanges,
    ChangeDetectorRef,
    NgZone,
    ViewChild,
    ElementRef,
    ChangeDetectionStrategy
} from '@angular/core';

import { Observable } from 'rxjs/Observable';

import {
    ObjService,
    TabsService,
    TreeService,
    LogService,
    FormsService
} from '../../services';
import { PloneHtmlPipe } from '../../pipes';
import {ElementService} from "../../services/element.service";
import {WidgetService} from "../../services/widget.service";
import { PlominoBlockPreloaderComponent } from "../../utility";

@Component({
    selector: 'plomino-palette-formsettings',
    template: require('./formsettings.component.html'),
    styles: [require('./formsettings.component.css')],
    directives: [PlominoBlockPreloaderComponent],
    providers: [],
    pipes: [PloneHtmlPipe],
    changeDetection: ChangeDetectionStrategy.OnPush
})

export class FormSettingsComponent implements OnInit {
    @ViewChild('formElem') formElem: ElementRef;

    tab: PlominoTab;
    formSaving: boolean = false;
    macrosWidgetTimer: number = null;

    // This needs to handle both views and forms
    heading: string;
    formSettings: string = '';

    /**
     * display block preloader
     */
    loading: boolean = false;
    
    private formLayout: string = '';

    constructor(private objService: ObjService,
                private log: LogService,
                private changeDetector: ChangeDetectorRef,
                private tabsService: TabsService,
                private treeService: TreeService,
                private activeEditorService: PlominoActiveEditorService,
                private zone: NgZone,
                private elementService: ElementService,
                private widgetService: WidgetService,
                private formsService: FormsService) {}

    ngOnInit() {
        this.getSettings();

        let onSaveFinishCb: any = null;

        this.formsService.formSettingsSave$.subscribe((data) => {
          // debugger;
          this.log.info('T-5 formsettings.component.ts', this.tabsService.ping());
          // debugger;
            // if (typeof data.formUniqueId === 'undefined'
            //   || data.formUniqueId >= 1e10) {
            //     data.formUniqueId = this.tab.formUniqueId;
            // }
            
            // if (this.tab.formUniqueId !== data.formUniqueId)
            //     return;
            if (this.tab.url !== data.url)
                return;

            onSaveFinishCb = data.cb;

            this.formsService.getFormContentBeforeSave(data.url);
        });

        this.formsService.onFormContentBeforeSave$
          .subscribe((data:{id:any, content:any}) => {
            this.log.info('T-3 formsettings.component.ts', data.id, this.tabsService.ping());
            if (this.tab.url !== data.id)
                return;
            // if (this.tab.formUniqueId !== data.id)
            //     return;

            this.saveForm({
                cb: onSaveFinishCb,
                content: data.content
            });
        });
    }

    private hasAuthPermissions() {
      return !(this.formSettings.indexOf(
        'You do not have sufficient privileges to view this page'
      ) !== -1);
    }

    saveFormSettings(formData: FormData, formLayout: any, cb: any) {
      this.log.info('T-1 formsettings.component.ts', this.tabsService.ping());
      this.formSaving = true;
      let $formId: any = '';
    
      formData.set('form.widgets.form_layout', formLayout);
    
      const flatMapCallback = ((responseData: {html: string, url: string}) => {
        if (responseData.html !== "<div id='ajax_success'/>") {
            return Observable.of(responseData.html);
        } else {
            $formId = responseData.url.slice(responseData.url.lastIndexOf('/') + 1);
            let newUrl = this.tab.url
              .slice(0, this.tab.url.lastIndexOf('/') + 1) + $formId;
            let oldUrl = this.tab.url;

            if (newUrl && oldUrl && newUrl !== oldUrl) {
                this.formsService.changeFormId({
                    newId: newUrl,
                    oldId: oldUrl
                });
                
                this.tabsService.updateTabId(this.tab, $formId);
                this.changeDetector.markForCheck();
            }

            this.formsService.formSaving = false;
            this.changeDetector.markForCheck();
            return this.objService.getFormSettings(newUrl);
        }
      }).bind(this);

      this.loading = true;
      this.objService.updateFormSettings(this.tab.url, formData)
        .flatMap((responseData: {html: string, url: string}) => 
          flatMapCallback(responseData))
        .map(this.parseTabs)
        .subscribe((responseHtml: string) => {
          this.log.info('updateFormSettings');
          this.log.extra('formsettings.component.ts');
          this.treeService.updateTree().then(() => {
            this.log.info('updateTree() figured out');
              this.formSaving = false;
              this.formSettings = responseHtml;
              this.updateMacroses();
              this.loading = false;
              this.activeEditorService.turnActiveEditorToLoadingState(false);
              this.changeDetector.markForCheck();
              
              window['materialPromise'].then(() => {
                componentHandler.upgradeDom();
    
                setTimeout(() => {
                  componentHandler.upgradeDom();
                  $('.form-settings-wrapper form').submit((submitEvent) => {
                    submitEvent.preventDefault();
                    this.submitForm();
                    return false;
                  });
                  
                  this.loading = false;
                  // debugger;
                  this.changeDetector.markForCheck();
                  this.changeDetector.detectChanges();
                }, 400);
              });

              if (cb) {
                cb();
              }
              else {
                /* reinitialize tinymce */
                // Object.keys(tinymce.EditorManager.editors)
                // .forEach((key: string) => {
                //   if (isNaN(parseInt(key, 10))) {
                //     tinymce.EditorManager.execCommand('mceRemoveEditor', true, key);
                //     tinymce.EditorManager.execCommand('mceAddEditor', true, key);
                //   }
                // });
              }
          });
        }, err => {
            console.error(err)
        });
    }

    submitForm() {
      this.log.info('T-200-b formsettings.compmonent.ts', this.tabsService.ping());
      this.formsService.saveForm(this.tab.url);
      this.changeDetector.markForCheck();
    }

    saveForm(data:{content:any,cb:any}) {
      this.log.info('T-2 formsettings.component.ts', this.tabsService.ping());
      this.log.info('saveForm CALLED!');
      let $form: any = $(this.formElem.nativeElement);
      let form: HTMLFormElement = $form.find('form').get(0);
      let formData: any = new FormData(form);

      // this.treeService.updateTree();

      formData.append('form.buttons.save', 'Save');

      this.saveFormSettings(formData, data.content, data.cb);
    }

    cancelForm() {
        this.getSettings();
    }

    openFormCode(tab: any): void {
        const eventData = {
            formUniqueId: tab.formUniqueId,
            editor: 'code',
            label: tab.label,
            path: [{ name: tab.label, type: 'Forms' }],
            url: tab.url
        };
        this.log.info('this.tabsService.openTab #frs0001 with showAdd');
        this.tabsService.openTab(eventData, true);
    }

    openFormPreview(formUrl: string, tabType: string): void {
      if (tabType === 'PlominoForm') {
        
        ((): Promise<any> => {
          const anyChanges = tinymce.get(formUrl).isDirty();

          if (anyChanges) {
            /**
             * warn the user of any unsaved changes
             */
            return this.elementService.awaitForConfirm(
              'The Form has unsaved changes, do you want to show preview anyway?'
            );
          }

          return Promise.resolve();
        })()
        .then(() => {
            window.open(`${formUrl}/OpenForm`);
          })
        .catch(() => null);
      }
      else {
        window.open(`${formUrl}/view`);
      }
    }

    private deleteForm(tabData: PlominoTab) {
      const tab = this.tab;
      this.elementService.awaitForConfirm()
      .then(() => {
        this.elementService
          .deleteElement(tabData.url)
          .subscribe(() => {
            this.tabsService.closeTab(tab);
            this.tab = null;
            this.formSettings = '';
            this.formLayout = '';
            this.changeDetector.detectChanges();
            this.treeService.updateTree();
            this.changeDetector.markForCheck();
          });
      })
      .catch(() => null);
    }

    private updateMacroses() {
      if (this.formSettings) {
        window['MacroWidgetPromise'].then((MacroWidget: any) => {
          if (this.macrosWidgetTimer !== null) {
            clearTimeout(this.macrosWidgetTimer);
          }

          this.macrosWidgetTimer = setTimeout(() => { // for exclude bugs
            let $el = $('.form-settings-wrapper ' + 
            '#formfield-form-widgets-IHelpers-helpers > ul.plomino-macros');
            if ($el.length) {
              this.zone.runOutsideAngular(() => {
                try {
                  new MacroWidget($el);
                }
                catch (e) {
                  setTimeout(() => {
                    let $el = $('.form-settings-wrapper ' + 
                      '#formfield-form-widgets-IHelpers-helpers > ul.plomino-macros');
                    new MacroWidget($el);
                  }, 100);
                }
              });
            }
          }, 200);
        });

        let formulasSelector = '';
        formulasSelector += '#formfield-form-widgets-document_title';
        formulasSelector += ',#formfield-form-widgets-document_id';
        formulasSelector += ',#formfield-form-widgets-search_formula';
        formulasSelector += ',#fieldset-events';
        setTimeout(() => {
          $(formulasSelector).remove();
          $('.plomino-formula').parent('div.field').remove();
          $('#content').css('margin-bottom', 0);
        }, 500);
      }
    }

    private parseTabs(settingsHTML: string): string {
      const $settings = $(`<div>${ settingsHTML }</div>`);
      $settings.find('form')
        .prepend(`<div class="mdl-tabs__tab-bar default"></div>`);
      $settings.find('#content')
        .css('margin-bottom', '0');
      $settings.find('form')
        .wrap(`<div class="mdl-tabs mdl-js-tabs default mdl-js-ripple-effect"></div>`);
      $settings.find('fieldset')
        .filter((i, element) => {
          return $(element).find('legend').text().trim() !== 'Events';
        })
        .each((i, element) => {
        const $element = $(element);
        $element.css('margin-top', '10px');
        const tabId = Math.floor(Math.random() * 10e10) + 10e10 - 1;
        const $legend = $element.find('legend');
        const legend = $legend.text().trim();

        $settings.find('.mdl-tabs__tab-bar').append(`
          <a href="#fs-tab-${ tabId }" style="width: 50%"
            class="mdl-tabs__tab default ${ i === 0 ? 'is-active' : '' }">
            ${ legend }
          </a>
        `);

        $legend.remove();
        
        $element.replaceWith(`
        <div class="mdl-tabs__panel ${ i === 0 ? 'is-active' : '' }"
          id="fs-tab-${ tabId }">
          ${ element.outerHTML }
        </div>
        `);
      });

      return $settings.get(0).outerHTML;
    }

    private getSettings() {
      this.log.extra('formsettings.component.ts');
      this.tabsService.getActiveTab()
        .do((tab) => {
          this.tab = tab;
        })
        .flatMap((tab: any) => {
          // this.log.info('tab', tab, tab && tab.url ? tab.url : null);
          // this.log.extra('formsettings.component.ts getSettings -> flatMap');
          
          if (tab && tab.url) {
            this.formSettings = 
              `<p><div class="mdl-spinner mdl-js-spinner is-active"></div></p>`;
            componentHandler.upgradeDom();

            return this.objService
              .getFormSettings(tab.url)
              .map(this.parseTabs);
          } else {
            return Observable.of('');
          }
        })
        .subscribe((template) => {
          this.formSettings = template;

          this.updateMacroses();
          this.loading = false;
          this.changeDetector.markForCheck();
          this.changeDetector.detectChanges();
          window['materialPromise'].then(() => {
            componentHandler.upgradeDom();

            setTimeout(() => {
              componentHandler.upgradeDom();

              $('.form-settings-wrapper form').submit((submitEvent) => {
                submitEvent.preventDefault();
                this.submitForm();
                return false;
              });
            }, 400);
          });
        });
    }
}
