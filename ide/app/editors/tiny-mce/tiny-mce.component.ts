import { PlominoActiveEditorService } from './../../services/active-editor.service';
import { TinyMCEFormContentManagerService } from './content-manager';
import {
    Component, 
    Input, 
    Output,
    OnInit,
    OnChanges,
    OnDestroy, 
    EventEmitter,
    ViewChild,
    ElementRef,
    AfterViewInit, 
    ChangeDetectorRef,
    ChangeDetectionStrategy,
    NgZone
} from '@angular/core';

import { 
    Http,
    Response
} from '@angular/http';

import {DND_DIRECTIVES} from 'ng2-dnd';

import {
    Subscription,
    Observable,
    Scheduler
} from 'rxjs/Rx';

import {
  ElementService,
  FieldsService,
  DraggingService,
  TemplatesService,
  LogService,
  PlominoElementAdapterService,
  WidgetService,
  TabsService,
  FormsService,
  PlominoSaveManagerService
} from '../../services';

import { UpdateFieldService, LabelsRegistryService } from './services';
import { PlominoBlockPreloaderComponent } from "../../utility";

@Component({
    selector: 'plomino-tiny-mce',
    template: require('./tiny-mce.template.html'),
    styles: [`
        .drop-zone {
            width: 100%;
            background-color: black;
            opacity: 0;
            transition: opacity 0.5s linear;
        }
        .dnd-drag-over {
            opacity: 0.1;
        }
    `],
    directives: [DND_DIRECTIVES, PlominoBlockPreloaderComponent],
    providers: [ElementService, UpdateFieldService],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class TinyMCEComponent implements AfterViewInit, OnDestroy {

  @Input() id: string;
  @Input() item: any;
  @Output() isDirty: EventEmitter<any> = new EventEmitter();
  @Output() isLoading: EventEmitter<any> = new EventEmitter();
  @Output() fieldSelected: EventEmitter<any> = new EventEmitter();

  labelMarkupEvent: EventEmitter<any> = new EventEmitter();

  @ViewChild('theEditor') editorElement: ElementRef;

  data: string;
  isDragged: boolean = false;
  dragData: any;
  idChanges: any;
  editorInstance: any;

  draggingSubscription: Subscription;
  insertionSubscription: Subscription;
  templatesSubscription: Subscription;

  autoSaveTimer: any = null;
  autoSavedContent: string = null;

  theFormIsSavingNow: boolean = false;

  /**
   * display block preloader
   */
  loading: boolean = true;

  constructor(private elementService: ElementService,
    private fieldsService: FieldsService,
    private draggingService: DraggingService,
    private templatesService: TemplatesService,
    private widgetService: WidgetService,
    private log: LogService,
    private adapter: PlominoElementAdapterService,
    private formsService: FormsService,
    private labelsRegistry: LabelsRegistryService,
    private changeDetector: ChangeDetectorRef,
    private tabsService: TabsService,
    private activeEditorService: PlominoActiveEditorService,
    private updateFieldService: UpdateFieldService,
    private contentManager: TinyMCEFormContentManagerService,
    private saveManager: PlominoSaveManagerService,
    private http: Http,
    private zone: NgZone) {
    
    /**
     * fields, hidewhens, actions, etc
     */
    this.insertionSubscription = this.fieldsService.getInsertion()
    .subscribe((insertion: InsertFieldEvent) => {
      this.log.info('fieldsService.getInsertion', insertion);
      this.log.extra('tiny-mce.component.ts this.insertionSubscription');
      let insertionParent = insertion.name.slice(0, insertion.name.lastIndexOf('/'));
      let dataToInsert = Object.assign({}, insertion, { 
        type: insertion['@type']
      });
      this.log.info('insertionSubscription', dataToInsert);
      if (insertionParent === this.id) {
        this.addElement(dataToInsert);
        
        /* form save automatically */
        // this.formsService.saveForm(this.item.formUniqueId, false);
        this.changeDetector.markForCheck();
      }
    });

    /**
     * form components like text/long text/etc
     */
    this.templatesSubscription = this.templatesService.getInsertion()
    .subscribe((insertion: InsertTemplateEvent) => {
      this.log.info('templatesService.getInsertion', insertion);
      this.log.extra('tiny-mce.component.ts this.templatesSubscription');
      let parent = insertion.parent;
      if (insertion.parent === this.id) {
        if (insertion.target === null) {
          const $selected = this.adapter.getSelectedPosition() || this.adapter.getSelected();
          insertion.target = $selected && $selected.prop('tagName') !== 'BODY' 
            ? ($selected.prev().length 
            ? $selected.prev().get(0) : $selected.get(0)) : null;
          // console.warn(insertion.target, $selected);
        }
        this.log.info('insertion template', insertion);
        this.insertGroup(insertion.group, insertion.target);

        /* form save automatically */
        this.saveTheForm();
      }
    });
    
    this.draggingSubscription = this.draggingService.getDragging()
    .subscribe((dragData: any) => {
      this.dragData = dragData;
      this.isDragged = !!dragData;
      this.changeDetector.markForCheck();
    });

    this.tabsService.getActiveField()
    .subscribe((fieldData: any) => {
      if (fieldData && fieldData.type === 'PlominoField'
        && fieldData.id && fieldData.url.replace(`/${ fieldData.id }`, '') === this.id
      ) {
        if (tinymce.get(this.id)) {
          const $body = $(tinymce.get(this.id).getBody());
          let $element = $body
            .find(`.plominoFieldClass[data-plominoid="${ fieldData.id }"]`);
          if ($element.length) {
            if ($element.closest('.plominoGroupClass').length) {
              $element = $element.closest('.plominoGroupClass');
            }
            $body.animate({ scrollTop: $element.offset().top },
              { duration: 'medium', easing: 'swing' });
          }
        }
      }
    });

    this.fieldsService.listenToUpdates()
    .subscribe((updateData) => { this.updateField(updateData); });

    this.formsService.formIdChanged$.subscribe((data) => {
      this.idChanges = Object.assign({}, data);
      if (this.activeEditorService.editorURL === data.oldId) {
        this.activeEditorService.setActive(data.newId);
      }
    });

    this.formsService.formContentSave$.subscribe((data) => {
      try {
        this.changeDetector.detectChanges();
      }
      catch (e) {
        this.log.error(e);
      }

      // if (this.theFormIsSavingNow && data.formUniqueId >= 1e10) {
      //   data.formUniqueId = this.item.formUniqueId;
      // }

      if (data.url !== this.item.url)
        return;

      this.isLoading.emit(true);

      let editor = tinymce.get(this.id) || 
        tinymce.get(this.idChanges && this.idChanges.oldId);

      // editor.buttons.save.onclick();
      editor.setDirty(false);
      this.log.info('i am', this.id, 'and I doing call saveFormLayout');
      this.saveFormLayout(data.cb);
    } );

    this.formsService.getFormContentBeforeSave$.subscribe((data:{id:any}) => {
      this.log.info('T-4 tiny-mce.component.ts', this.id, this.tabsService.ping());
      // if (typeof this.item.formUniqueId === 'undefined'
      //   || this.item.formUniqueId >= 1e10) {
      //   this.item.formUniqueId = data.id;
      // }
      
      if (data.id !== this.item.url)
        return;

      this.theFormIsSavingNow = true;
      this.fallLoading();
      this.log.info('fallLoading from getFormContentBeforeSave$');
      // this.loading = true;
      // try {
      //   this.changeDetector.markForCheck();
      //   this.changeDetector.detectChanges();
      // }
      // catch (e) {
      //   this.log.error(e);
      // }

      this.formsService.onFormContentBeforeSave({
        id: data.id,
        content: this.contentManager.getContent(this.id)
      });
    });
  }

  ngOnDestroy() {
    this.draggingSubscription.unsubscribe();
    this.insertionSubscription.unsubscribe();
    this.templatesSubscription.unsubscribe();
    tinymce.EditorManager.execCommand('mceRemoveEditor', true, this.id);
  }

  saveTheForm() {
    // this.loading = true;
    this.fallLoading();
    this.log.info('fallLoading from saveTheForm', this.item.formUniqueId, this.id);
    this.theFormIsSavingNow = true;
    this.formsService.saveForm(this.item.url, false);
    // tinymce.get(this.id).setDirty(false);
    // this.isDirty.emit(false);
    // this.saveManager.nextEditorSavedState(this.id, );
    // this.changeDetector.markForCheck();
  }

  ngAfterViewInit(): void {
    let tiny = this;

    const LinkModal = window['LinkModal'];

    // this.http.post('/Plone/mydb/rename-group', {

    // })
    // .subscribe((r: any) => {
    //   console.log(r);
    // });

    tinymce.init({
      cleanup : false,
      selector:'.tinymce-wrap',
      mode : 'textareas',
      forced_root_block: '',
      linkModal: null,
      addLinkClicked: function () {
        tiny.zone.runOutsideAngular(() => {
          var self = <any>this;
          if (self.linkModal === null) {
            var $el = $('<div/>').insertAfter(self.$el);
            var linkTypes = ['internal', 'upload', 'external', 'email', 'anchor'];
            if (!self.options.upload) {
              linkTypes.splice(1, 1);
            }
            self.linkModal = new LinkModal($el,
              $.extend(true, {}, self.options, {
                tinypattern: self,
                linkTypes: linkTypes
              })
            );
            self.linkModal.show();
          } else {
            self.linkModal.reinitialize();
            self.linkModal.show();
          }
        });
      },
      linkAttribute: 'path',
      prependToScalePart: '/imagescale/',
      appendToScalePart: '',
      appendToOriginalScalePart: '',
      defaultScale: 'large',
      scales: 'Listing (16x16):listing,Icon (32x32):icon,Tile (64x64):tile,' +
              'Thumb (128x128):thumb,Mini (200x200):mini,Preview (400x400):preview,' +
              'Large (768x768):large',
      targetList: [
        { text: 'Open in this window / frame', value: '' },
        { text: 'Open in new window', value: '_blank' },
        { text: 'Open in parent window / frame', value: '_parent' },
        { text: 'Open in top frame (replaces all frames)', value: '_top' }
      ],
      imageTypes: ['Image'],
      folderTypes: ['Folder', 'Plone Site'],
      plugins: ['code', 'save', 'link', 'noneditable', 
        'preview'/*, 'ploneimage', 'plonelink'*/],
      toolbar: 'save | undo redo | formatselect | bold italic underline' +
      ' | alignleft aligncenter alignright alignjustify | ' +
      'bullist numlist | outdent indent',
      // 'plonelink unlink ploneimage',

      save_onsavecallback: () => {
        this.log.info('T-200 tiny-mce.component.ts', this.tabsService.ping());
        // this.loading = true;
        this.fallLoading();
        this.log.info('fallLoading from save_onsavecallback');
        this.saveTheForm();
      },

      setup : (editor: TinyMceEditor) => {
        if(this.editorInstance) {
          this.editorInstance.remove();
        } else {
          // this.getFormLayout();
        }

        editor.addMenuItem('PreviewButton', {
          text: 'Open form in new tab',
          context: 'view',
          onclick: () => {
            // this.formsService.saveForm(this.item.formUniqueId, false);
            // this.changeDetector.markForCheck();
            // setTimeout(() => {
              window.open(`${ this.item.url }/OpenForm`);
            // }, 200);
            return;
          }
        });

        this.editorInstance = editor;

        setTimeout(() => this.editorInstance.show());

        editor.on('change', (e: any) => {
          this.log.info('change event received', e, 
            this.activeEditorService.editorURL, this.id);
          if (this.activeEditorService.editorURL === this.id 
            && !this.theFormIsSavingNow) {
            /* TinyMCE BUG: change one editor throws other */
            this.log.info('onchange dirty', this.formsService.formSaving, this.id);
            tiny.isDirty.emit(true);
          }
        });

        editor.on('NodeChange', (nodeChangeEvent: any) => {
          if (nodeChangeEvent.selectionChange === true) {
            const $label = $(nodeChangeEvent.element).closest('.plominoLabelClass');

            if ($label.length) {
              this.labelMarkupEvent.next($label);
            }
          }
        });

        // editor.on('activate', (e: any) => {
        //   let $editorFrame = $(this.editorElement.nativeElement)
        //     .find('iframe[id*=mce_]');
        // });

        editor.on('mousedown', (ev: MouseEvent) => {
          let $element = $(ev.target);
          this.adapter.selectPosition($element);

          this.zone.run(() => {
            let $element =  $(ev.target);
            let eventTarget = <any> ev.target;

            if (eventTarget.control ||
              (['radio', 'select-one'].indexOf(eventTarget.type) !== -1)) {
              $element = $element.parent();
            }
            else if (eventTarget.tagName === 'OPTION' ||
              eventTarget.nodeName === 'OPTION') {
              $element = $element.parent().parent();
            }
            
            let $parent = $element.parent();
            let $grandParent = $parent.parent();
            let $grandGrandParent = $grandParent.parent();
            let $closest = $element.closest('[data-mce-selected]');
            let $elementIsGroup = $element.hasClass('plominoGroupClass');
            let elementIsLabel = $element.hasClass('plominoLabelClass');
            let elementIsSubform = $element.hasClass('plominoSubformClass');
            let parentIsSubform = $parent.hasClass('plominoSubformClass')
              || $grandParent.hasClass('plominoSubformClass')
              || $grandGrandParent.hasClass('plominoSubformClass');
            let closestIsSubform = $closest.hasClass('plominoSubformClass')
              || ($parent.hasClass('plominoFieldGroup') && 
              $parent.closest('[data-mce-selected]').hasClass('plominoSubformClass'));
            let parentIsLabel = $parent.hasClass('plominoLabelClass');

            let $elementId = $element.attr('data-plominoid');
            let $parentId = $parent.attr('data-plominoid');
            let $closestLabel = $element.closest('.plominoLabelClass');

            this.log.info($element, $parent, $grandParent, $grandGrandParent, $closest);
            this.log.extra('tiny-mce.component.ts editor.on(\'mousedown\', ...)');

            const $s = $closestLabel.length ? $closestLabel : $element;
            if ($s.is(this.adapter.getSelected())) {
              return;
            }
            this.adapter.select($s);

            if (!elementIsSubform && (parentIsSubform || closestIsSubform)) {
              elementIsSubform = true;
            }

            if (!elementIsSubform && $elementIsGroup) {
              this.fieldSelected.emit({
                id: $element.attr('data-groupid'),
                type: 'group',
                parent: this.id
              });

              // let groupChildrenQuery = 
              //   '.plominoFieldClass, .plominoHidewhenClass, .plominoActionClass';
              // let $groupChildren = $element.find(groupChildrenQuery);
              // if ($groupChildren.length > 1) {
              //   this.log.info('field selected #a');
              //   this.fieldSelected.emit(null);
              //   return;
              // }
              // else {
              //   let $child = $groupChildren;
              //   let $childId = $child.data('plominoid');
              //   let $childType = this.extractClass($child.attr('class'));
              //   this.log.info('field selected #b');
              //   this.fieldSelected.emit({
              //     id: $childId,
              //     type: $childType,
              //     parent: this.id
              //   });
              //   return;
              // }
            }
            else if (!elementIsSubform && (elementIsLabel || parentIsLabel || $closestLabel.length)) {
              if (!$elementId) {
                $elementId = $closestLabel.attr('data-plominoid');
              }
              this.log.info('field selected #-d', $elementId, $element.get(0), $closestLabel.get(0));
              this.fieldSelected.emit({
                id: $elementId,
                type: 'label',
                parent: this.id
              });
            } 
            else if (elementIsSubform) {
              /**
               * subform clicked
               */
              let id = $elementId || $parentId;
              if (!id) {
                $element = $element.closest('.plominoSubformClass');
                id = $element.attr('data-plominoid');
              }
              this.log.info('field selected #d');
              this.fieldSelected.emit({ id: id, type: 'subform', parent: this.id });
            }
            else if ($elementId || $parentId) {
              let id = $elementId || $parentId;
                  
              let $elementType = $element.data('plominoid')
                ? this.extractClass($element.attr('class')) : null;

              let $parentType = $parent.data('plominoid') 
                ? this.extractClass($parent.attr('class')) : null;

              let type = $elementType || $parentType;

              this.log.info('field selected #e');
              this.fieldSelected.emit({ id: id, type: type, parent: this.id });
            } else if ($element.children().length
              && $element.children().first().hasClass('plominoLabelClass')
            ) {
              $element = $element.children().first();
              $elementId = $element.attr('data-plominoid');
              this.log.info('field selected #e2', $elementId, $element.get(0));
              this.fieldSelected.emit({
                id: $elementId,
                type: 'label',
                parent: this.id
              });
            } else if ($element.closest('.plominoGroupClass').length) {
              $element = $element.closest('.plominoGroupClass');
              $elementId = $element.attr('data-groupid');
              this.log.info('field selected #e2', $elementId, $element.get(0));
              this.fieldSelected.emit({
                id: $elementId,
                type: 'group',
                parent: this.id
              });
            }
            else if ($element.closest('.plominoSubformClass').length) {
              $element = $element.closest('.plominoSubformClass');
              $elementId = $element.attr('data-plominoid');
              this.log.info('field selected #-f2', $elementId, $element.get(0));
              this.fieldSelected.emit({
                id: $elementId,
                type: 'subform',
                parent: this.id
              });
            } else {
              this.log.info('field selected #f');
              this.fieldSelected.emit(null);
            }
          });
        });

        editor.setDirty(false);
        const $edContainer = $(editor.getContainer());
        if ($edContainer.length) {
          const $saveDiv = $edContainer
            .find('.mce-toolbar-grp div.mce-widget.mce-btn:contains("Save")');
          $saveDiv.attr('aria-disabled', 'true');
          $saveDiv.addClass('mce-disabled');
        }
      },
      content_css: [
        'theme/barceloneta-compiled.css', 'theme/++plone++static/plone-compiled.css'
      ],
      content_style: require('./tinymce.css'),
      menubar: "edit insert view format table tools",
      height : "780",
      resize: false
    });

    this.getFormLayout();

    this.draggingService
    .onPaletteCustomDragEvent()
    .subscribe((eventData: MouseEvent) => {
      this.dragData = this.draggingService.currentDraggingData 
        ? this.draggingService.currentDraggingData 
        : this.draggingService.previousDraggingData;
      
      this.contentManager.selectAndRemoveElementById(this.id, 'drag-autopreview');
      this.dropped({ mouseEvent: eventData });
    });

    this.tabsService.getActiveTab()
      .subscribe((tab) => {
        if (this.item && typeof this.item.formUniqueId === 'undefined') {
          this.item = tab;
          this.changeDetector.markForCheck();
          this.changeDetector.detectChanges();
        }
      });

    this.labelMarkupEvent.asObservable()
    .subscribe(($element: JQuery) => {
      /**
       * when markup changed on any plominoLabelClass element
       */
      const a = $element.text().replace(/\s+/g, ' ').trim();
      const b = $element.html()
        .replace(/&nbsp;/g, ' ')
        .replace(/^(.+?)?<br>$/, '$1')
        .replace(/\s+/g, ' ').trim();
      const hasMarkup = a !== b;
      const dataAdvanced = Boolean($element.attr('data-advanced'));
      this.log.info('a,b', a, b, 'hasMarkup', hasMarkup, 'dataAdvanced', dataAdvanced);

      if (hasMarkup || (dataAdvanced && !hasMarkup)) {
        this.log.info('label markup inserted', $element);
        this.log.extra('tiny-mce.component.ts');
        
        if (hasMarkup) {
          $element.attr('data-advanced', '1');
        }
        else {
          const selectedId = $element.attr('data-plominoid');
    
          this.labelsRegistry.update(
            `${ this.id }/${ selectedId }`, b, 'temporary_title'
          );
        }
      }
      else if (!hasMarkup && !dataAdvanced && b.length === 0) {
        this.log.info('reselected $element');
        this.adapter.select($element);

        const selectedId = $element.attr('data-plominoid');
    
        if (selectedId) {
          this.labelsRegistry.update(
            `${ this.id }/${ selectedId }`, b, 'temporary_title'
          );
        }
      }
    });

    this.activeEditorService.onLoadingPush()
    .subscribe((state: boolean) => {
      // debugger;
      this.log.info('onLoadingPush i am', this.id, 
        'this msg to', this.activeEditorService.editorURL);
      if (this.activeEditorService.editorURL === this.id) {
        this.fallLoading(state);
        this.log.info('fallLoading from onLoadingPush with state', state);
        // this.loading = state;
        // try {
        //   this.changeDetector.markForCheck();
        //   this.changeDetector.detectChanges();
        // }
        // catch (e) {
        //   this.log.error(e);
        // }
      }
      else if (this.activeEditorService.getActive() === null && this.id) {
        tinymce.editors.forEach((editor: any) => {
          if (editor.targetElm && editor.targetElm.id 
            && editor.targetElm.id === this.id
          ) {
            this.fallLoading(state);
            this.log.info('RESTORED fallLoading from onLoadingPush with state', state);
          }
        });
      }
    });

    this.activeEditorService.onSavedPush()
    .subscribe((state: boolean) => {
      if (this.activeEditorService.editorURL === this.id) {
        const editor = tinymce.get(this.id);
        const isDirty = editor.isDirty();

        if (!isDirty) {
          const $edContainer = $(editor.getContainer());
          if ($edContainer.length) {
            const $saveDiv = $edContainer
              .find('.mce-toolbar-grp div.mce-widget.mce-btn:contains("Save")');
            $saveDiv.attr('aria-disabled', 'true');
            $saveDiv.addClass('mce-disabled');
            $(`span[data-url="${ this.id }"] > span:contains("* ")`).remove();
            $(`span[data-url="${ this.id }"] > .tabunsaved`).removeClass('tabunsaved');
          }
        }
      }
    });
  }

  /**
   * because the native angular2 changeDetector is buggable here
   */
  fallLoading(state = true) {
    // debugger;
    const editor = tinymce.get(this.id);
    if (editor) {
      const preloader = editor.getContainer()
        .parentElement.querySelector('plomino-block-preloader');
      (<HTMLElement> preloader.querySelector('.plomino-block-preloader'))
        .style.display = state ? 'flex' : 'none';
    }
    else if (this.id && this.activeEditorService.getActive() === null) {
      /* id is present but no editor here, lets try to find it */
      tinymce.editors.forEach((editor: any) => {
        if (editor.targetElm && editor.targetElm.id 
          && editor.targetElm.id === this.id
        ) {
          /* remove tinymce editor and add it again */
          const preloader = editor.getContainer()
            .parentElement.querySelector('plomino-block-preloader');
          (<HTMLElement> preloader.querySelector('.plomino-block-preloader'))
            .style.display = state ? 'flex' : 'none';
          // editor.remove();
          // tinymce.EditorManager.execCommand('mceAddEditor', true, this.id);
          // tinymce.EditorManager.execCommand('mceAddEditor', true, this.id);

          this.ngAfterViewInit();
        }
      });
    }
  }

  isLoadingNow(): boolean {
    const editor = tinymce.get(this.id);
    if (editor) {
      const preloader = editor.getContainer()
        .parentElement.querySelector('plomino-block-preloader');
      return (<HTMLElement> preloader.querySelector('.plomino-block-preloader'))
        .style.display === 'flex';
    } else {
      return false
    }
  }

  /**
   * calling REST-API and receiving form data
   */
  getFormLayout() {
    this.fallLoading();
    this.log.info('fallLoading from getFormLayout');
    // setTimeout(() => {
    //   if (this.isLoadingNow()) {
    //     this.fallLoading(false);
    //     this.log.warn('the preloader did produce some bug and we removed it');
    //   }
    // }, 2000);
    // this.loading = true;
    // try {
    //   this.changeDetector.markForCheck();
    //   this.changeDetector.detectChanges();
    // }
    // catch (e) {
    //   this.log.error(e);
    // }
    this.elementService.getElementFormLayout(this.id)
    .subscribe((form: PlominoFormDataAPIResponse) => {
      for (let item of form.items) {
        this.labelsRegistry.update(item['@id'], item.title, 'title');
      }
      const data = form.form_layout;
      let newData = '';
      
      if (data && data.length) {
        /* here I will replace the tinymce storage to virtual */
        // this.contentManager.setContent(
        //   this.id, data, this.draggingService
        // );
        this.log.info('first content installed ok');
        // const $inner = $(`iframe[id="${ this.id }_ifr"]`).contents().find('#tinymce');
        // $inner.css('opacity', '0');
        this.autoSavedContent = data;
        const $edIframeFake = $(`<div>${ data }</div>`);
        const loadingElements = this.widgetService.getFormLayout(this.id, $edIframeFake);
        Promise.all(loadingElements).then(() => {
          this.log.info('loading content finished');
          // $inner.css('opacity', '');
          // const $content = $(`<div>${this.contentManager.getContent(this.id)}</div>`);
          const $content = $edIframeFake;
          $content.find('div.plominoLabelClass').each((i, element) => {
            const $element = $(element);
            if ($element.next().length && $element.next().prop('tagName') === 'BR'
            && $element.next().next().length 
            && $element.next().next().prop('tagName') === 'BR') {
              $element.next().next().remove();
            }
          });

          const htmlContent = $content.html();
          this.contentManager.setContent(this.id, htmlContent, this.draggingService);

          this.saveManager.nextEditorSavedState(
            this.id, this.contentManager.getContent(this.id)
          );
          
          this.fallLoading(false);
          // this.loading = false;
          // this.log.info('tiny-mce loading', false, this.id);
          // try {
          //   this.changeDetector.markForCheck();
          //   this.changeDetector.detectChanges();
          // }
          // catch (e) {
          //   this.log.error(e);
          // }

          const editor = tinymce.get(this.id);
          const isDirty = editor.isDirty();

          if (!isDirty) {
            const $edContainer = $(editor.getContainer());
            if ($edContainer.length) {
              const $saveDiv = $edContainer
                .find('.mce-toolbar-grp div.mce-widget.mce-btn:contains("Save")');
              $saveDiv.attr('aria-disabled', 'true');
              $saveDiv.addClass('mce-disabled');
            }
          }
          
        });
      }
      else {
        this.contentManager.setContent(
          this.id, newData, this.draggingService
        );
        this.autoSavedContent = newData;
        this.fallLoading(false);
        
        // this.loading = false;
        // this.log.info('tiny-mce loading', false, this.id);
        // try {
        //   this.changeDetector.markForCheck();
        //   this.changeDetector.detectChanges();
        // }
        // catch (e) {
        //   this.log.error(e);
        // }
      }

    }, (err) => {
      this.log.error(err);
      this.fallLoading(false);
      // this.log.info('tiny-mce loading', false, this.id);
      // this.loading = false;
      // this.changeDetector.markForCheck();
    });
  }

  saveFormLayout(cb:any) {
    this.log.info('calling saveFormLayout', cb.toString(), this.id);
    let tiny = this;
    let editor = tinymce.get(this.id) || tinymce.get(this.idChanges.oldId);

    if (editor !== null) {
      tiny.isLoading.emit(false);
      if (cb) cb();
      this.log.info('onchange not dirty', this.id);
      tiny.isDirty.emit(false);
      editor.setDirty(false);
      // this.loading = false;
      this.theFormIsSavingNow = false;
      this.log.info('tiny-mce loading', false, this.id);
      this.fallLoading(false);
      // try {
      //   this.changeDetector.markForCheck();
      //   this.changeDetector.detectChanges();
      // }
      // catch (e) {
      //   this.log.error(e);
      // }
      this.ngAfterViewInit();
    }
  }

  allowDrop() {
    return () => {
      return this.dragData.type !== 'PlominoForm' 
        ? this.dragData.parent === this.id
        : this.dragData.name !== this.id;
    }
  }

  dropped({ mouseEvent }: any) {
    if (this.dragData === null) {
      this.dragData = this.draggingService.currentDraggingData 
        ? this.draggingService.currentDraggingData 
        : this.draggingService.previousDraggingData;
    }

    if (this.dragData === null) {
      return false;
    }

    let targetGroup = this.draggingService.target === null 
      ? null : this.draggingService.target.get(0);

    if (!targetGroup) {
      const $iframeContents = $(this.activeEditorService.getActive()
          .getContainer().querySelector('iframe')).contents();
      const $latestTarget = $(
        $.merge(
          $iframeContents.find('#tinymce *:first').toArray(),
          $iframeContents.find('#tinymce *:not(.mce-visual-caret)')
          .filter(function (i, tag) {
            return $(tag).html().replace(/&nbsp;/g, '').trim() 
              && !($(tag).closest('.plominoGroupClass').length 
              && !$(tag).hasClass('plominoGroupClass'));
            }).toArray()
        )
      ).last();
      targetGroup = $latestTarget.get(0);
    }
    this.draggingService.target = null;
    
    if (this.dragData.resolved) {
      this.addElement(this.dragData);
    } else {
      this.resolveDragData(targetGroup, this.dragData, this.dragData.resolver);
    }

    this.draggingService.currentDraggingData = null;
  }

  /**
   * this method calling on observable subject triggering
   * fieldsService.listenToUpdates()
   * 
   * after fieldsettings.component.ts calling submitForm()
   */
  private updateField(updateData: PlominoFieldUpdatesStreamEvent) {
    const context = this;
    this.log.info('tinymce -> updateField callback', updateData);

    let originalTitle = this.labelsRegistry.get(updateData.fieldData.url);
    const editor = tinymce.get(this.id);
    if (!editor) {
      this.log.error('editor did not appear', this.id);
      return;
    }
    const dataToUpdate = $(editor.getBody())
      .find(`*[data-plominoid="${updateData.fieldData.id.split('/').pop()}"]`)
      .filter(function () {
        const $plominoElement = $(this);
        if (originalTitle === null && $plominoElement.hasClass('plominoLabelClass')) {
          context.labelsRegistry.update(
            updateData.fieldData.url, $plominoElement.html().trim()
          );
          originalTitle = $plominoElement.html().trim();
        }
        return $plominoElement.closest('.mce-offscreen-selection').length === 0;
      })
      .toArray();

    this.log.info('originalTitle', originalTitle);

    if (dataToUpdate.length) {
      const hwPos = { start: false, end: false };
      let i = 0;
      Observable.from(dataToUpdate).map((element) => {
        /* WTF? */
        let normalizedType = $(element).attr('class')
          .split(' ')[0].slice(7, -5);
        let typeCapitalized = normalizedType[0].toUpperCase() +
          normalizedType.slice(1);

        let newTitle = updateData.newData.title;

        if (normalizedType === 'Label' && originalTitle !== element.innerText) {
          newTitle = element.innerHTML;
        }

        return <PlominoUpdatingItemData> {
          base: this.id,
          type: normalizedType,
          newId: updateData.newId,
          oldTemplate: element,
          newTitle
        };
      })
      .flatMap((itemToReplace: PlominoUpdatingItemData) => {
        return this.updateFieldService.updateField(itemToReplace);
      })
      .subscribe((data) => {
        if (data.item && data.item.type === 'Hidewhen') {
          let $position = $(data.oldTemplate).data('plominoPosition');
          if (hwPos[$position]) {
            return false;
          }
          else {
            hwPos[$position] = true;
          }
        }
        else {
          this.log.info('dataToUpdate subscribe enter', dataToUpdate, ++i, data);
          this.log.extra(`tiny-mce.component.ts, data: ${ JSON.stringify(data) }`);
        }

        data.newTemplate = 
          this.adapter.endPoint(data.item.type.toLowerCase(), data.newTemplate);

        this.contentManager.selectContent(this.id, data.oldTemplate);
        this.contentManager.setSelectionContent(this.id, data.newTemplate);
      });
    }
  }

  private addElement(
    element: InsertFieldEvent
  ) {
    this.log.info('addElement', element);

    let type: string;
    let elementClass: string;
    let elementEditionPage: string;
    let elementIdName: string;

    let elementId: string = element.name.split('/').pop();
    let baseUrl: string = element.name.slice(0, element.name.lastIndexOf('/'));
    
    switch (element.type) {
      case 'PlominoField':
        elementClass = 'plominoFieldClass';
        elementEditionPage = '@@tinymceplominoform/field_form';
        elementIdName = 'fieldid';
        type = 'field';
        break;

      case 'PlominoLabel':
        elementClass = 'plominoLabelClass';
        elementEditionPage = '@@tinymceplominoform/label_form';
        elementIdName = 'labelid';
        type = 'label';
        break;

      case 'PlominoAction':
        elementClass = 'plominoActionClass';
        elementEditionPage = '@@tinymceplominoform/action_form';
        elementIdName = 'actionid';
        type = 'action';
        break;

      case 'PlominoForm':
      case 'PlominoSubform':
        elementClass = 'plominoSubformClass';
        elementEditionPage = '@@tinymceplominoform/subform_form';
        elementIdName = 'subformid';
        type = 'subform';

        if (elementId === 'defaultSubform' && element.subformHTML) {
          elementId = element.title;
        }
        break;

      case 'PlominoHidewhen':
        elementClass = 'plominoHidewhenClass';
        elementEditionPage = '@@tinymceplominoform/hidewhen_form';
        elementIdName = 'hidewhenid';
        type = 'hidewhen';
        break;

      case 'PlominoCache':
        elementClass = 'plominoCacheClass';
        elementEditionPage = '@@tinymceplominoform/cache_form';
        elementIdName = 'cacheid';
        type = 'cache';
        break;

      case 'PlominoPagebreak':
        $(tinymce.get(this.id).getBody())
          .find('.drag-autopreview').remove(); // just in case
        this.contentManager.insertContent(
          this.id, this.draggingService,
          '<hr class="plominoPagebreakClass">',
          { target: element.target }
        );
        return;

      default: return;
    }

    this.log.info('element.target', element.target);

    let target: any = element.target || null;
    let subformHTML: string = element.subformHTML || null;

    this.insertElement(target, baseUrl, type, elementId, subformHTML);
  }

  private insertElement(
    target: any, baseUrl: string, type: string, value: string, option?: string
  ) {
    let ed: any = tinymce.get(this.id);
    let selection: any = ed.selection.getNode();
    let title: string;
    let plominoClass: string;
    let content: string;

    var container = 'span';

    if (type === 'action') {
      plominoClass = 'plominoActionClass';
    } else if (type === 'field') {
      plominoClass = 'plominoFieldClass';
      container = "div";
    } else if (type === 'subform') {
      plominoClass = 'plominoSubformClass';
      container = "div";
    } else if (type === 'label') {
      plominoClass = 'plominoLabelClass';
      if (option == '0') {
        container = "span";
      } else {
        container = "div";
      }
    }
        
    if (type == 'label') {
      this.elementService.getWidget(baseUrl, type, value)
      .subscribe((widgetTemplate: any) => {
        this.contentManager.insertContent(
          this.id, this.draggingService,
          `${widgetTemplate}`, { skip_undo: 1, target }
        );
      });
    }
    else if (type == 'subform') {
      ((): Observable<string> => {
        if (value !== 'defaultSubform') {
          return Observable.of(option);
        }
        else {
          return this.elementService.getWidget(baseUrl, type, null)
        }
      })()
      .subscribe((widgetTemplate: any) => {
        this.contentManager.insertContent(
          this.id, this.draggingService,
          `<div class="plominoSubformClass mceNonEditable"
          ${ (value !== 'defaultSubform') ? ` data-plominoid="${ value }"` : '' }
          >${widgetTemplate}</div>`, { skip_undo: 1, target }
        );
      });
    }
    else if (plominoClass !== undefined) {
      this.elementService.getWidget(baseUrl, type, value)
      .subscribe((response) => {
        let responseAsElement = $(response);
        let container = 'span';

        selection = ed.selection.getNode();

        if (responseAsElement.find('div,table,p').length) {
          container = 'div';
        }

        if (response != undefined) {
          content = '<' + container + ' class="' + plominoClass + 
            ' mceNonEditable" data-mce-resize="false" data-plominoid="' +
            value + '">' + response + '</' + container + '>';
        }
        else {
          content = '<span class="' + plominoClass + '">' + value + '</span>';
        }

        this.contentManager.insertContent(
          this.id, this.draggingService, content, { skip_undo: 1, target }
        );

        this.tabsService.selectField({
          id: value,
          type: `Plomino${type}`,
          parent: this.id
        });
      });
		}
    else if (type == "hidewhen" || type == 'cache') {
      // Insert or replace the selection
      let cssclass = 'plomino' +
        type.charAt(0).toUpperCase() +
        type.slice(1) + 'Class';

			// If the node is a <span class="plominoFieldClass"/>, select all its content
			if (tinymce.DOM.hasClass(selection, cssclass)) {
        // get the old hide-when id
        let oldId = selection.getAttribute('data-plominoid');
        let pos = selection.getAttribute('data-plomino-position')

				// get a list of hide-when opening and closing spans
				let hidewhens = this.contentManager.selectDOM(this.id, 'span.' + cssclass);

				// find the selected span
				var i: number;
				for (i = 0; i < hidewhens.length; i++) {
					if (hidewhens[i] == selection)
						break;
				}

				// change the corresponding start/end
				if (pos == 'start') {
					selection.setAttribute('data-plominoid', value);

					for (; i < hidewhens.length; i++) {
						if (hidewhens[i] &&
              hidewhens[i].getAttribute('data-plominoid') == oldId &&
              hidewhens[i].getAttribute('data-plomino-position') == 'end') {
							hidewhens[i].setAttribute('data-plominoid', value);
							break;
						}
					}
				} else {
				    // change the corresponding start by going backwards
					selection.setAttribute('data-plominoid', value);

					for (; i >= 0; i--) {
						if (hidewhens[i] &&
              hidewhens[i].getAttribute('data-plominoid') == oldId &&
              hidewhens[i].getAttribute('data-plomino-position') == 'start') {
							hidewhens[i].setAttribute('data-plominoid', value);
							break;
						}
					}
				}
			} else {
				let zone = '<span class="' + cssclass + ' mceNonEditable" data-plominoid="' + 
          value + '" data-plomino-position="start">&nbsp;</span>' +
          ed.selection.getContent() +
          '<span class="' + cssclass + ' mceNonEditable" data-plominoid="' + 
          value + '" data-plomino-position="end">&nbsp;</span>';
				
        this.contentManager.insertContent(
          this.id, this.draggingService, zone, { skip_undo: 1, target }
        );
			}
      
      this.tabsService.selectField({
        id: value,
        type: `Plomino${type}`,
        parent: this.id
      });
		}
	}

  private insertGroup(group: string, target?: any) {
    this.contentManager.insertContent(
      this.id, this.draggingService, group, { skip_undo: 1, target: target }
    );
  }
  
  private resolveDragData(target: any, data: any, resolver: any): void {
    resolver(target, data);
  }

  private extractClass(classString: string): string {
    if (!classString) return null;
    let type = classString.split(' ')[0].slice(0, -5);
    return type.indexOf('plomino') > -1 ? type : null;
  }
}
