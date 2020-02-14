import { Component, Input, EventEmitter, Output } from '@angular/core';

export const DIRECTION_RIGHT = 'right';
export const DIRECTION_LEFT = 'left';
export const DIRECTION_UP = 'up';
export const DIRECTION_DOWN = 'down';

declare let tinymce: any;

@Component({
    selector: 'plomino-resize-divider',
    styles: [require('./resize-divider.css')],
    template: `
    <div class="resizeable-divider"
        [class.resizeable-divider--row]="!columnResize"
        [class.resizeable-divider--column]="columnResize"
        (mousedown)="startDragging($event)">
        <img [src]="getSVG()" class="resizeable-divider__control">
    </div>
    `
})
export class ResizeDividerComponent {
    @Input() columnResize = false;
    @Input() listen: string[] = 
        [DIRECTION_RIGHT, DIRECTION_LEFT, DIRECTION_UP, DIRECTION_DOWN];
    @Output() move: EventEmitter<any> = new EventEmitter();
    
    private currentPos: { x: number; y: number } = null;
    constructor() { }

    private getSVG() {
        return this.columnResize 
        ? 'images/drag-vertical.svg' : 'images/drag-horizontal.svg';
    }

    private startDragging(e: MouseEvent) {
        this.currentPos = this.getMousePos(e);

        $(document)
        .on('mousemove.rsz', this.drag.bind(this))
        .on('mouseup.rsz', this.stopDragging.bind(this));

        $('iframe').contents()
        .on('mousemove.rsz', this.drag.bind(this))
        .on('mouseup.rsz', this.stopDragging.bind(this));
    }

    private drag(e: MouseEvent) {
        const pos = this.getMousePos(e);
        
        if (this.currentPos === null) {
            this.currentPos = this.getMousePos(e);
        }

        if (pos === null) {
            this.stopDragging(e);
            return;
        }

        const directions: string[] = [];
        const difference: {x: number; y: number} = { x: 0, y: 0 };

        const needed = (direction: string) => {
            return this.listen.indexOf(direction) !== -1;
        };

        if (pos.x < this.currentPos.x && needed(DIRECTION_LEFT)) {
            directions.push(DIRECTION_LEFT);
            difference.x = this.currentPos.x - pos.x;
        }
        else if (pos.x > this.currentPos.x && needed(DIRECTION_RIGHT)) {
            directions.push(DIRECTION_RIGHT);
            difference.x = pos.x - this.currentPos.x;
        }

        if (pos.y < this.currentPos.y && needed(DIRECTION_UP)) {
            directions.push(DIRECTION_UP);
            difference.y= this.currentPos.y - pos.y;
        }
        else if (pos.y > this.currentPos.y && needed(DIRECTION_DOWN)) {
            directions.push(DIRECTION_DOWN);
            difference.y = pos.y - this.currentPos.y;
        }

        if (difference.x > 5) {
            difference.x = 5;
        }

        // if (difference.y > 5) {
        //     difference.y = 5;
        // }

        this.currentPos = pos;
        this.move.emit({ directions, difference });
    }

    private stopDragging(e: MouseEvent) {
        e.stopPropagation();
        e.preventDefault();
        $(document).off('.rsz');
        $('iframe').contents().off('.rsz');
        this.currentPos = null;
    }

    private getMousePos (e: MouseEvent): { x: number; y: number } {
        return typeof e.clientX !== "number" ? null : { x: e.clientX, y: e.clientY };
    }
}