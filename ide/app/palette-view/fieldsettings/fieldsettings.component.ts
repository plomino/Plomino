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
import { LoadingComponent } from '../../editors';

@Component({
    selector: 'plomino-palette-fieldsettings',
    template: require('./fieldsettings.component.html'),
    styles: [require('./fieldsettings.component.css')],
    directives: [
        LoadingComponent
    ],
    providers: [],
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
    labelAdvanced: boolean;
    labelSaving: boolean;
    $selectedElement: JQuery;
    
    constructor(private objService: ObjService,
                private log: LogService,
                private tabsService: TabsService,
                private contentManager: TinyMCEFormContentManagerService,
                private labelsRegistry: LabelsRegistryService,
                private adapter: PlominoElementAdapterService,
                private zone: NgZone,
                private http: PlominoHTTPAPIService,
                private draggingService: DraggingService,
                private elementService: ElementService,
                private formsService: FormsService,
                private widgetService: WidgetService,
                private formsList: PlominoFormsListService,
                private fieldsService: FieldsService,
                private changeDetector: ChangeDetectorRef,
                private treeService: TreeService) { }

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

    submitForm() {
      this.log.info('changing field settings...', this.field);
      let $form: JQuery = $(this.fieldForm.nativeElement);
      let form: HTMLFormElement = <HTMLFormElement> $form.find('form').get(0);
      let formData: FormData = new FormData(form);

      formData.append('form.buttons.save', 'Save');

      this.formSaving = true;
      
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
          this.field, this.formAsObject($form), $fieldId);
          
          this.fieldsService.updateField(
            this.field, this.formAsObject($form), $fieldId
          );
          this.field.id = $fieldId;
          this.treeService.updateTree();
          return this.objService.getFieldSettings(newUrl);
        }
      })
      .subscribe((responseHtml: string) => {
        this.formTemplate = responseHtml;

        let newTitle: string = $(`<div>${responseHtml}</div>`)
          .find('#form-widgets-IBasic-title').val();
        let newId: string = $(`<div>${responseHtml}</div>`)
          .find('#form-widgets-IShortName-id').val();
        
        /**
         * fixing the replace bugs, not right but should work
         * should be rebuilded
         */
        setTimeout(() => {
          const pfc = '.plominoFieldClass';
          const $frame = $('iframe:visible').contents();
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

          if ($relatedLabel.length) {
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
            tinymce.activeEditor.id, 
            this.contentManager.getContent(tinymce.activeEditor.id), 
            this.draggingService
          );
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
        this.tabsService.openTab(eventData, true);
    }

    isLabelSettingsSaved() {
      return true;
    }

    private updateTemporaryTitle() {
      const selectedId = $('#form-widgets-label-relation').val();
      const temporaryTitle = $('#form-widgets-label-fieldtitle').val();
      this.labelsRegistry.update(
        `${tinymce.activeEditor.id}/${selectedId}`, 
        temporaryTitle, 'temporary_title'
      );
      if (!this.labelAdvanced) {
        this.$selectedElement.html(temporaryTitle);
        const $allTheSame = $('iframe:visible').contents()
          .find(`.plominoLabelClass[data-plominoid="${ selectedId }"]`)
          .filter((i, element) => element !== this.$selectedElement.get(0) 
            && !Boolean($(element).attr('data-advanced')));

        $allTheSame.html(temporaryTitle);
        this.changeDetector.detectChanges();
      }
      tinymce.activeEditor.setDirty(true);
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
          `${tinymce.activeEditor.id}/${selectedId}`, { title }
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
          `${tinymce.activeEditor.id}/${selectedId}`
        );

        if (this.fieldTitle === null) {
          this.elementService
            .getElement(`${tinymce.activeEditor.id}/${selectedId}`)
            .catch((error: any) => {
              return Observable.of(null);
            })
            .subscribe((fieldData: PlominoFieldDataAPIResponse) => {
              if (fieldData) {
                this.labelsRegistry.update(
                  `${tinymce.activeEditor.id}/${selectedId}`, fieldData.title
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
      // tinymce.activeEditor.setDirty(true);
    }

    private loadSettings() {
      this.tabsService.getActiveField()
        .do((field) => {
            if (field === null) {
                this.clickAddLink();
            }

            this.field = field;
        })
        .flatMap((field: PlominoFieldRepresentationObject) => {

          this.$selectedElement = this.adapter.getSelected();

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
                
                $select.on('change.sfevents', (event) => {
                  /**
                   * receipt:
                   * 1. value of select2 - [ok]
                   * 2. reference to subform element - [ok]
                   * 3. current form url - [tinymce.activeEditor.id]
                   */
                  $('iframe:visible').contents()
                    .find('[data-mce-selected="1"]')
                    .attr('data-plominoid', $select2.val());
  
                  if ($select2.val() && tinymce.activeEditor.id) {
                    let url = tinymce.activeEditor.id;
                    url += '/@@tinyform/example_widget?widget_type=subform&id=';
                    url += $select2.val();
  
                    this.http.get(url, 'fieldsettings.component.ts loadSettings')
                    .subscribe((response: any) => {
                      this.widgetService.getGroupLayout(
                        tinymce.activeEditor.id,
                        { id: this.field.id, layout: response.json() }
                      )
                      .subscribe((result: string) => {
                        try {
                          const subformHTML = $($(result).html()).html();
                          $('iframe:visible').contents()
                            .find('[data-mce-selected="1"]').html(subformHTML);
                          tinymce.activeEditor.setDirty(true);
                        }
                        catch (e) {
                          $select2.val('').trigger('change');
                          if (this.field.id && this.field.id !== 'Subform') {
                            $select2.val(this.field.id).trigger('change');
                          }
                        }
                      });
                    })
                  }
                });
              }
            }, 100);
            return Observable.of(false);
          }
          else if (field && field.type === 'label') {
            this.log.info('field', field);
            this.log.extra('fieldsettings.component.ts label');

            this.labelAdvanced = Boolean(this.$selectedElement.attr('data-advanced'));
            this.updateFieldTitle(field);

            setTimeout(() => {
              const $select = $('#form-widgets-label-relation');
              if ($select.length) {
                const $select2 = (<any>$select).select2({
                  placeholder: 'Select the field'
                });
    
                $select.off('change.lsevents');
                $select2.val('').trigger('change');
                this.log.info('this.field', this.field);
                this.log.extra('fieldsettings.component.ts ngOnInit');
    
                if (this.field.id) {
                  $select2.val(this.field.id).trigger('change');
                }

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
          else if (field && field.id) {
            return this.objService.getFieldSettings(field.url)
          }
          else {
            return Observable.of('');
          }
        })
        .subscribe((template: any) => {
          if (!template) {
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
          
          this.updateMacroses();
          this.changeDetector.detectChanges();
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
