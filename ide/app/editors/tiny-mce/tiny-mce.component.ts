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

import {
    ElementService,
    FieldsService,
    DraggingService,
    TemplatesService,
    WidgetService,
    TabsService,
    FormsService
} from '../../services';

import {DND_DIRECTIVES} from 'ng2-dnd/ng2-dnd';

import { Subscription } from 'rxjs/Subscription';

import 'jquery';

declare let $: any;
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
    providers: [ElementService],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class TinyMCEComponent implements AfterViewInit, OnInit, OnDestroy {

    @Input() id: string;
    @Output() isDirty: EventEmitter<any> = new EventEmitter();
    @Output() isLoading: EventEmitter<any> = new EventEmitter();
    @Output() fieldSelected: EventEmitter<any> = new EventEmitter();

    @ViewChild('theEditor') editorElement: ElementRef;

    data: string;
    isDragged: boolean = false;
    dragData: any;
    editorInstance: any;

    draggingSubscription: Subscription;
    insertionSubscription: Subscription;
    templatesSubscription: Subscription;

    constructor(private elementService: ElementService,
                private fieldsService: FieldsService,
                private draggingService: DraggingService,
                private templatesService: TemplatesService,
                private widgetService: WidgetService,
                private formsService: FormsService,
                private changeDetector: ChangeDetectorRef,
                private tabsService: TabsService,
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
            console.log(`Dragging data `, dragData);
            this.dragData = dragData;
            this.isDragged = !!dragData;
            this.changeDetector.markForCheck();
        });

        this.fieldsService.listenToUpdates()
        .subscribe((updateData) => {
            this.updateField(updateData);
        });

        this.formsService.formContentSave$.subscribe((cb) => {
            this.isLoading.emit(true);
            this.changeDetector.detectChanges();
            tinymce.activeEditor.buttons.save.onclick();
            this.saveFormLayout(cb);
        } );
        
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
        tinymce.init({
            selector:'.tinymce-wrap',
            plugins: ['code', 'save', 'link', 'noneditable'],
            toolbar: 'save | undo redo | formatselect | bold italic underline | alignleft aligncenter alignright alignjustify | bullist numlist | outdent indent | unlink link | image',
            save_onsavecallback: () => { this.formsService.saveForm(); this.isLoading.emit(true);  },
            setup : (editor: any) => {
                editor.on('change', (e: any) => {
                    tiny.isDirty.emit(true);
                });

                editor.on('activate', (e: any) => {
                    let $editorFrame = $(this.editorElement.nativeElement).find('iframe[id*=mce_]');
                    console.log($editorFrame);
                });

                editor.on('mousedown', (ev: MouseEvent) => {
                    let $element = $(ev.target);
                    this.zone.run(() => {
                        let $element = $(ev.target);
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
                
                // editor.on('click', (ev: Event) => {
                //     console.log(`Clicked on element `); 
                // });
            },
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
                    this.widgetService.getFormLayout(this.id, data)
                        .subscribe((formLayout: string) => {
                            tinymce.get(this.id).setContent(formLayout); 
                        });
                } else {
                    tinymce.get(this.id).setContent(newData);
                }
            }, (err) => { 
                console.error(err);
            });
    }

    saveFormLayout(cb:any) {
        let tiny = this;
        if(tinymce.activeEditor !== null){
            this.elementService.patchElement(this.id, JSON.stringify({
                "form_layout": tinymce.activeEditor.getContent()
            })).subscribe(
                () => {
                    tiny.isLoading.emit(false);
                    // let the app know that saving finished
                    if(cb) cb();
                    tiny.isDirty.emit(false);
                    tinymce.activeEditor.setDirty(false);
                    this.changeDetector.markForCheck();
                },
                err => console.error(err)
            );
        }
    }

    allowDrop() {
        return () => this.dragData.parent === this.id;
    }

    dropped({ mouseEvent }: any) {
        let offset = $(this.editorElement.nativeElement)
                        .find(`iframe[id*='${this.id}']`)
                        .offset();
        let editor = tinymce.get(this.id);
        let x = Math.round(mouseEvent.clientX - offset.left);
        let y = Math.round(mouseEvent.clientY - offset.top);
        let rng = this.getCaretFromEvent(x, y, editor);

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
        } else {
            this.resolveDragData(this.dragData, this.dragData.resolver);
        }
    }

    private updateField(updateData: any) {
        let ed = tinymce.get(this.id);
        console.log(updateData.fieldData.id);
        let selection = ed.selection.select(ed.dom.select(`*[data-plominoid=${updateData.fieldData.id}]`)[0]);

        if (selection) {
            let normalizedFieldType = updateData.fieldData.type.slice(7).toLowerCase();
            let typeCapitalized = normalizedFieldType[0].toUpperCase() + normalizedFieldType.slice(1);

            this.elementService.getWidget(this.id, normalizedFieldType, updateData.newId)
            .subscribe((response: any) => {
                let resultingElement = this.wrapElement(`plomino${typeCapitalized}`, updateData.newId, response);
                ed.execCommand('mceReplaceContent', false, resultingElement);
            });
        }
    }

    private addElement(element: { name: string, type: string}) {
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
    }

    private insertElement(baseUrl: string, type: string, value: string, option?: string) {

		let ed: any = tinymce.get(this.id);
        let selection: any = ed.selection.getNode();
        let title: string;
        let plominoClass: string;
        let content: string;

        for (let e = 0; e < tinymce.editors.length; e += 1) {
            console.log(tinymce.editors[e]);
        }

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
                    ed.execCommand('mceInsertContent', false, `${widgetTemplate}<br />`, {skip_undo : 1});
                });
            // Handle labels - TODO: replace this with example_wiget
            // title = (value[0].toUpperCase() + value.slice(1, value.length)).split('-').join(" ");
            // if (container == "span") {
            //     content = '<span class="plominoLabelClass mceNonEditable" data-plominoid="' + 
            //                 value + '">' + title + '</span><br />';
            // } else {
            //     if (tinymce.DOM.hasClass(selection, "plominoLabelClass") && 
            //         selection.tagName === "SPAN") {

            //         content = '<div class="plominoLabelClass mceNonEditable" data-plominoid="' +
            //                     value + '"><div class="plominoLabelContent">' + 
            //                     title + '</div></div><br />';
            //     }
            //     else if (tinymce.DOM.hasClass(selection.firstChild, "plominoLabelContent")) {
            //         content = '<div class="plominoLabelClass mceNonEditable" data-plominoid="' + 
            //                     value + '">' + selection.innerHTML + '</div><br />';
            //     } else {
            //         if (selection.textContent == "") {
            //             content = '<div class="plominoLabelClass mceNonEditable" data-plominoid="' + 
            //                         value + '"><div class="plominoLabelContent">' + 
            //                         title + '</div></div><br />';
            //         } else {
            //             content = '<div class="plominoLabelClass mceNonEditable" data-plominoid="' + 
            //                         value + '"><div class="plominoLabelContent">' + 
            //                         ed.selection.getContent() + '</div></div><br />';
            //         }
            //     }
            // }

            // console.log(`You want to insert label! `, baseUrl, type, value);

            // ed.execCommand('mceInsertContent', false, content, {skip_undo : 1});

        } else if (plominoClass !== undefined) {

            this.elementService.getWidget(baseUrl, type, value)
                .subscribe((response) => {
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
                    } else {

                        ed.execCommand('mceInsertContent', false, content, {skip_undo : 1});
                    }

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
			}

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
    }
    
    private resolveDragData(data: any, resolver: any): void {
        resolver(data);
    }

    private extractClass(classString: string): string {
        let type = classString.split(' ')[0].slice(0, -5);
        return type.indexOf('plomino') > -1 ? type : null;
    }

    private getCaretFromEvent(clientX: any, clientY: any, editor: any) {
        return tinymce.dom.RangeUtils.getCaretRangeFromPoint(clientX, clientY, editor.getDoc());
    }

    private wrapElement(elType: string, id: string, content: string) {
        switch(elType) {
            case 'plominoField':
            case 'plominoAction':
                return this.wrapFieldOrAction(elType, id, content);
            case 'plominoHidewhen':
                return this.wrapHidewhen(elType, id, content);
            default:
        }
    }

    private wrapFieldOrAction(elType: string, id: string, contentString: string) {  
        let $response = $(contentString);
        let $class = `${elType}Class`;

        let container = 'span';
        let content = '';
        let $newId: any;

        if ($response.find("div,table,p").length) {
            container = "div";
        }
        
        if (contentString != undefined) {
            content = `<${container} class="${$class} mceNonEditable" 
                                    data-mce-resize="false" 
                                    data-plominoid="${id}">
                ${contentString}    
            </${container}><br />`;
        } else {
            content = `<span class="${$class}">${id}</span><br />`;
        }

        return content;
    }

    private wrapHidewhen(elType: string, id: string, contentString: string) {
        let $element = $(contentString); 
        let $class = $element.attr('class');
        let $position = $element.text().split(':')[0];
        let $id = $element.text().split(':')[1];
      
        let container = 'div';
        let content = `<${container} class="${$class} mceNonEditable" 
                                  data-mce-resize="false"
                                  data-plomino-position="${$position}" 
                                  data-plominoid="${$id}">
                        &nbsp;
                      </${container}>${ $position === 'start' ? '' : '<br />' }`;
    
        return content;
    }
}
