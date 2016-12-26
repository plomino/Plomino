import {
    Component, 
    Input, 
    Output, 
    EventEmitter,
    ViewChild,
    ElementRef,
    AfterViewInit, 
    ChangeDetectorRef,
    ChangeDetectionStrategy
} from '@angular/core';

import { 
    Http,
    Response
} from '@angular/http';

import {
    ElementService,
    FieldsService,
    DraggingService
} from '../../services';

import {DND_DIRECTIVES} from 'ng2-dnd/ng2-dnd';

import 'jquery';

declare let $: any;
declare var tinymce: any;

@Component({
    selector: 'plomino-tiny-mce',
    template: `
    <form #theEditor><textarea class="tinymce-wrap"></textarea></form>
    <div *ngIf="isDragged" 
        [style.height]="theEditor.offsetHeight+'px'" 
        [style.margin-top]="'-'+theEditor.offsetHeight+'px'" 
        class="drop-zone" 
        dnd-droppable 
        [allowDrop]="allowDrop()" 
        (onDropSuccess)="dropped()">
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
export class TinyMCEComponent implements AfterViewInit {

    @Input() id: string;
    @Output() isDirty: EventEmitter<any> = new EventEmitter();
    @Output() fieldSelected: EventEmitter<any> = new EventEmitter();

    @ViewChild('theEditor') editorElement: ElementRef;

    data: string;
    isDragged: boolean = false;
    dragData: any;

    constructor(private _elementService: ElementService,
                private fieldsService: FieldsService,
                private draggingService: DraggingService,
                private changeDetector: ChangeDetectorRef,
                private http: Http) {
        this.fieldsService.getInsertion()
            .subscribe((insertion) => {
                let dataToInsert = Object.assign({}, insertion, { 
                    type: insertion['@type']
                });
                console.log(dataToInsert);
                this.addElement(dataToInsert);
                this.changeDetector.markForCheck();
            });
        
        this.draggingService.getDragging()
            .subscribe((dragData: any) => {
                console.log(`Drag status `, dragData);
                this.dragData = dragData;
                this.isDragged = !!dragData;
                this.changeDetector.markForCheck();
            });
    }

    ngOnInit() {
        let tiny = this;
        tinymce.init({
            selector:'.tinymce-wrap',
            plugins: ["code", "save", "link"],
            toolbar: "save | undo redo | formatselect | bold italic underline | alignleft aligncenter alignright alignjustify | bullist numlist | outdent indent | unlink link | image",
            save_onsavecallback: () => { this.saveFormLayout() },
            setup : (editor: any) => {
                editor.on('change', (e: any) => {
                    tiny.isDirty.emit(true);
                });
                
                editor.on('click', (ev: Event) => {
                    let $element = $(ev.target);
                    let $elementId = $element.data('plominoid');
                    let $parentId = $element.parent().data('plominoid');
                    if ($elementId || $parentId) {
                        let id = $elementId || $parentId;
                        this.fieldSelected.emit(id);
                    } else {
                        this.fieldSelected.emit(null);
                    }
                });
            },
            content_style: require('./tiny-mce-content.css'),
		    menubar: "file edit insert view format table tools",
            height : "780",
            resize: false
        });
        this.getFormLayout();
    }

    ngAfterViewInit(): void {
        // let $editor: any = $(this.editorElement.nativeElement).find('iframe');
        // let $editorWorkspace = $editor.contentWindow ? $editor.contentWindow : $editor.contentDocument.defaultView;
        // console.log($editorWorkspace);
        // $editorWorkspace.on('click', (ev: Event) => {
        //     console.log(ev);
        // });
        // editor.on('click', (ev: Event) => {
        //     console.log(`clicked `, ev);
        //     let $target = $(ev.target);
        //     let $targetId = $target.data('plominoid');
        //     let $targetParentId = $target.parent().data('plominoid');
        //     if ($targetId || $targetParentId) {
        //         let id = $target.data('plominoid') || $targetParentId;
        //         this.fieldSelected.emit(id);
        //     }
        // });
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

    dropped() {
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
        let editor: any = tinymce.activeEditor;
        
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

		let ed: any = tinymce.activeEditor;
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

	};
    
    private resolveDragData(data: any, resolver: any): void {
        resolver(data);
    }
}
