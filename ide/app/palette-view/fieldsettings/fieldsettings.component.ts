import { PlominoActiveEditorService } from './../../services/active-editor.service';
import { PlominoElementAdapterService } from './../../services/element-adapter.service';
import { LabelsRegistryService } from './../../editors/tiny-mce/services/labels-registry.service';
import { DraggingService } from './../../services/dragging.service';
import { TinyMCEFormContentManagerService } from './../../editors/tiny-mce/content-manager/content-manager.service';
import { 
  Component,
  OnInit,
  OnChanges, 
  Input, 
  Output,
  ViewChild,
  ElementRef,
  NgZone,
  ChangeDetectorRef,
  ChangeDetectionStrategy,
  EventEmitter 
} from '@angular/core';

import { Observable } from 'rxjs/Observable';

import { 
  LogService,
  PlominoHTTPAPIService,
  ObjService,
  TabsService,
  TreeService,
  FieldsService,
  WidgetService,
  PlominoFormsListService,
  ElementService,
  FormsService
} from '../../services';

import { PloneHtmlPipe } from '../../pipes';
import { IField } from '../../interfaces';
import { PlominoBlockPreloaderComponent } from "../../utility";

@Component({
    selector: 'plomino-palette-fieldsettings',
    template: require('./fieldsettings.component.html'),
    styles: [require('./fieldsettings.component.css')],
    providers: [],
    directives: [PlominoBlockPreloaderComponent],
    pipes: [PloneHtmlPipe],
    // changeDetection: ChangeDetectionStrategy.OnPush
})

export class FieldSettingsComponent implements OnInit {
    @ViewChild('fieldForm') fieldForm: ElementRef;
    
    field: PlominoFieldRepresentationObject;
    formTemplate: string = '';

    formSaving: boolean = false;
    macrosWidgetTimer: number = null;

    fieldTitle: string;
    groupPrefix: string;
    labelAdvanced: boolean;
    labelSaving: boolean;
    $selectedElement: JQuery;

    /**
     * display block preloader
     */
    loading: boolean = false;
    
    constructor(private objService: ObjService,
      private log: LogService,
      private tabsService: TabsService,
      private contentManager: TinyMCEFormContentManagerService,
      private labelsRegistry: LabelsRegistryService,
      private adapter: PlominoElementAdapterService,
      private activeEditorService: PlominoActiveEditorService,
      private zone: NgZone,
      private http: PlominoHTTPAPIService,
      private draggingService: DraggingService,
      private elementService: ElementService,
      private formsService: FormsService,
      private widgetService: WidgetService,
      private formsList: PlominoFormsListService,
      private fieldsService: FieldsService,
      private changeDetector: ChangeDetectorRef,
      private treeService: TreeService
    ) {}

    ngOnInit() {
      this.loadSettings();

      this.formsService.formIdChanged$
      .subscribe(((data: {oldId: any, newId: any}) => {
        if (this.field && this.field.url.indexOf(data.oldId) !== -1) {
          this.field.url = 
            `${data.newId}/${this.formsService.getIdFromUrl(this.field.url)}`;
        }
      }).bind(this));
    }

    /* @todo FIX this */
    getEditorURLFromAnyURL(url: string): string {
      return url.replace(/^https?:\/\/.+?\//, '').split('/').slice(0, 3).join('/');
    }

    submitForm() {
      this.log.info('changing field settings...', this.field);
      let $form: JQuery = $(this.fieldForm.nativeElement);
      let form: HTMLFormElement = <HTMLFormElement> $form.find('form').get(0);
      let formData: FormData = new FormData(form);

      formData.append('form.buttons.save', 'Save');

      this.formSaving = true;
      this.loading = true;
      
      const oldId = this.field.url.split('/').pop();

      this.log.info('calling objService.updateFormSettings...');
      this.objService.updateFormSettings(this.field.url, formData)
      .flatMap((extractedTextAndURL: { html: string, url: string }) => {
        this.log.info('another changed element...', extractedTextAndURL);
        if (extractedTextAndURL.html.indexOf('dl.error') > -1) {
          return Observable.of(extractedTextAndURL.html);
        } else {
          let $fieldId = extractedTextAndURL.url
            .slice(extractedTextAndURL.url.lastIndexOf('/') + 1);
          // todo: newUrl - WTF?
          let newUrl = this.field.url.slice(
            0, this.field.url.lastIndexOf('/') + 1) + $fieldId; 
          
          this.field.url = newUrl;
          
          this.log.info('calling update field...', 
            this.field, this.formAsObject($form), $fieldId
          );

          this.fieldsService.updateField(
            this.field, this.formAsObject($form), $fieldId
          );

          this.field.id = $fieldId;
          this.treeService.updateTree();

          this.formTemplate = 
            `<p><div class="mdl-spinner mdl-js-spinner is-active"></div></p>`;
          componentHandler.upgradeDom();

          return this.objService
            .getFieldSettings(newUrl)
            .map(this.parseTabs);
        }
      })
      .subscribe((responseHtml: string) => {
        this.formTemplate = responseHtml;

        setTimeout(() => {
          $('.field-settings-wrapper form').submit((submitEvent) => {
            submitEvent.preventDefault();
            this.submitForm();
            return false;
          });

          this.loading = false;
        }, 300);

        let newTitle: string = $(`<div>${responseHtml}</div>`)
          .find('#form-widgets-IBasic-title').val();
        let newId: string = $(`<div>${responseHtml}</div>`)
          .find('#form-widgets-IShortName-id').val();
        
        /**
         * fixing the replace bugs, not right but should work
         * should be rebuilded
         */
        setTimeout(() => {
          if (!this.activeEditorService.getActive()) {
            if (this.field.type === 'PlominoAction') {
              $(`input#${ oldId }:visible`)
                .each((i, viewActionElement: HTMLInputElement) => {
                  viewActionElement.id = newId;
                  viewActionElement.name = newId;
                  viewActionElement.value = newTitle;
                });

              this.loading = false;
              this.changeDetector.detectChanges();
            }
            else if (this.field.type === 'PlominoColumn') {
              $(`.view-editor__column-header--selected:visible`)
                .each((i, viewColumnElement: HTMLInputElement) => {
                  viewColumnElement.dataset.column = newId;
                  viewColumnElement.innerHTML = newTitle;
                });

              this.loading = false;
              this.changeDetector.detectChanges();
            }

            return false;
          }
          const pfc = '.plominoFieldClass';
          const $frame = $(this.activeEditorService.getActive().getBody());
          this.log.info('id/title was changed',
            'newTitle', newTitle,
            'newId', newId,
            'oldId', oldId);

          const baseUrl = this.field.url.slice(
            0, this.field.url.lastIndexOf('/') + 1);
          this.labelsRegistry.replace(
            `${baseUrl}${oldId}`, `${baseUrl}${newId}`, newTitle
          );
          
          /* fix id of old field */
          $frame.find(`${pfc}[data-plominoid="${oldId}"]`)
            .attr('data-plominoid', newId);

          /* fix id of old field inputs */
          $frame.find(
            `${pfc} > input[id="${oldId}"], ${pfc} > textarea[id="${oldId}"]`)
            .attr('id', newId).attr('name', newId);

          /* fix id of old group */
          $frame.find(`.plominoGroupClass[data-groupid="${oldId}"]`)
            .attr('data-groupid', newId);

          /* get new id field related label */
          let $relatedLabel: JQuery;
          let $targetField = $frame.find(`${pfc}[data-plominoid="${newId}"]`);

          // this.log.info('$targetField', $targetField.get(0).outerHTML);
          // this.log.info('$targetField.parent()', $targetField.parent().get(0).outerHTML);

          if ($targetField.length && $targetField.parent().hasClass('plominoGroupClass')) {
            $relatedLabel = $targetField.parent().find('.plominoLabelClass');
          }
          else if ($targetField.length && $targetField.parent().prev().length) {
            $relatedLabel = $targetField.parent().prev().find('.plominoLabelClass');
          }

          if ($relatedLabel && $relatedLabel.length) {
            $relatedLabel.each((i, relatedLabelNode) => {
              const $relatedLabelNode = $(relatedLabelNode);
              if ($relatedLabelNode.next().next().hasClass('plominoFieldClass')
                && $relatedLabelNode.next().next().attr('data-plominoid') === newId
              ) {
                $relatedLabelNode.text(
                  $relatedLabelNode.text()
                ).attr('data-plominoid', newId);
              }
              else if ($relatedLabelNode.parent().next()
                  .children().first().hasClass('plominoFieldClass')
                && $relatedLabelNode.parent().next()
                  .children().first().attr('data-plominoid') === newId
              ) {
                $relatedLabelNode.text(
                  $relatedLabelNode.text()
                ).attr('data-plominoid', newId);
              }
            });
          }

          /* fix tinymce selection plugin */
          this.contentManager.setContent(
            this.activeEditorService.getActive().id, 
            this.contentManager.getContent(this.activeEditorService.getActive().id), 
            this.draggingService
          );

          componentHandler.upgradeDom();

          this.loading = false;
          this.changeDetector.detectChanges();

          /* form save automatically */
          /** @todo: replace to activeEditorService */
          this.activeEditorService.getActive().setDirty(true);
          $('#mceu_0 button:visible').click();
        }, 100);
        
        this.formSaving = false;
        this.updateMacroses();
        this.changeDetector.markForCheck();
      }, (err: any) => { 
        console.error(err) 
      });
    }

    cancelForm() {
        this.loadSettings();
    }

    openFieldCode(): void {
        let $form: JQuery = $(this.fieldForm.nativeElement);
        let form: HTMLFormElement = <HTMLFormElement> $form.find('form').get(0);
        let formData: any = new FormData(form);
        const label = formData.get('form.widgets.IBasic.title');
        const urlData = this.field.url.split('/');
        const eventData = {
            formUniqueId: this.field.formUniqueId,
            editor: 'code',
            label: label,
            path: [
                { name: urlData[urlData.length - 2], type: 'Forms' },
                { name: label, type: 'Fields' }
            ],
            url: this.field.url
        };
        this.log.info('this.tabsService.openTab #fs0001');
        this.tabsService.openTab(eventData, true);
    }

    private getDBOptionsLink(link: string) {
      return `${ 
        window.location.pathname
        .replace('++resource++Products.CMFPlomino/ide/', '')
        .replace('/index.html', '')
      }/${ link }`;
    }

    private openFormTab(formId: string) {
      this.log.info('calling elementService on openFormTab');
      this.log.extra('fieldsettings.component.ts openFormTab');
      this.elementService.getElementFormLayout(this.getDBOptionsLink(formId))
      .subscribe((formData) => {
        this.log.info('this.tabsService.openTab #fs0002');
        this.tabsService.openTab({
          // formUniqueId: response.formUniqueId,
          editor: 'layout',
          label: formData.title,
          url: formData['@id'],
          path: [{
              name: formData.title,
              type: 'Forms'
          }]
        });

        this.formsService.changePaletteTab(0);
        this.field = null;
      });
    }

    private updateTemporaryTitle() {
      const selectedId = $('#form-widgets-label-relation').val();
      const temporaryTitle = $('#form-widgets-label-fieldtitle').val();
      this.log.info('updateTemporaryTitle...', selectedId, temporaryTitle);
      this.labelsRegistry.update(
        `${this.activeEditorService.getActive().id}/${selectedId}`, 
        temporaryTitle, 'temporary_title', true
      );
      if (!this.labelAdvanced) {
        this.$selectedElement.html(temporaryTitle);
        const $allTheSame = $(this.activeEditorService.getActive().getBody())
          .find(`.plominoLabelClass[data-plominoid="${ selectedId }"]`)
          .filter((i, element) => element !== this.$selectedElement.get(0) 
            && !Boolean($(element).attr('data-advanced')));

        $allTheSame.html(temporaryTitle);
        this.changeDetector.detectChanges();
      }
      this.activeEditorService.getActive().setDirty(true);
    }

    private updateMacroses() {
      if (this.field) {
        window['MacroWidgetPromise'].then((MacroWidget: any) => {
          if (this.macrosWidgetTimer !== null) {
            clearTimeout(this.macrosWidgetTimer);
          }
          this.macrosWidgetTimer = setTimeout(() => { // for exclude bugs
            let $el = $('.field-settings-wrapper ' + 
            '#formfield-form-widgets-IHelpers-helpers > ul.plomino-macros');
            if ($el.length) {
              this.zone.runOutsideAngular(() => { new MacroWidget($el); });
            }
          }, 200);
        });

        let formulasSelector = '';
        formulasSelector += '#formfield-form-widgets-validation_formula';
        formulasSelector += ',#formfield-form-widgets-formula';
        formulasSelector += ',#formfield-form-widgets-html_attributes_formula';
        formulasSelector += ',#formfield-form-widgets-ISelectionField-selectionlistformula';
        setTimeout(() => { $(formulasSelector).remove(); }, 500);
      }
    }

    private clickAddLink() {
      this.formsService.changePaletteTab(0);
    }

    private saveLabelTitle() {
      const title = this.fieldTitle;
      const selectedId = $('#form-widgets-label-relation').val();
      if (selectedId) {
        this.labelSaving = true;
        this.elementService.patchElement(
          `${this.activeEditorService.getActive().id}/${selectedId}`, { title }
        );
        
        setTimeout(() => {
          this.labelSaving = false;
          this.$selectedElement.html(title);
          this.changeDetector.detectChanges();
        }, 200);
      }
    }

    private labelRelationSelected(eventData: Event) {
      const selectedId = $(eventData.target).val();

      this.$selectedElement.attr('data-plominoid', selectedId);
      
      if (!this.labelAdvanced) {
        this.fieldTitle = this.labelsRegistry.get(
          `${this.activeEditorService.getActive().id}/${selectedId}`
        );

        if (this.fieldTitle === null) {
          this.elementService
            .getElement(`${this.activeEditorService.getActive().id}/${selectedId}`)
            .catch((error: any) => {
              return Observable.of(null);
            })
            .subscribe((fieldData: PlominoFieldDataAPIResponse) => {
              if (fieldData) {
                this.labelsRegistry.update(
                  `${this.activeEditorService.getActive().id}/${selectedId}`, 
                  fieldData.title
                );
                this.fieldTitle = fieldData.title;
              }
              else {
                this.fieldTitle = 'Untitled';
              }
            });
        }

        this.$selectedElement.html(this.fieldTitle);
        this.changeDetector.detectChanges();
      }
    }

    private labelAdvancedChanged(eventData: Event) {
      const selectedId = $(eventData.target).val();
      const checked = (<HTMLInputElement> eventData.target).checked;
      this.$selectedElement.attr('data-advanced', checked ? '1' : '');

      if (selectedId && this.fieldTitle && !checked) {
        this.$selectedElement.html(this.fieldTitle);
      }

      this.changeDetector.detectChanges();
    }

    private updateFieldTitle(field: PlominoFieldRepresentationObject) {
      if (!this.field) {
        return;
      }
      const tmpId = this.field.url.split('/').pop();
      this.fieldTitle = this.labelsRegistry.get(field.url);
      if (this.fieldTitle === null
        && tmpId !== 'defaultLabel') {
        this.elementService
          .getElement(field.url)
          .catch((error: any) => {
            return Observable.of(null);
          })
          .subscribe((fieldData: PlominoFieldDataAPIResponse) => {
            if (fieldData) {
              this.labelsRegistry.update(field.url, fieldData.title, 'title', false);
              this.fieldTitle = fieldData.title;
            }
            else {
              this.fieldTitle = 'Untitled';
            }
          });
      }
      else if (tmpId === 'defaultLabel') {
        this.fieldTitle = 'Untitled';
      }

      this.changeDetector.detectChanges();
      // this.activeEditorService.getActive().setDirty(true);
    }

    private getSelectedSubform() {
      const $select: any = $('#form-widgets-subform-id');
      return $select.select2().val();
    }

    private getSelectedRelatedField() {
      const $select: any = $('#form-widgets-label-relation');
      return $select.select2().val();
    }

    private parseTabs(settingsHTML: string): string {
      const $settings = $(`<div>${ settingsHTML }</div>`);
      $settings.find('form')
        .prepend(`<div class="mdl-tabs__tab-bar default"></div>`);
      $settings.find('#content')
        .css('margin-bottom', '0');
      $settings.find('form')
        .wrap(`<div class="mdl-tabs mdl-js-tabs default mdl-js-ripple-effect"></div>`);
      $settings.find('fieldset').each((i, element) => {
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

    private saveGroupPrefix() {
      const $group = $(this.activeEditorService.getActive().getBody())
        .find(`.plominoGroupClass[data-groupid="${ this.field.id }"]`);
      $group.attr('data-groupid', this.groupPrefix);
      this.field.id = this.groupPrefix;
    }

    private cancelGroupPrefixChanges() {
      this.groupPrefix = this.field.id;
    }

    private deleteGroup() {
      if (!this.activeEditorService.getActive()) {
        return false;
      }
      this.elementService.awaitForConfirm()
      .then(() => {
        /** @todo: replace to activeEditorService */
        const $group = $(this.activeEditorService.getActive().getBody())
          .find(`.plominoGroupClass[data-groupid="${ this.field.id }"]`);

        const deleteJoins: Observable<any>[] = [];
  
        $group
          .find('.plominoFieldClass')
          .each((i, groupFieldElement: HTMLElement) => {
            // this.log.warn(this.field.url, groupFieldElement.dataset.plominoid);
            if (this.labelsRegistry.get(this.field.url)) {
              this.labelsRegistry.remove(this.field.url);
              deleteJoins.push(this.elementService.deleteElement(this.field.url));
            }
          });

        this.loading = true;
        Observable.forkJoin(deleteJoins)
          .subscribe(() => {
            this.treeService.updateTree().then(() => {});
            $group.remove();
            this.loading = false;
            this.field = null;
            this.formTemplate = null;
            this.changeDetector.detectChanges();

            /* form save automatically */
            this.activeEditorService.getActive().setDirty(true);
            $('#mceu_0 button:visible').click();
          });
      })
      .catch(() => null);
    }

    private ungroup() {
      /**
       * ungroup: unwrap fields from plominoGroup and close
       */
      const $group = $(this.activeEditorService.getActive().getBody())
        .find(`.plominoGroupClass[data-groupid="${ this.field.id }"]`);

      /* here I should update the ungrouped labels and fields to be mceNonEditable */
      $group.find('.plominoLabelClass, .plominoFieldClass')
        .removeClass('mceEditable')
        .addClass('mceNonEditable')
        .attr('contenteditable', 'false');

      $group.replaceWith($group.html());
      this.field = null;
      this.formTemplate = null;
      this.changeDetector.detectChanges();
    }

    private deleteField() {
      this.elementService.awaitForConfirm()
      .then(() => {
        this.elementService.deleteElement(this.field.url)
        .subscribe(() => {
          if (this.activeEditorService.getActive()) {
            this.labelsRegistry.remove(this.field.url);
            $(this.activeEditorService.getActive().getBody())
              .find(`[data-plominoid="${ this.field.id }"],[data-groupid="${ this.field.id }"]`)
              .remove();
          }
          else {
            if (this.field.type === 'PlominoAction') {
              $(`input#${ this.field.id.split('/').pop() }:visible`)
                .remove();
            }
            else if (this.field.type === 'PlominoColumn') {
              $(`.view-editor__column-header--selected:visible`)
                .remove();
            }
          }
          this.field = null;
          this.formTemplate = null;
          this.changeDetector.detectChanges();
          this.treeService.updateTree().then(() => {});
          /* form save automatically */
          this.activeEditorService.getActive().setDirty(true);
          $('#mceu_0 button:visible').click();
        });
      })
      .catch(() => null);
    }

    private getCurrentRegistryKeys() {
      return Array.from(this.labelsRegistry.getRegistry().keys())
        .filter((key: string) => {
          const id = this.activeEditorService.getActive().id;
          return key.indexOf(`${ id }/`) !== -1;
        });
    }

    private loadSettings() {
      this.tabsService.getActiveField()
        .do((field: PlominoFieldRepresentationObject) => {
            if (field === null) {
                this.clickAddLink();
            }

            this.field = field;
        })
        .flatMap<any>((field: PlominoFieldRepresentationObject) => {

          this.loading = true;
          this.$selectedElement = this.adapter.getSelected();
          this.groupPrefix = null;

          if (field && field.type === 'subform') {
            setTimeout(() => {
              const $select = $('#form-widgets-subform-id');
              if ($select.length) {
                const $select2 = (<any>$select).select2({
                  placeholder: 'Select the form'
                });
  
                $select.off('change.sfevents');
                $select2.val('').trigger('change');
                this.log.info(this.field);
  
                if (this.field.id && this.field.id !== 'Subform') {
                  $select2.val(this.field.id).trigger('change');
                }

                this.loading = false;
                this.changeDetector.detectChanges();
                
                $select.on('change.sfevents', (event) => {
                  /**
                   * receipt:
                   * 1. value of select2 - [ok]
                   * 2. reference to subform element - [ok]
                   * 3. current form url - [tinymce.activeEditor.id]
                   */
                  let $founded = $(this.activeEditorService.getActive().getBody())
                    .find('[data-mce-selected="1"]');
                  if (!$founded.hasClass('plominoSubformClass')) {
                    $founded = $founded.closest('.plominoSubformClass');
                  }
                  
                  $founded.attr('data-plominoid', $select2.val());
  
                  if ($select2.val() && this.activeEditorService.getActive().id) {
                    let url = this.activeEditorService.getActive().id;
                    url += '/@@tinyform/example_widget?widget_type=subform&id=';
                    url += $select2.val();
  
                    this.http.get(url, 'fieldsettings.component.ts loadSettings')
                    .subscribe((response: any) => {
                      /** @todo: replace to activeEditorService */
                      this.widgetService.getGroupLayout(
                        this.activeEditorService.getActive().id,
                        { id: this.field.id, layout: response.json() }
                      )
                      .subscribe((result: string) => {
                        try {
                          const $result = $(result);
                          $result.find('input,textarea,button').removeAttr('name').removeAttr('id');
                          $result.find('span').removeAttr('data-plominoid').removeAttr('data-mce-resize');
                          $result.removeAttr('data-groupid');
                          $result.find('div').removeAttr('data-groupid');
                          const subformHTML = $($result.html()).html();
                          $founded.html(subformHTML);
                          this.activeEditorService.getActive().setDirty(true);
                        }
                        catch (e) {
                          $select2.val('').trigger('change');
                          if (this.field.id && this.field.id !== 'Subform') {
                            $select2.val(this.field.id).trigger('change');
                          }
                        }

                        this.changeDetector.detectChanges();
                      });
                    })
                  }
                });
              }
            }, 100);
            return Observable.of(false);
          }
          else if (field && field.type === 'label') {
            this.log.info('field', field, 'labelsRegistry', 
              this.labelsRegistry.getRegistry());
            this.log.extra('fieldsettings.component.ts label');

            this.labelAdvanced = Boolean(this.$selectedElement.attr('data-advanced'));
            this.updateFieldTitle(field);

            setTimeout(() => {
              const $select = $('#form-widgets-label-relation');
              if ($select.length) {
                const $select2 = (<any>$select).select2({
                  placeholder: ''
                });
    
                $select.off('change.lsevents');
                $select2.val('').trigger('change');
                this.log.info('this.field', this.field);
                this.log.extra('fieldsettings.component.ts ngOnInit');
    
                if (this.field.id) {
                  $select2.val(this.field.id).trigger('change');
                }

                this.loading = false;

                $select.on('change.lsevents', ($event) => {
                  this.labelRelationSelected($event);
                });
              }
            }, 100);

            this.labelsRegistry.onUpdated()
            .subscribe(() => {
              this.labelAdvanced = Boolean(this.$selectedElement.attr('data-advanced'));
              this.updateFieldTitle(field);
            });

            return Observable.of(false);
          }
          else if (field && field.type === 'group') {
            this.log.info('group', field);
            this.log.extra('fieldsettings.component.ts group');
            this.groupPrefix = field.id;
            const $scrollingItem = $('.fieldsettings--control-buttons');
            if ($scrollingItem.length) {
              $scrollingItem.get(0).scrollIntoView();
            }
            this.loading = false;
            return Observable.of(false);
          }
          else if (field && field.id) {
            this.formTemplate = 
              `<p><div class="mdl-spinner mdl-js-spinner is-active"></div></p>`;
            componentHandler.upgradeDom();

            return this.objService
              .getFieldSettings(field.url)
              .map(this.parseTabs);
          }
          else {
            this.loading = false;
            return Observable.of('');
          }
        })
        .subscribe((template: any) => {
          const $scrollingContainer = $('.scrolling-container:visible');
          if ($scrollingContainer.length && !this.groupPrefix) {
            $scrollingContainer.get(0).scrollIntoView();
          }
          
          if (!template) {
            setTimeout(() => {
              this.changeDetector.detectChanges();
              this.changeDetector.markForCheck();
              componentHandler.upgradeDom()
            }, 200);
            return;
          }

          /**
           * patch field settings
           */
          const temporaryTitle = this.labelsRegistry.get(this.field.url);
          
          if (temporaryTitle) {
            const $template = $(`<div>${template}</div>`);
            $template.find('#form-widgets-IBasic-title').attr('value', temporaryTitle);
            template = $template.html();
          }

          this.formTemplate = template;

          setTimeout(() => {
            $('.field-settings-wrapper form').submit((submitEvent) => {
              submitEvent.preventDefault();
              this.submitForm();
              return false;
            });
          }, 300);
          
          this.updateMacroses();
          this.loading = false;
          this.changeDetector.detectChanges();

          componentHandler.upgradeDom();
        }); 
    }

    private formAsObject(form: any): any {
        let result = {};
        let serialized = form.find('form').serializeArray();
        serialized.forEach((formItem: any) => {
            let isId = formItem.name.indexOf('IShortName.id') > -1;
            let isTitle = formItem.name.indexOf('IBasic.title') > -1;
            let isType = formItem.name.indexOf('field_type:list') > -1;
            let isWidget = formItem.name.indexOf('ITextField.widget:list') > -1;
        
            if (isId) {
                result['id'] = formItem.value;
            }

            if (isTitle) {
                result['title'] = formItem.value;
            }

            if (isType) {
                result['type'] = formItem.value.toLowerCase();
            }

            if (isWidget) {
                result['widget'] = formItem.value.toLowerCase();
            }
        });
        return result;
    }
}
