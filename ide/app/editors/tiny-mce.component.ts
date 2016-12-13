import {Component, Input, Output, EventEmitter, NgZone} from '@angular/core';
import {ElementService} from '../services/element.service';
import {DND_DIRECTIVES} from 'ng2-dnd';

declare var tinymce: any;

@Component({
    selector: 'plomino-tiny-mce',
    template: `
    <form #theEditor><textarea class="tinymce-wrap"></textarea></form>
    <div *ngIf="isDragged" [style.height]="theEditor.offsetHeight+'px'" [style.margin-top]="'-'+theEditor.offsetHeight+'px'" class="drop-zone" dnd-droppable [allowDrop]="allowDrop()" (onDropSuccess)="dropped($event)"></div>
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
    providers: [ElementService]
})
export class TinyMCEComponent {

    @Input() id: string;
    @Input() isDragged: boolean = false;
    @Output() isDirty = new EventEmitter();
    data: string;

    constructor(private _elementService: ElementService, private zone: NgZone) {}

    ngOnInit() {
        let tiny = this;
        tinymce.init({
            selector:'.tinymce-wrap',
            plugins: ["code", "save", "link"],
            toolbar: "save | undo redo | formatselect | bold italic underline | alignleft aligncenter alignright alignjustify | bullist numlist | outdent indent | unlink link | image",
            save_onsavecallback: () => { this.saveFormLayout() },
            setup : (editor:any) => {
                editor.on('change', (e:any) => {
                    tiny.isDirty.emit(true);
                });
            },
            content_style: require('./tiny-mce-content.css'),
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
        return (dragData:any) => dragData.parent === this.id;
    }

    dropped(element: any) {
        tinymce.activeEditor.execCommand('mceInsertContent', false,
            '<p><span class="'+element.dragData.type.charAt(0).toLowerCase()+
            element.dragData.type.slice(1)+'Class">'+
            element.dragData.name.split('/').pop()+'</span></p>'
        );
    }

}
