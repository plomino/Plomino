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

import {DND_DIRECTIVES} from 'ng2-dnd/ng2-dnd';

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
    WidgetService,
    TabsService,
    FormsService
} from '../../services';

import { UpdateFieldService } from './services';

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
    directives: [DND_DIRECTIVES],
    providers: [ElementService, UpdateFieldService],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class TinyMCEComponent implements AfterViewInit, OnDestroy {

  @Input() id: string;
  @Input() item: any;
  @Output() isDirty: EventEmitter<any> = new EventEmitter();
  @Output() isLoading: EventEmitter<any> = new EventEmitter();
  @Output() fieldSelected: EventEmitter<any> = new EventEmitter();

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

  constructor(private elementService: ElementService,
    private fieldsService: FieldsService,
    private draggingService: DraggingService,
    private templatesService: TemplatesService,
    private widgetService: WidgetService,
    private formsService: FormsService,
    private changeDetector: ChangeDetectorRef,
    private tabsService: TabsService,
    private updateFieldService: UpdateFieldService,
    private contentManager: TinyMCEFormContentManagerService,
    private http: Http,
    private zone: NgZone) {
    this.insertionSubscription = this.fieldsService.getInsertion()
    .subscribe((insertion) => {
      let insertionParent = insertion.name.slice(0, insertion.name.lastIndexOf('/'));
      let dataToInsert = Object.assign({}, insertion, { 
        type: insertion['@type']
      });
      if (insertionParent === this.id) {
        this.addElement(dataToInsert);
        this.changeDetector.markForCheck();
      }
    });

    this.templatesSubscription = this.templatesService.getInsertion()
    .subscribe((insertion) => {
      let parent = insertion.parent;
      if (insertion.parent === this.id) {
        console.log('insertion', insertion);
        this.insertGroup(insertion.group, insertion.target);
        this.changeDetector.markForCheck();
      }
    });
    
    this.draggingSubscription = this.draggingService.getDragging()
    .subscribe((dragData: any) => {
      this.dragData = dragData;
      this.isDragged = !!dragData;
      this.changeDetector.markForCheck();
    });

    this.fieldsService.listenToUpdates()
    .subscribe((updateData) => { this.updateField(updateData); });

    this.formsService.formIdChanged$.subscribe((data) => {
      this.idChanges = Object.assign({}, data);
    });

    this.formsService.formContentSave$.subscribe((data) => {
      this.changeDetector.detectChanges();

      if(data.formUniqueId !== this.item.formUniqueId)
        return;

      this.isLoading.emit(true);

      let editor = tinymce.get(this.id) || 
        tinymce.get(this.idChanges && this.idChanges.oldId);

      editor.buttons.save.onclick();

      this.saveFormLayout(data.cb);
    } );

    this.formsService.getFormContentBeforeSave$.subscribe((data:{id:any}) => {
      if (typeof this.item.formUniqueId === 'undefined') {
        this.item.formUniqueId = data.id;
      }
      
      if (data.id !== this.item.formUniqueId)
        return;

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
    tinymce.EditorManager.execCommand('mceRemoveEditor',true, this.id);
  }

  ngAfterViewInit(): void {
    let tiny = this;

    const LinkModal = window['LinkModal'];

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
        'preview', 'ploneimage', 'plonelink'],
      toolbar: 'save | undo redo | formatselect | bold italic underline' +
      ' | alignleft aligncenter alignright alignjustify | ' +
      'bullist numlist | outdent indent | ' +
      'plonelink unlink ploneimage',

      save_onsavecallback: () => {
        this.formsService.saveForm(this.item.formUniqueId);
        this.changeDetector.markForCheck();
      },

      setup : (editor: any) => {
        if(this.editorInstance) {
          this.editorInstance.remove();
        } else {
          this.getFormLayout();
        }

        editor.addMenuItem('PreviewButton', {
          text: 'Open form in new tab',
          context: 'view',
          onclick: () => {
            window.open(`${ this.item.url }/OpenForm`);
            return;
          }
        });

        this.editorInstance = editor;

        setTimeout(() => this.editorInstance.show());

        editor.on('change', (e: any) => {
          tiny.isDirty.emit(true);
        });

        editor.on('activate', (e: any) => {
          let $editorFrame = $(this.editorElement.nativeElement)
            .find('iframe[id*=mce_]');
        });

        editor.on('mousedown', (ev: MouseEvent) => {
          let $element = $(ev.target);

          this.zone.run(() => {
            let $element =  $(ev.target);
            let eventTarget = <any> ev.target;
            console.info('mousedown $element', $element);

            if (eventTarget.control ||
              (['radio', 'select-one'].indexOf(eventTarget.type) !== -1)) {
              $element = $element.parent();
            }
            else if (eventTarget.tagName === 'OPTION' ||
              eventTarget.nodeName === 'OPTION') {
              $element = $element.parent().parent();
            }
            
            let $parent = $element.parent();
            let $elementIsGroup = $element.hasClass('plominoGroupClass');
            let elementIsLabel = $element.hasClass('plominoLabelClass');
            let parentIsLabel = $parent.hasClass('plominoLabelClass');

            let $elementId = $element.data('plominoid');
            let $parentId = $parent.data('plominoid');

            if ($elementIsGroup) {
              let groupChildrenQuery = 
                '.plominoFieldClass, .plominoHidewhenClass, .plominoActionClass';
              let $groupChildren = $element.find(groupChildrenQuery);
              if ($groupChildren.length > 1) {
                this.fieldSelected.emit(null);
                return;
              }
              else {
                let $child = $groupChildren;
                let $childId = $child.data('plominoid');
                let $childType = this.extractClass($child.attr('class'));
                this.fieldSelected.emit({
                  id: $childId,
                  type: $childType,
                  parent: this.id
                });
                return;
              }
            }
            
            if (elementIsLabel || parentIsLabel) {
                this.fieldSelected.emit(null);
            } else {
              if ($elementId || $parentId) {
                let id = $elementId || $parentId;
                    
                let $elementType = $element.data('plominoid')
                  ? this.extractClass($element.attr('class')) : null;

                let $parentType = $parent.data('plominoid') 
                  ? this.extractClass($parent.attr('class')) : null;

                let type = $elementType || $parentType;

                this.fieldSelected.emit({ id: id, type: type, parent: this.id });
              } else {
                this.fieldSelected.emit(null);
              }
            }
          });
        });
      },
      content_css: [
        'theme/barceloneta-compiled.css', 'theme/++plone++static/plone-compiled.css'
      ],
      content_style: require('./tinymce.css'),
      menubar: "file edit insert view format table tools",
      height : "780",
      resize: false
    });

    // this.getFormLayout();

    this.draggingService
    .onPaletteCustomDragEvent()
    .subscribe((eventData: MouseEvent) => {
      this.dragData = this.draggingService.currentDraggingData 
        ? this.draggingService.currentDraggingData 
        : this.draggingService.previousDraggingData;
      
      this.contentManager.selectAndRemoveElementById(this.id, 'drag-autopreview');
      this.dropped({ mouseEvent: eventData });
      // this.autoSavedContent = this.contentManager.getContent(this.id);
      // this.contentManager.setContent(this.id, this.autoSavedContent);
    });

    // this.draggingService
    // .onPaletteCustomDragEventCancel()
    // .subscribe((eventData: MouseEvent) => {
    //   this.contentManager.selectAndRemoveElementById(this.id, 'drag-autopreview');
    //   if (this.autoSavedContent) {
    //     this.contentManager.setContent(this.id, this.autoSavedContent);
    //   }
    // });


    // this.draggingService
    // .onPaletteCustomDragMMOIEvent()
    // .subscribe((eventData: MouseEvent) => {
    //   // this.removeExampleWidget();
    //   // if (this.autoSavedContent) {
    //   //   tinymce.get(this.id).setContent(this.autoSavedContent);
    //   // }
    // });

    // this.draggingService
    // .onPaletteCustomDragMMIIEvent()
    // // .distinctUntilChanged((eventData: MouseEvent) => {
    // //   const rng = this.contentManager.getCaretRangeFromMouseEvent(this.id, eventData);
    // //   return rng.startOffset;
    // // })
    // .map((test: any) => 
    //   this.contentManager.getCaretRangeFromMouseEvent(this.id, test).startOffset)
    // .subscribe((test2: any) => console.log(test2));
    // .subscribe((eventData: MouseEvent) => {
    //   this.autoSavedContent = this.contentManager.getContent(this.id);
    //   this.dragData = this.draggingService.currentDraggingData 
    //     ? this.draggingService.currentDraggingData 
    //     : this.draggingService.previousDraggingData;
      
    //   // calculate the point

    //   // get x/y of the point

    //   // put the div into the point
    //   // const $mockWidgetGroup = $(
    //   //   `<div style="background: white; width: 200px; height: 25px;">demo</div>`
    //   // );

    //   this.contentManager.selectAndRemoveElementById(this.id, 'drag-autopreview');
    //   this.insertTemplatePreviewAtTheCursor(eventData);
    // });
  }

  getFormLayout() {
    this.elementService.getElementFormLayout(this.id)
    .subscribe((data) => {
      let newData = '';
      
      if (data && data.length) {
        this.contentManager.setContent(
          this.id, data, this.draggingService
        );
        const $inner = $(`iframe[id="${ this.id }_ifr"]`).contents().find('#tinymce');
        $inner.css('opacity', '0');
        this.autoSavedContent = data;
        const loadingElements = this.widgetService.getFormLayout(this.id);
        Promise.all(loadingElements).then(() => {
          $inner.css('opacity', '');
          this.contentManager.setContent(
            this.id, this.contentManager.getContent(this.id), this.draggingService
          );
        });
      }
      else {
        this.contentManager.setContent(
          this.id, newData, this.draggingService
        );
        this.autoSavedContent = newData;
      }

    }, (err) => {
      console.error(err);
    });
  }

  saveFormLayout(cb:any) {
    let tiny = this;
    let editor = tinymce.get(this.id) || tinymce.get(this.idChanges.oldId);

    if (editor !== null) {
      tiny.isLoading.emit(false);
      if (cb) cb();
      tiny.isDirty.emit(false);
      editor.setDirty(false);
      this.changeDetector.markForCheck();
      this.ngAfterViewInit();
    }
  }

  allowDrop() {
    return () => this.dragData.parent === this.id;
  }

  insertTemplatePreviewAtTheCursor(eventData: any) {
    console.log('FAAAKE');
    // const rng = this.contentManager.getCaretRangeFromMouseEvent(this.id, eventData);

    // if (rng) {
    //   this.contentManager.setRange(this.id, rng);
    //   this.contentManager.insertRawHTML(
    //     this.id, this.draggingService.currentDraggingTemplateCode
    //   );
    // }
  }

  dropped({ mouseEvent }: any) {
    if (this.dragData === null) {
      this.dragData = this.draggingService.currentDraggingData 
        ? this.draggingService.currentDraggingData 
        : this.draggingService.previousDraggingData;
    }

    let targetGroup = this.draggingService.target === null 
      ? null : this.draggingService.target.get(0);
    if (!targetGroup) {
      targetGroup = $('iframe:visible').contents()
        .find('*:not(.mce-visual-caret):last').get(0);
    }
    console.info('dropped', targetGroup);
    this.draggingService.target = null;

    if (this.dragData.resolved) {
      this.addElement(this.dragData);
      console.info('this.addElement', this.dragData);
    } else {
      this.resolveDragData(targetGroup, this.dragData, this.dragData.resolver);
      console.info('this.resolveDragData', this.dragData, this.dragData.resolver);
    }

    this.draggingService.currentDraggingData = null;
  }

  private updateField(updateData: any) {
    let ed = tinymce.get(this.id);
    let dataToUpdate: any[] = this.contentManager.selectDOM(
      this.id, `*[data-plominoid=${updateData.fieldData.id}]`
    );

    if (dataToUpdate.length) {
      Observable.from(dataToUpdate).map((element) => {
        /* WTF? */
        let normalizedType = $(element).attr('class')
          .split(' ')[0].slice(7, -5);
        let typeCapitalized = normalizedType[0].toUpperCase() +
          normalizedType.slice(1);

        return {
          base: this.id,
          type: normalizedType,
          newId: updateData.newId,
          oldTemplate: element
        };
      })
      .flatMap((itemToReplace: any) => {
        return this.updateFieldService.updateField(itemToReplace);
      })
      .subscribe((data: any) => {
        this.contentManager.selectContent(this.id, data.oldTemplate);
        this.contentManager.replaceContent(this.id, data.newTemplate);

        if (this.autoSaveTimer !== null) {
          clearTimeout(this.autoSaveTimer);
        }
        this.autoSaveTimer = setTimeout(() => {
          this.formsService.saveForm(this.item.formUniqueId, false);
          this.changeDetector.markForCheck();
        }, 500);
      });
    }
  }

  private addElement(element: { name: string, type: string, target?: any }) {
    let type: string;
    let elementClass: string;
    let elementEditionPage: string;
    let elementIdName: string;

    let elementId: string = element.name.split('/').pop();
    let baseUrl: string = element.name.slice(0, element.name.lastIndexOf('/'));
    
    switch(element.type) {
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

      case 'PlominoSubform':
        elementClass = 'plominoSubformClass';
        elementEditionPage = '@@tinymceplominoform/subform_form';
        elementIdName = 'subformid';
        type = 'subform';
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
        this.contentManager.insertContent(
          this.id, this.draggingService,
          '<hr class="plominoPagebreakClass"><br />', { target: element.target }
        );
        return;

      default: return;
    }

    this.insertElement(baseUrl, type, elementId);
  }

  private insertElement(
    baseUrl: string, type: string, value: string, option?: string) {
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
          `${widgetTemplate}`, { skip_undo: 1 }
        );
      });
    }
    else if (plominoClass !== undefined) {
      this.elementService.getWidget(baseUrl, type, value)
      .subscribe((response) => {
        console.info('response', response);
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
          this.id, this.draggingService, content, { skip_undo: 1 }
        );
  
        console.info('this.tabsService.selectField', {
          id: value,
          type: `Plomino${type}`,
          parent: this.id
        });

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
          this.id, this.draggingService, zone, { skip_undo: 1 }
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
