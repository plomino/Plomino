import { PlominoTabsManagerService } from './../../services/tabs-manager/index';
import { PlominoHTTPAPIService } from './../../services/http-api.service';
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
    Response,
    RequestOptions
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
  PlominoSaveManagerService,
  PlominoFormFieldsSelectionService,
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
  subscriptions: Subscription[] = [];

  autoSaveTimer: any = null;
  autoSavedContent: string = null;

  theFormIsSavingNow: boolean = false;
  loadedFirstTime: boolean = null;
  registry: any;
  tinyMCEPatData: string = null;

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
    private formFieldsSelection: PlominoFormFieldsSelectionService,
    private activeEditorService: PlominoActiveEditorService,
    private updateFieldService: UpdateFieldService,
    private contentManager: TinyMCEFormContentManagerService,
    private saveManager: PlominoSaveManagerService,
    private tabsManagerService: PlominoTabsManagerService,
    private http: PlominoHTTPAPIService,
    private zone: NgZone
  ) {
    this.log.info(this.item, 'tinymce constructed');
    
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
        // this.saveManager.enqueueNewFormSaveProcess(this.item.url);
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
          const $selected = 
            this.adapter.getSelectedPosition() || this.adapter.getSelected();
          insertion.target = $selected && $selected.prop('tagName') !== 'BODY' 
            ? ($selected.prev().length 
            ? $selected.prev().get(0) : $selected.get(0)) : null;
          // console.warn(insertion.target, $selected);
        }
        this.log.info('insertion template', insertion);
        this.insertGroup(insertion.group, insertion.target);

        /* form save automatically */
        // this.saveTheForm(); // was before
        this.saveManager.enqueueNewFormSaveProcess(this.item.url); // now async
      }
    });
    
    this.draggingSubscription = this.draggingService.getDragging()
    .subscribe((dragData: any) => {
      this.dragData = dragData;
      this.isDragged = !!dragData;
      this.changeDetector.markForCheck();
    });

    const activeFieldSubscribtion = this.formFieldsSelection.getActiveField()
    .subscribe((fieldData: any) => {
      if (fieldData && fieldData.type === 'PlominoField'
        && fieldData.id && fieldData.url.replace(`/${ fieldData.id }`, '') === this.id
      ) {
        if (this.getEditor()) {
          const $body = $(this.getEditor().getBody());
          let $element = $body
            .find(`.plominoFieldClass[data-plominoid="${ fieldData.id }"]`);
          if ($element.length) {
            if ($element.closest('.plominoGroupClass').length) {
              $element = $element.closest('.plominoGroupClass');
            }
            $body.animate({ scrollTop: $element.offset().top },
              { duration: 'medium', easing: 'swing' });
            
            /* if the $element is not selected - click on it */
            if ($element.hasClass('plominoGroupClass')) {
              const $field = $element.find('.plominoFieldClass');
              if ($field.length) {
                $body.find('.plominoFieldClass--selected')
                  .removeClass('plominoFieldClass--selected');
                $field.addClass('plominoFieldClass--selected');
              }
            }
            else if ($element.hasClass('plominoFieldClass')) {
              $body.find('.plominoFieldClass--selected')
                .removeClass('plominoFieldClass--selected');
              $element.addClass('plominoFieldClass--selected');
            }
          }
        }
      }
    });

    this.subscriptions.push(activeFieldSubscribtion);

    this.subscriptions.push(this.fieldsService.listenToUpdates()
    .subscribe((updateData) => { this.updateField(updateData); }));

    const idChangeSub = this.formsService.formIdChanged$.subscribe((data) => {
      this.idChanges = Object.assign({}, data);
      if (this.activeEditorService.editorURL === data.oldId) {
        this.log.info('set active url', data.newId);
        this.log.extra('tiny-mce.component.ts');
        this.activeEditorService.setActive(data.newId);
      }
    });

    this.subscriptions.push(idChangeSub);

    const contSaveSub = this.formsService
      .formContentSave$.subscribe((data) => {
      try {
        this.changeDetector.detectChanges();
      }
      catch (e) {
        this.log.error(e);
      }

      if (data.url !== this.item.url)
        return;

      this.isLoading.emit(true);

      let editor = this.getEditor() || 
        this.getEditor(this.idChanges && this.idChanges.oldId);

      editor.setDirty(false);
      this.log.info('i am', this.id, 'and I doing call saveFormLayout');
      this.saveFormLayout(data.cb);
    } );

    this.subscriptions.push(contSaveSub);

    const formBeforeSaveSub = this.formsService
      .getFormContentBeforeSave$.subscribe((data:{id:any}) => {
      if (data.id !== this.item.url)
        return;

      this.theFormIsSavingNow = true;
      this.fallLoading();
      this.log.info('fallLoading from getFormContentBeforeSave$');

      this.formsService.onFormContentBeforeSave({
        id: data.id,
        content: this.contentManager.getContent(this.id)
      });
    });

    this.subscriptions.push(formBeforeSaveSub);

    const mcePatternSub = this.formsService.tinyMCEPatternData$
      .subscribe((data) => {
        if (this.id.split('/').pop() === data.formId) {
          const tinyMCEPatData = this.modifyDataPatParams(data.data);
          if (tinyMCEPatData !== this.tinyMCEPatData) {
            this.tinyMCEPatData = tinyMCEPatData;
            this.ngAfterViewInit();
          }
        }
      });

    this.subscriptions.push(mcePatternSub);

    const bgProcSub = this.saveManager.onBackgroundSaveProcessComplete()
      .subscribe((formURL: string) => {
        if (formURL === this.id) {
          this.bitDirtyStateAfterSave();
        }
      });

    this.subscriptions.push(bgProcSub);
  }

  ngOnDestroy() {
    const edId = this.id.split('/').pop();
    this.log.info(this.item.url, 'tinymce destroyed');
    if (this.activeEditorService.editorURL === this.item.url) {
      this.activeEditorService.setActive(null);
    }
    this.draggingSubscription.unsubscribe();
    this.insertionSubscription.unsubscribe();
    this.templatesSubscription.unsubscribe();
    for (let sub of this.subscriptions) {
      sub.unsubscribe();
    }
    this.subscriptions = [];
    try {
      tinymce.EditorManager
        .execCommand('mceRemoveEditor', true, edId);
    }
    catch (e) {
      tinymce.editors.forEach((editor, index) => {
        if (editor.id === edId) {
          tinymce.editors.splice(index, 1);
          return false;
        }
      });

      Object.keys(tinymce.editors).forEach((key) => {
        if (key === edId) {
          delete tinymce.editors[key];
          return false;
        }
      });
    }
  }

  bitDirtyStateAfterSave() {
    this.theFormIsSavingNow = false;
    this.getEditor().setDirty(false);
    this.isDirty.emit(false);
    this.tabsManagerService.setActiveTabDirty(false);
    this.saveManager.nextEditorSavedState(this.id);
    this.changeDetector.markForCheck();
  }

  saveTheForm() {
    this.fallLoading();
    this.log.info('fallLoading from saveTheForm', this.item.formUniqueId, this.id);
    this.theFormIsSavingNow = true;

    this.saveManager
      .createFormSaveProcess(this.item.url)
      .start()
      .subscribe(() => {
        this.fallLoading(false);
        this.bitDirtyStateAfterSave();
      });
  }

  ngAfterViewInit(): void {
    this.activeEditorService.setActive(this.item.url);
    this.log.info(this.item.url, 'tinymce view initialized');
    window['$'] = jQuery;
    window['registryPromise'].then((registry: any) => {
      this.registry = registry;
      this.initialize();

      this.draggingService
      .onPaletteCustomDragEvent()
      .subscribe((eventData: MouseEvent) => {
        this.dragData = this.draggingService.currentDraggingData 
          ? this.draggingService.currentDraggingData 
          : this.draggingService.previousDraggingData;
        
        this.contentManager.selectAndRemoveElementById(this.id, 'drag-autopreview');
        this.dropped({ mouseEvent: eventData });
      });

      this.tabsManagerService.getActiveTab()
        .filter((tab) => tab !== null)
        .subscribe((tab) => {
          if (this.item && typeof this.item.formUniqueId === 'undefined') {
            this.item = {
              label: tab.label || tab.id,
              url: tab.url,
              editor: tab.editor
            };
            try {
              this.changeDetector.markForCheck();
              this.changeDetector.detectChanges();
            }
            catch (e) {}
          }
        });
  
      // this.tabsService.getActiveTab()
      //   .subscribe((tab) => {
      //     if (this.item && typeof this.item.formUniqueId === 'undefined') {
      //       this.item = tab;
      //       this.changeDetector.markForCheck();
      //       this.changeDetector.detectChanges();
      //     }
      //   });
  
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
        this.log.info('onLoadingPush i am', this.id, 
          'this msg to', this.activeEditorService.editorURL);
        if (this.activeEditorService.editorURL === this.id) {
          this.fallLoading(state);
          this.log.info('fallLoading from onLoadingPush with state', state);
        }
        else if (this.activeEditorService.getActive() === null && this.id) {
          tinymce.editors.forEach((editor: any) => {
            if (editor.targetElm && editor.targetElm.id 
              && editor.targetElm.id === (this.id ? this.id.split('/').pop() : null)
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
          const editor = this.getEditor();
          if (!editor) { return; }
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
    });
  }

  /**
   * @param dataPat data-pat-tinymce
   */
  modifyDataPatParams(dataPat: string): string {
    const patObject = JSON.parse(dataPat);
    patObject.inline = false;
    patObject.tiny.height = 780;
    patObject.tiny.resize = false;
    patObject.tiny.forced_root_block = '';
    patObject.tiny.cleanup = false;
    patObject.tiny.content_css = patObject.tiny.content_css.split(',');
    patObject.tiny.content_css = [patObject.tiny.content_css[2]];
    patObject.tiny.content_css.push('theme/barceloneta-compiled.css');
    patObject.tiny.content_css.push('theme/++plone++static/plone-compiled.css');
    patObject.tiny.content_css.push('theme/tinymce.css');
    patObject.tiny.content_css.push('../../../++plone++static/tinymce-styles.css');
    patObject.tiny.plugins = ['code', 'save', 'importcss', 'noneditable', 
      'preview', 'ploneimage', 'plonelink', 'hr', 
      'lists', 'media', 'table'],
    patObject.tiny.toolbar = 
      'undo redo | styleselect | bold italic underline | ' +
      'alignleft aligncenter alignright alignjustify | ' +
      'bullist numlist | outdent indent' +
      'plonelink unlink ploneimage';
    // patObject.tiny.toolbar = 'save | ' + patObject.tiny.toolbar;
    // patObject.tiny.plugins.push('save');
    // const saveTrigger = `window['save_onsavecallback_${ this.id.split('/').pop() }']`;
    // patObject.tiny.save_onsavecallback = `function(){${ saveTrigger }?${ saveTrigger }():null}`;
    delete patObject.tiny.external_plugins; // does not work good
    return JSON.stringify(patObject);
  }

  onSaveCallback() {
    this.fallLoading();
    this.log.info('fallLoading from save_onsavecallback');
    this.saveTheForm();
  }

  initialize(): void {
    if (!this.tinyMCEPatData) { return; }
    const edId = this.id.split('/').pop();
    const $el = $('textarea#' + edId);
    $el.attr('data-pat-tinymce', this.tinyMCEPatData);
    this.zone.runOutsideAngular(() => {
      this.registry.scan($el);
    });

    window['save_onsavecallback_' 
      + this.id.split('/').pop()] = this.onSaveCallback.bind(this);

    setTimeout(() => {
      const editor = tinymce.get(edId);
      editor.onChange.add(this.onTinyMCEEditorChange.bind(this));
      editor.onKeyDown.add(this.onTinyMCEEditorKeyDown.bind(this));
      editor.onKeyUp.add(this.onTinyMCEEditorKeyUp.bind(this));
      editor.onNodeChange.add(this.onTinyMCEEditorNodeChange.bind(this));
      // editor.onActivate.add(this.onTinyMCEEditorChange.bind(this));
      editor.onMouseDown.add(this.onTinyMCEEditorMouseDown.bind(this));
      this.editorInstance = editor;
      this.editorInstance.show();
      this.bitDirtyStateAfterSave();

      if (editor) {
        // editor.setDirty(false);
        const $edContainer = $(editor.getContainer());
        if ($edContainer.length) {
          const $saveDiv = $edContainer
            .find('.mce-toolbar-grp div.mce-widget.mce-btn:contains("Save")');
          $saveDiv.attr('aria-disabled', 'true');
          $saveDiv.addClass('mce-disabled');
          const $iframe = $edContainer.find('iframe');
          const iframeDocument = (<HTMLIFrameElement> $iframe.get(0))
            .contentWindow.document;
          iframeDocument.addEventListener('keydown', (e) => {
            return this.beforeTinyMCEEditorKeyDown(editor, e);
          }, true);
          $iframe.css('height', 'calc(100vh - 226px)');
        }

        this.getFormLayout();
      }
    }, 300);
  }

  /**
   * because the native angular2 changeDetector is buggable here
   */
  fallLoading(state = true) {
    if (state === false) {
      this.loadedFirstTime = this.loadedFirstTime === null;
    }
    const editor = this.getEditor();
    if (editor && editor.getContainer() !== null) {
      const preloader = editor.getContainer()
        .parentElement.querySelector('plomino-block-preloader');
      (<HTMLElement> preloader.querySelector('.plomino-block-preloader'))
        .style.display = state ? 'flex' : 'none';
    }
    else if (this.id && this.activeEditorService.getActive() === null) {
      /* id is present but no editor here, lets try to find it */
      tinymce.editors.forEach((editor: any) => {
        const id = this.id.split('/').pop();
        if (editor.targetElm && editor.targetElm.id 
          && editor.targetElm.id === id
        ) {
          /* remove tinymce editor and add it again */
          const preloader = editor.getContainer()
            .parentElement.querySelector('plomino-block-preloader');
          (<HTMLElement> preloader.querySelector('.plomino-block-preloader'))
            .style.display = state ? 'flex' : 'none';

          editor.id = id;
          editor.settings.id = id;
          editor.getContainer().firstElementChild
            .children[2].firstElementChild.id = id + '_ifr';
          editor.render();

          this.ngAfterViewInit();
        }
      });
    }
  }

  onTinyMCEEditorChange() {
    if (this.activeEditorService.editorURL === this.id 
      && !this.theFormIsSavingNow
      && this.saveManager.isEditorUnsaved(this.id)) {
      this.isDirty.emit(true);
    }
  }

  onTinyMCEEditorNodeChange(editor: TinyMceEditor, nodeChangeEvent: any) {
    if (nodeChangeEvent.selectionChange === true) {
      const $label = $(nodeChangeEvent.element).closest('.plominoLabelClass');

      if ($label.length) {
        this.labelMarkupEvent.next($label);
      }
    }
  }

  beforeTinyMCEEditorKeyDown(editor: TinyMceEditor, e: KeyboardEvent) {
    if (e.keyCode === 8) { // BACKSPACE PRESSED
      const editor = this.getEditor();
      if (!editor) { return true; }

      const rng = editor.selection.getRng();
      if (!(rng && rng.startContainer)) { return true; }

      const container: HTMLElement = rng.startContainer;
      const parent = <HTMLElement> container.parentElement;
      const contPrev = <HTMLElement> container.previousElementSibling;

      if (contPrev && contPrev.classList.contains('plominoHidewhenClass')) {
        $(editor.getBody())
          .find('[data-plominoid="' + contPrev.dataset.plominoid + '"]')
          .remove();
      }
      
      if (!(
        parent && parent.tagName === 'P' 
        && !(parent.innerText.trim()).length
      )) {
        return true;
      }

      const prev = <HTMLElement> parent.previousElementSibling;
      const next = <HTMLElement> parent.nextElementSibling;
      if (!prev || !next) { return true; }

      /**
       * @see https://trello.com/c/89jSvQ7A/242-deleting-p-between-non-editable-elements
       */
      if (prev.tagName === 'DIV' 
        && !(next.tagName === 'P' && next.innerHTML === '&nbsp;')
      ) {
        /* prevent default and remove parent */
        $(parent).remove();

        /** start do nothing */
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        return false;
        /** end do nothing */
      }
    }
  }

  onTinyMCEEditorKeyDown(editor: TinyMceEditor, e: KeyboardEvent) {
    if (e.keyCode === 8) { // BACKSPACE PRESSED
      const editor = this.getEditor();
      if (!editor) { return; }
      const rng = editor.selection.getRng();
      if (!(rng && rng.startContainer)) { return; }
      const container: HTMLElement = rng.startContainer;
      const prev = <HTMLElement> container.previousElementSibling;

      /* deleting hidewhen by backspace with cursor at right */
      if (prev && prev.classList.contains('plominoHidewhenClass')) {
        $(editor.getBody())
          .find('[data-plominoid="' + prev.dataset.plominoid + '"]')
          .remove();
      }
    }
    else if (e.keyCode === 46) { // DELETE PRESSED
      const editor = this.getEditor();
      if (!editor) { return; }
      const rng = editor.selection.getRng();
      if (!(rng && rng.startContainer)) { return; }
      const container: HTMLElement = rng.startContainer;
      const next = <HTMLElement> container.nextElementSibling;

      /* deleting hidewhen by backspace with cursor at right */
      if (next && next.classList.contains('plominoHidewhenClass')) {
        $(editor.getBody())
          .find('[data-plominoid="' + next.dataset.plominoid + '"]')
          .remove();
      }
    }
  }

  onTinyMCEEditorKeyUp(editor: TinyMceEditor, ev: KeyboardEvent) {
    /* check current selected element is there */
    const $selected = this.adapter.getSelected();
    editor = this.getEditor();
    if (!editor) { return; }

    const $edBody = $(editor.getBody());

    if ($selected && !$edBody.has(<any> $selected).length) { // BACKSPACE/DEL

      /** element was deleted */
      if ($selected.hasClass('plominoHidewhenClass')) {
        $edBody
          .find('[data-plominoid="' + $selected.attr('data-plominoid') + '"]')
          .remove();
      }

      this.formFieldsSelection.selectField('none');
      this.adapter.select(null);
    }
  }

  onTinyMCEEditorMouseDown(editor: TinyMceEditor, ev: MouseEvent) {
    // setTimeout(() => {
    //   $('body > plomino-app > div > div > main').get(0).scrollTop = 0;
    // }, 1);
    const eventCustomCheck = this.saveManager.detectNewIFrameInnerClick(ev);

    eventCustomCheck
    .then(() => {
      /* #region: custom check */
      let $element = $(ev.target);
      this.adapter.selectPosition($element);

      this.zone.run(() => {
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
          this.formFieldsSelection.selectField({
            id: $element.attr('data-groupid'),
            type: 'group',
            parent: this.id
          });
        }
        else if (!elementIsSubform && (elementIsLabel 
          || parentIsLabel || $closestLabel.length)) {
          if (!$elementId) {
            $elementId = $closestLabel.attr('data-plominoid');
          }
          this.formFieldsSelection.selectField({
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
          this.formFieldsSelection.selectField({
            id: id, type: 'subform', parent: this.id });
        }
        else if ($elementId || $parentId) {
          let id = $elementId || $parentId;
              
          let $elementType = $element.data('plominoid')
            ? this.extractClass($element.attr('class')) : null;

          let $parentType = $parent.data('plominoid') 
            ? this.extractClass($parent.attr('class')) : null;

          let type = $elementType || $parentType;

          this.formFieldsSelection.selectField({ 
            id: id, type: type, parent: this.id });
        } else if ($element.children().length
          && $element.children().first().hasClass('plominoLabelClass')
        ) {
          $element = $element.children().first();
          $elementId = $element.attr('data-plominoid');
          this.formFieldsSelection.selectField({
            id: $elementId,
            type: 'label',
            parent: this.id
          });
        } else if ($element.closest('.plominoGroupClass').length) {
          $element = $element.closest('.plominoGroupClass');
          $elementId = $element.attr('data-groupid');
          this.formFieldsSelection.selectField({
            id: $elementId,
            type: 'group',
            parent: this.id
          });
        }
        else if ($element.closest('.plominoSubformClass').length) {
          $element = $element.closest('.plominoSubformClass');
          $elementId = $element.attr('data-plominoid');
          this.formFieldsSelection.selectField({
            id: $elementId,
            type: 'subform',
            parent: this.id
          });
        } else {
          this.formFieldsSelection.selectField(null);
        }
      });
      /* #endregion */
    })
    .catch(() => {
      ev.preventDefault();
      this.log.warn('prevented');
    });
  }

  isLoadingNow(): boolean {
    const editor = this.getEditor();
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
    
    this.elementService.getElementFormLayout(this.id)
    .subscribe((form: PlominoFormDataAPIResponse) => {
      for (let item of form.items) {
        this.labelsRegistry.update(item['@id'], item.title, 'title');
        this.labelsRegistry.update(item['@id'], item['@type'], '@type');
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
          const editor = this.getEditor();
          if (!editor) { return; }
          const isDirty = editor.isDirty();

          if (editor && this.loadedFirstTime) {
            setTimeout(() => {
              $(editor.getBody())
              .animate(
                { scrollTop: 0 },
                { duration: 'medium', easing: 'swing' }
              );
            }, 100);
          }

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
      }

    }, (err) => {
      this.log.error(err);
      this.fallLoading(false);
    });
  }

  saveFormLayout(cb:any) {
    this.log.info('calling saveFormLayout', cb.toString(), this.id);
    let tiny = this;
    let editor = this.getEditor() || this.getEditor(this.idChanges.oldId);

    if (editor !== null) {
      tiny.isLoading.emit(false);
      if (cb) cb();
      this.log.info('onchange not dirty', this.id);
      tiny.isDirty.emit(false);
      editor.setDirty(false);
      this.theFormIsSavingNow = false;
      this.log.info('tiny-mce loading', false, this.id);
      this.fallLoading(false);
      this.initialize();
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
    const editor = this.getEditor();
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
        $(this.getEditor().getBody())
          .find('.drag-autopreview').remove(); // just in case
        this.contentManager.insertContent(
          this.id, this.draggingService,
          '<hr class="plominoPagebreakClass">',
          { target: element.target }
        );
        this.saveManager.enqueueNewFormSaveProcess(this.item.url);
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
    let ed = this.getEditor();
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
        this.saveManager.enqueueNewFormSaveProcess(this.item.url);
      });
    }
    else if (type == 'subform') {
      ((): Observable<string> => {
        if (value !== 'defaultSubform') {
          return Observable.of(option);
        }
        else {
          return this.elementService.getWidget(baseUrl, type, null);
        }
      })()
      .subscribe((widgetTemplate: any) => {
        this.contentManager.insertContent(
          this.id, this.draggingService,
          `<div class="plominoSubformClass mceNonEditable"
          ${ (value !== 'defaultSubform') ? ` data-plominoid="${ value }"` : '' }
          >${widgetTemplate}</div>`, { skip_undo: 1, target }
        );
        this.saveManager.enqueueNewFormSaveProcess(this.item.url);
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

        this.saveManager.enqueueNewFormSaveProcess(this.item.url);

        this.formFieldsSelection.selectField({
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

      this.saveManager.enqueueNewFormSaveProcess(this.item.url);
      
      this.formFieldsSelection.selectField({
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

  private getEditor(id = this.id) {
    const edId = id ? id.split('/').pop() : null;
    return tinymce.get(edId);
  }
}
