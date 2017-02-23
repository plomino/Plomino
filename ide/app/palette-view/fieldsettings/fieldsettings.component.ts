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
    ObjService,
    TabsService,
    TreeService,
    FieldsService,
    FormsService
} from '../../services';

import { PloneHtmlPipe } from '../../pipes';

import { IField } from '../../interfaces';

import 'jquery';

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
    
    field: any;
    formTemplate: string = '';

    formSaving: boolean = false;
    macrosWidgetTimer: any = null;
    
    constructor(private objService: ObjService,
                private tabsService: TabsService,
                private zone: NgZone,
                private formsService: FormsService,
                private fieldsService: FieldsService,
                private changeDetector: ChangeDetectorRef,
                private treeService: TreeService) { }

    ngOnInit() {
        this.loadSettings();

        this.formsService.formIdChanged$.subscribe(((data: any) => {
            if (this.field && this.field.url.indexOf(data.oldId) !== -1) {
                this.field.url = `${data.newId}/${this.formsService.getIdFromUrl(this.field.url)}`;
            }
        }).bind(this));
    }

    submitForm() {
        let $form: JQuery = $(this.fieldForm.nativeElement);
        let form: HTMLFormElement = <HTMLFormElement> $form.find('form').get(0);
        let formData: FormData = new FormData(form);

        formData.append('form.buttons.save', 'Save');

        this.formSaving = true;
        
        const oldId = this.field.url.split('/').pop();
        this.objService.updateFormSettings(this.field.url, formData)
        .flatMap((responseData: any) => {
          if (responseData.html.indexOf('dl.error') > -1) {
            return Observable.of(responseData.html);
          } else {
            let $fieldId = responseData.url.slice(responseData.url.lastIndexOf('/') + 1);
            let newUrl = this.field.url.slice(0, this.field.url.lastIndexOf('/') + 1) + $fieldId; 
            this.field.url = newUrl;
            this.fieldsService.updateField(this.field, this.formAsObject($form), $fieldId);
            this.field.id = $fieldId;
            this.treeService.updateTree();
            return this.objService.getFieldSettings(newUrl);
          }
        })
        .subscribe((responseHtml: string) => {
            this.formTemplate = responseHtml;
            let newTitle = $(`<div>${responseHtml}</div>`).find('#form-widgets-IBasic-title').val();
            let newId = $(`<div>${responseHtml}</div>`).find('#form-widgets-IShortName-id').val();
            
            /**
             * fixing the replace bugs, not right but should work
             * should be rebuilded
             */
            setTimeout(() => {
              const pfc = '.plominoFieldClass';
              const $frame = $('iframe:visible').contents();
              console.info('id/title was changed',
                'newTitle', newTitle,
                'newId', newId,
                'oldId', oldId);
              
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
  
              console.info('$targetField', $targetField.get(0).outerHTML);
              console.info('$targetField.parent()', $targetField.parent().get(0).outerHTML);

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
                  && $relatedLabelNode.next().next().attr('data-plominoid') === newId) {
                    $relatedLabelNode.text(newTitle).attr('data-plominoid', newId);
                  }
                  else if ($relatedLabelNode.parent().next()
                    .children().first().hasClass('plominoFieldClass')
                  && $relatedLabelNode.parent().next()
                    .children().first().attr('data-plominoid') === newId) {
                    $relatedLabelNode.text(newTitle).attr('data-plominoid', newId);
                  }
                });
              }
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

    private loadSettings() {
        this.tabsService.getActiveField()
            .do((field) => {
                if (field === null) {
                    this.clickAddLink();
                }

                this.field = field;
            })
            .flatMap((field: any) => {
                if (field && field.id) {
                    return this.objService.getFieldSettings(field.url)
                } else {
                    return Observable.of('');
                }
            })
            .subscribe((template) => {
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
