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
    TemplatesService
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
    @Output() fieldSelected: EventEmitter<any> = new EventEmitter();

    @ViewChild('theEditor') editorElement: ElementRef;

    data: string;
    isDragged: boolean = false;
    dragData: any;
    editorInstance: any;

    draggingSubscription: Subscription;
    insertionSubscription: Subscription;
    templatesSubscription: Subscription;

    constructor(private _elementService: ElementService,
                private fieldsService: FieldsService,
                private draggingService: DraggingService,
                private templatesService: TemplatesService,
                private changeDetector: ChangeDetectorRef,
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
            save_onsavecallback: () => { this.saveFormLayout() },
            setup : (editor: any) => {
                editor.on('change', (e: any) => {
                    tiny.isDirty.emit(true);
                });

                editor.on('activate', (e: any) => {
                    let $editorFrame = $(this.editorElement.nativeElement).find('iframe[id*=mce_]');
                    console.log($editorFrame);
                });
                
                editor.on('click', (ev: Event) => {
                    this.zone.run(() => {
                        let $element = $(ev.target);
                        let $parent = $element.parent();
    
                        let $elementId = $element.data('plominoid');
                        let $parentId = $parent.data('plominoid');
                        
                        if ($elementId || $parentId) {
                            let id = $elementId || $parentId;
                                
                            let $elementType = $element.hasClass('mceEditable') ? 
                                                this.extractClass($element.attr('class')) : 
                                                null;
    
                            let $parentType = $parent.hasClass('mceEditable') ? 
                                                this.extractClass($parent.attr('class')) : 
                                                null;
    
                            let type = $elementType || $parentType;
    
                            this.fieldSelected.emit({ id: id, type: type });
                        } else {
                            this.fieldSelected.emit(null);
                        }
                    });
                });
            },
            content_style: require('./tinymce.css'),
		    menubar: "file edit insert view format table tools",
            height : "780",
            resize: false
        });
        this.getFormLayout();
    }

    getFormLayout() {
        this._elementService.getElementFormLayout(this.id).subscribe(
            (data) => { tinymce.activeEditor.setContent(data ? data : ''); },
            err => console.error(err)
        );
    }

    saveFormLayout() {
        let tiny = this;
        if(tinymce.activeEditor !== null){
            this._elementService.patchElement(this.id, JSON.stringify({
                "form_layout": tinymce.activeEditor.getContent()
            })).subscribe(
                () => {
                    tiny.isDirty.emit(false);
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

            // Handle labels - TODO: replace this with example_wiget
            title = (value[0].toUpperCase() + value.slice(1, value.length)).split('-').join(" ");
            if (container == "span") {
                content = '<span class="plominoLabelClass mceNonEditable" data-plominoid="' + 
                            value + '">' + title + '</span><br />';
            } else {
                if (tinymce.DOM.hasClass(selection, "plominoLabelClass") && 
                    selection.tagName === "SPAN") {

                    content = '<div class="plominoLabelClass mceNonEditable" data-plominoid="' +
                                value + '"><div class="plominoLabelContent mceEditable">' + 
                                title + '</div></div><br />';
                }
                else if (tinymce.DOM.hasClass(selection.firstChild, "plominoLabelContent")) {
                    content = '<div class="plominoLabelClass mceNonEditable" data-plominoid="' + 
                                value + '">' + selection.innerHTML + '</div><br />';
                } else {
                    if (selection.textContent == "") {
                        content = '<div class="plominoLabelClass mceNonEditable" data-plominoid="' + 
                                    value + '"><div class="plominoLabelContent mceEditable">' + 
                                    title + '</div></div><br />';
                    } else {
                        content = '<div class="plominoLabelClass mceNonEditable" data-plominoid="' + 
                                    value + '"><div class="plominoLabelContent mceEditable">' + 
                                    ed.selection.getContent() + '</div></div><br />';
                    }
                }
            }

            ed.execCommand('mceInsertContent', false, content, {skip_undo : 1});

        } else if (plominoClass !== undefined) {

            this.http.get(`${baseUrl}/@@tinyform/example_widget?widget_type=${type}&id=${value}`)
                .map((response: Response) => response.json())
                .subscribe((response) => {
                    let responseAsElement = $(response);
                    selection = ed.selection.getNode();

                    if (responseAsElement.find("div,table,p").length) {
                        container = "div";
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
}
