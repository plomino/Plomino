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

import 'jquery';
declare var tinymce: any;

@Component({
    selector: 'plomino-tiny-mce',
    template: `
    <form #theEditor 
        class="tiny-editor">
        <textarea class="tinymce-wrap" 
                [id]="id">
        </textarea>
    </form>
    <div *ngIf="isDragged" 
        dnd-droppable 
        class="drop-zone"
        [style.height]="theEditor.offsetHeight+'px'" 
        [style.margin-top]="'-'+theEditor.offsetHeight+'px'" 
        [allowDrop]="allowDrop()"  
        (onDragEnter)="_test($event)"
        (onDropSuccess)="dropped($event)">
    </div>
    `,
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
export class TinyMCEComponent implements AfterViewInit, OnInit, OnDestroy {

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

    constructor(private elementService: ElementService,
                private fieldsService: FieldsService,
                private draggingService: DraggingService,
                private templatesService: TemplatesService,
                private widgetService: WidgetService,
                private formsService: FormsService,
                private changeDetector: ChangeDetectorRef,
                private tabsService: TabsService,
                private updateFieldService: UpdateFieldService,
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
                this.insertGroup(insertion.group);
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
        .subscribe((updateData) => {
            console.info('this.updateField(updateData)', updateData);
            this.updateField(updateData);
        });

        this.formsService.formIdChanged$.subscribe((data) => {
            this.idChanges = Object.assign({}, data);
        });

        this.formsService.formContentSave$.subscribe((data) => {
            console.info('this.formsService.formContentSave$.subscribe', data);

            this.changeDetector.detectChanges();

            if(data.formUniqueId !== this.item.formUniqueId)
                return;

            this.isLoading.emit(true);

            let editor = tinymce.get(this.id) || tinymce.get(this.idChanges && this.idChanges.oldId);

            editor.buttons.save.onclick();

            this.saveFormLayout(data.cb);
        } );

        this.formsService.getFormContentBeforeSave$.subscribe((data:{id:any}) => {
            console.info('getFormContentBeforeSave$', data);
            console.info('data.id !== this.item.formUniqueId',
                data.id !== this.item.formUniqueId);
            
            console.info('this.item.formUniqueId', this.item.formUniqueId);
            console.info('data.id', data.id);
            
            if (typeof this.item.formUniqueId === 'undefined') {
                this.item.formUniqueId = data.id;
            }
            
            if (data.id !== this.item.formUniqueId)
                return;

            this.formsService.onFormContentBeforeSave({
                id: data.id,
                content: tinymce.get(this.id).getContent()
            });
        });

    }

    ngOnInit() { }

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
            force_br_newlines : true,
            force_p_newlines : false,
            forced_root_block: '',
            linkModal: null,
            addLinkClicked: function () {
                tiny.zone.runOutsideAngular(() => {
                    var self = <any>this;
                    if (self.linkModal === null) {
                        var $el = $('<div/>').insertAfter(self.$el);
                        var linkTypes = ['internal', 'upload', 'external', 'email', 'anchor'];
                        if(!self.options.upload){
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
            // addImageClicked: function() {
            //   var self = this;
            //   if (self.imageModal === null) {
            //     var linkTypes = ['image', 'uploadImage', 'externalImage'];
            //     if(!self.options.upload){
            //       linkTypes.splice(1, 1);
            //     }
            //     var options = $.extend(true, {}, self.options, {
            //       tinypattern: self,
            //       linkTypes: linkTypes,
            //       initialLinkType: 'image',
            //       text: {
            //         insertHeading: _t('Insert Image')
            //       },
            //       relatedItems: {
            //         baseCriteria: [{
            //           i: 'portal_type',
            //           o: 'plone.app.querystring.operation.list.contains',
            //           v: self.options.imageTypes.concat(self.options.folderTypes)
            //         }],
            //         selectableTypes: self.options.imageTypes,
            //         resultTemplate: ResultTemplate,
            //         selectionTemplate: SelectionTemplate
            //       }
            //     });
            //     var $el = $('<div/>').insertAfter(self.$el);
            //     self.imageModal = new LinkModal($el, options);
            //     self.imageModal.show();
            //   } else {
            //     self.imageModal.reinitialize();
            //     self.imageModal.show();
            //   }
            // },
            // generateUrl: function(data) {
            //   var self = this;
            //   var part = data[self.options.linkAttribute];
            //   return self.options.prependToUrl + part + self.options.appendToUrl;
            // },
            // generateImageUrl: function(data, scale_name) {
            //   var self = this;
            //   var url = self.generateUrl(data);
            //   if (scale_name !== ''){
            //     var part = scale_name;
            //     for(var i=0; i<self.options.scales.length; i=i+1){
            //       if(self.options.scales[i].name === scale_name){
            //         part = self.options.scales[i].part;
            //       }
            //     }
            //     url = (url + self.options.prependToScalePart + part +
            //            self.options.appendToScalePart);
            //   }else{
            //     url = url + self.options.appendToOriginalScalePart;
            //   }
            //   return url;
            // },
            // stripGeneratedUrl: function(url) {
            //   // to get original attribute back
            //   var self = this;
            //   url = url.split(self.options.prependToScalePart, 2)[0];
            //   if (self.options.prependToUrl) {
            //     var parts = url.split(self.options.prependToUrl, 2);
            //     if (parts.length === 2) {
            //       url = parts[1];
            //     }
            //   }
            //   if (self.options.appendToUrl) {
            //     url = url.split(self.options.appendToUrl)[0];
            //   }
            //   return url;
            // },
            // getScaleFromUrl: function(url) {
            //   var self = this;
            //   var split = url.split(self.options.prependToScalePart);
            //   if (split.length !== 2) {
            //     // not valid scale, screw it
            //     return null;
            //   }
            //   if (self.options.appendToScalePart) {
            //     url = split[1].split(self.options.appendToScalePart)[0];
            //   } else {
            //     url = split[1];
            //   }
            //   if (url.indexOf('/image_') !== -1) {
            //     url = url.split('/image_')[1];
            //   }
            //   return url;
            // },
            linkAttribute: 'path',
            prependToScalePart: '/imagescale/', // some value here is required to be able to parse scales back
            appendToScalePart: '',
            appendToOriginalScalePart: '',
            defaultScale: 'large',
            scales: 'Listing (16x16):listing,Icon (32x32):icon,Tile (64x64):tile,' +
                    'Thumb (128x128):thumb,Mini (200x200):mini,Preview (400x400):preview,' +
                    'Large (768x768):large',
            targetList: [
            {text: 'Open in this window / frame', value: ''},
            {text: 'Open in new window', value: '_blank'},
            {text: 'Open in parent window / frame', value: '_parent'},
            {text: 'Open in top frame (replaces all frames)', value: '_top'}
            ],
            imageTypes: ['Image'],
            folderTypes: ['Folder', 'Plone Site'],
            // plugins: ['advlist', 'autolink', 'lists', 'charmap', 'print', 'preview', 'anchor', 'searchreplace',
            //       'visualblocks', 'code', 'fullscreen', 'insertdatetime', 'media', 'table', 'contextmenu',
            //       'paste', 'plonelink', 'ploneimage'],
            plugins: ['code', 'save', 'link', 'noneditable', 'preview', 'ploneimage', 'plonelink'],
            toolbar: 'save | undo redo | formatselect | bold italic underline' +
            ' | alignleft aligncenter alignright alignjustify | ' +
            'bullist numlist | outdent indent | ' +
            'plonelink unlink ploneimage',
            // toolbar: 'undo redo | styleselect | bold italic | ' +
            //      'alignleft aligncenter alignright alignjustify | ' +
            //      'bullist numlist outdent indent | ' +
            //      'unlink plonelink ploneimage',
            save_onsavecallback: () => { this.formsService.saveForm(this.item.formUniqueId); this.changeDetector.markForCheck(); },
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

                setTimeout(() => this.editorInstance.show()); // use timeout to push in new queue

                editor.on('change', (e: any) => {
                    tiny.isDirty.emit(true);
                });

                editor.on('activate', (e: any) => {
                    let $editorFrame = $(this.editorElement.nativeElement).find('iframe[id*=mce_]');
                });

                // editor.on('mouseover', (ev: MouseEvent) => {
                //     let $element = $(ev.target);
                //     this.zone.run(() => {
                //         console.info('mouseover $element', $element);
                //     });
                // });

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
                        console.log($element);
                        let $parent = $element.parent();
                        let $elementIsGroup = $element.hasClass('plominoGroupClass');
                        let elementIsLabel = $element.hasClass('plominoLabelClass');
                        let parentIsLabel = $parent.hasClass('plominoLabelClass');

                        let $elementId = $element.data('plominoid');
                        let $parentId = $parent.data('plominoid');

                        if ($elementIsGroup) {
                            let groupChildrenQuery = '.plominoFieldClass, .plominoHidewhenClass, .plominoActionClass';
                            let $groupChildren = $element.find(groupChildrenQuery);
                            if ($groupChildren.length > 1) {
                                this.fieldSelected.emit(null);
                                return;
                            } else {
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
                                    
                                let $elementType = $element.data('plominoid') ? 
                                                    this.extractClass($element.attr('class')) : 
                                                    null;
        
                                let $parentType = $parent.data('plominoid') ? 
                                                    this.extractClass($parent.attr('class')) : 
                                                    null;
        
                                let type = $elementType || $parentType;
        
                                this.fieldSelected.emit({ id: id, type: type, parent: this.id });
                            } else {
                                this.fieldSelected.emit(null);
                            }
                        }

                    });
                });
            },
            content_css: ['theme/barceloneta-compiled.css', 'theme/++plone++static/plone-compiled.css'],
            content_style: require('./tinymce.css'),
		    menubar: "file edit insert view format table tools",
            height : "780",
            resize: false
        });
        this.getFormLayout();
    }

    getFormLayout() {
        this.elementService.getElementFormLayout(this.id)
            .subscribe((data) => {
                let newData = '';
                if (data && data.length) {
                    console.info('this.widgetService.getFormLayout', this.id, data);
                    this.widgetService.getFormLayout(this.id, data)
                        .subscribe((formLayout: string) => {
                            console.info('tinymce setContent code (0)');
                            tinymce.get(this.id).setContent(formLayout);
                            // console.log(formLayout);
                        });
                } else {
                    console.info('tinymce setContent code (1)');
                    tinymce.get(this.id).setContent(newData);
                }
            }, (err) => {
                console.error(err);
            });
    }

    saveFormLayout(cb:any) {
        let tiny = this;
        let editor = tinymce.get(this.id) || tinymce.get(this.idChanges.oldId);
        if(editor !== null){
            // this.elementService.patchElement(this.id, JSON.stringify({
            //     "form_layout": editor.getContent()
            // })).subscribe(
            //     () => {
            tiny.isLoading.emit(false);
            // let the app know that saving finished
            if (cb) cb();
            tiny.isDirty.emit(false);
            editor.setDirty(false);
            this.changeDetector.markForCheck();
            this.ngAfterViewInit();
            // },
            // err => console.error(err)
            // );
        }
    }

    allowDrop() {
        return () => this.dragData.parent === this.id;
    }

    _test(eventData: any) {
        let offset = $(this.editorElement.nativeElement)
                        .find(`iframe[id*='${this.id}']`)
                        .offset();
        let editor = tinymce.get(this.id);
        let x = Math.round(eventData.mouseEvent.clientX - offset.left);
        let y = Math.round(eventData.mouseEvent.clientY - offset.top);
        let rng = this.getCaretFromEvent(x, y, editor);
        editor.selection.setRng(rng);
        // if (this.dragData.resolved) {
        //     // this.addElement(this.dragData);
        //     // console.info('this.addElement', this.dragData);
        // } else {
        //     this.resolveDragData(this.dragData, this.dragData.resolver);
        //     console.info('this.resolveDragData', this.dragData, this.dragData.resolver);
        // }
        console.info(this.dragData, eventData.mouseEvent);
    }

    dropped({ mouseEvent }: any) {
        let offset = $(this.editorElement.nativeElement)
                        .find(`iframe[id*='${this.id}']`)
                        .offset();
        let editor = tinymce.get(this.id);
        let x = Math.round(mouseEvent.clientX - offset.left);
        let y = Math.round(mouseEvent.clientY - offset.top);
        let rng = this.getCaretFromEvent(x, y, editor);
        console.info('this.getCaretFromEvent', rng);

        // if (startContainer.nodeName !== 'body') {
        //     let newRng = tinymce.DOM.createRng();
        //     let newStartOffset = startOffset !== endOffset ? endOffset : startOffset;
        //     let newEndOffset = endOffset;
        //     newRng.setStart(startContainer.parentNode, newStartOffset);
        //     newRng.setEnd(startContainer.parentNode, newEndOffset);
        //     editor.selection.setRng(newRng);
        // } else {
        //     editor.selection.setRng(rng);
        // }
        
        editor.selection.setRng(rng);
        if (this.dragData.resolved) {
            this.addElement(this.dragData);
            console.info('this.addElement', this.dragData);
        } else {
            this.resolveDragData(this.dragData, this.dragData.resolver);
            console.info('this.resolveDragData', this.dragData, this.dragData.resolver);
        }
    }

    private updateField(updateData: any) {
        let ed = tinymce.get(this.id);
        let dataToUpdate: any[] = ed.dom.select(`*[data-plominoid=${updateData.fieldData.id}]`);

        console.info('dataToUpdate selector', updateData.fieldData.id);
        console.info('dataToUpdate', dataToUpdate);

        if (dataToUpdate.length) {
            console.info('dataToUpdate presents');
            Observable.from(dataToUpdate)
                .map((element) => {
                    let normalizedType = $(element).attr('class').split(' ')[0].slice(7, -5);
                    let typeCapitalized = normalizedType[0].toUpperCase() + normalizedType.slice(1);

                    return {
                        base: this.id,
                        type: normalizedType,
                        newId: updateData.newId,
                        oldTemplate: element
                    };
                })
                .flatMap((itemToReplace: any) => {
                    console.info('itemToReplace', itemToReplace);
                    console.info('this.updateFieldService.updateField(itemToReplace)');
                    return this.updateFieldService.updateField(itemToReplace);
                })
                .subscribe((data: any) => {
                    console.info('updateField => subscribe => data', data);
                    
                    try {
                        let selection = ed.selection.select(data.oldTemplate);
                        console.info('selection', selection);
                        console.info('mceReplaceContent', data.newTemplate);
                        ed.execCommand('mceReplaceContent', false, data.newTemplate);
                    }
                    catch (e) {
                        console.log('content cannot be replaced :)', data.newTemplate);
                    }

                    if (this.autoSaveTimer !== null) {
                        clearTimeout(this.autoSaveTimer);
                    }
                    this.autoSaveTimer = setTimeout(() => {
                        console.info('saving your form...');
                        this.formsService.saveForm(this.item.formUniqueId, false);
                        this.changeDetector.markForCheck();
                    }, 500);
                });

        }
    }

    private addElement(element: { name: string, type: string}) {

        // TODO: Move this method to service

        let type: string;
        let elementClass: string;
        let elementEditionPage: string;
        let elementIdName: string;

        let elementId: string = element.name.split('/').pop();
        let baseUrl: string = element.name.slice(0, element.name.lastIndexOf('/'));
        let editor: any = tinymce.get(this.id);
        
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
                editor.execCommand('mceInsertContent', false, '<hr class="plominoPagebreakClass"><br />');
                return;
            default: 
                return;
        }

        this.insertElement(baseUrl, type, elementId);
        console.info('this.insertElement', baseUrl, type, elementId);
    }

    private insertElement(baseUrl: string, type: string, value: string, option?: string) {

        // TODO: Move this method to service

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

        console.info('plominoClass', plominoClass);
        console.info('type', type);
        console.info('container', container);
        
        if (type == 'label') {
            this.elementService.getWidget(baseUrl, type, value)
                .subscribe((widgetTemplate: any) => {
                    ed.execCommand('mceInsertContent', false, `${widgetTemplate}<br />`, {skip_undo : 1});
                    console.info('mceInsertContent (0)', `${widgetTemplate}<br />`);
                });
        } else if (plominoClass !== undefined) {

            console.info('this.elementService.getWidget(baseUrl, type, value)', baseUrl, type, value);
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
                        content = '<'+container+' class="'+plominoClass + 
                            ' mceNonEditable" data-mce-resize="false" data-plominoid="' +
                            value + '">' + response + '</'+container+'><br />';
                    }
                    
                    else {
                        content = '<span class="' + plominoClass + '">' + value + '</span><br />';
                    }

                    if (tinymce.DOM.hasClass(selection, 'plominoActionClass') || 
                        tinymce.DOM.hasClass(selection, 'plominoFieldClass') || 
                        tinymce.DOM.hasClass(selection, 'plominoLabelClass') || 
                        tinymce.DOM.hasClass(selection, 'plominoSubformClass')) {

                        ed.execCommand('mceInsertContent', false, content, {skip_undo : 1});
                        console.info('mceInsertContent (1)', content);
                    } else {

                        ed.execCommand('mceInsertContent', false, content, {skip_undo : 1});
                        console.info('mceInsertContent (2)', content);
                    }

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

		} else if (type == "hidewhen" || type == 'cache') {
			
            // Insert or replace the selection

            let cssclass = 'plomino' + type.charAt(0).toUpperCase() + type.slice(1) + 'Class';

			// If the node is a <span class="plominoFieldClass"/>, select all its content
			if (tinymce.DOM.hasClass(selection, cssclass)) {
				
                // get the old hide-when id
                let oldId = selection.getAttribute('data-plominoid');
                let pos = selection.getAttribute('data-plomino-position')

				// get a list of hide-when opening and closing spans
				let hidewhens = ed.dom.select('span.'+cssclass);

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
						if (hidewhens[i] && hidewhens[i].getAttribute('data-plominoid') == oldId &&
                            hidewhens[i].getAttribute('data-plomino-position') == 'end') {
							hidewhens[i].setAttribute('data-plominoid', value);
							break;
						}
					}
				} else {
				    // change the corresponding start by going backwards
					selection.setAttribute('data-plominoid', value);

					for (; i >= 0; i--) {
						if (hidewhens[i] && hidewhens[i].getAttribute('data-plominoid') == oldId &&
                            hidewhens[i].getAttribute('data-plomino-position') == 'start') {
							hidewhens[i].setAttribute('data-plominoid', value);
							break;
						}
					}
				}
			} else {
				// String to add in the editor
				let zone = '<br /> <span class="' + cssclass + ' mceNonEditable" data-plominoid="' + 
                            value + '" data-plomino-position="start">&nbsp;</span>' +
                            ed.selection.getContent() +
                            '<span class="' + cssclass + ' mceNonEditable" data-plominoid="' + 
                            value + '" data-plomino-position="end">&nbsp;</span><br />';
				
                ed.execCommand('mceInsertContent', false, zone, {skip_undo : 1});
                console.info('mceInsertContent (3) zone', zone);
			}

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
		}

	}

    private insertGroup(group: string) {
        let editor = tinymce.get(this.id);
        editor.execCommand('mceInsertContent', false, group, { skip_undo : 1 });
        console.info('insertGroup -> mceInsertContent (4) group', group);
    }
    
    private resolveDragData(data: any, resolver: any): void {
        resolver(data);
    }

    private extractClass(classString: string): string {
        if(!classString) return null;
        let type = classString.split(' ')[0].slice(0, -5);
        return type.indexOf('plomino') > -1 ? type : null;
    }

    private getCaretFromEvent(clientX: any, clientY: any, editor: any) {
        return tinymce.dom.RangeUtils.getCaretRangeFromPoint(clientX, clientY, editor.getDoc());
    }
}
