import { Component, Input, EventEmitter, Output } from "@angular/core";

export const HORIZONTAL = "HORIZONTAL";
export const VERTICAL = "VERTICAL";

declare let tinymce: any;

@Component({
    selector: "plomino-resize-divider",
    styles: [require("./resize-divider.css")],
    template: `
        <div
            class="resizeable-divider"
            [class.resizeable-divider--row]="!columnResize"
            [class.resizeable-divider--column]="columnResize"
            (mousedown)="startDragging($event)"
        >
            <img [src]="getSVG()" class="resizeable-divider__control" />
        </div>
    `,
})
export class ResizeDividerComponent {
    @Input() columnResize = false;
    @Input() listen: string;
    @Output() move: EventEmitter<any> = new EventEmitter();

    private currentPos: { x: number; y: number } = null;
    constructor() {}

    private getSVG() {
        return this.columnResize ? "images/drag-vertical.svg" : "images/drag-horizontal.svg";
    }

    private startDragging(e: MouseEvent) {
        this.currentPos = this.getMousePos(e);

        $(document)
            .on("mousemove.rsz", this.drag.bind(this))
            .on("mouseup.rsz", this.stopDragging.bind(this));

        $("iframe")
            .contents()
            .on("mousemove.rsz", this.drag.bind(this))
            .on("mouseup.rsz", this.stopDragging.bind(this));
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

        var amountToDrag: { x: number; y: number } = {
            x: pos.x - this.currentPos.x,
            y: pos.y - this.currentPos.y,
        };

        if (this.listen === "HORIZONTAL") {
            amountToDrag.y = 0;
        } else if (this.listen === "VERTICAL") {
            amountToDrag.x = 0;
        } else {
            amountToDrag = { x: 0, y: 0 };
        }

        this.move.emit(amountToDrag);
        this.currentPos = pos;
    }

    private stopDragging(e: MouseEvent) {
        e.stopPropagation();
        e.preventDefault();
        $(document).off(".rsz");
        $("iframe")
            .contents()
            .off(".rsz");
        this.currentPos = null;
    }

    private getMousePos(e: MouseEvent): { x: number; y: number } {
        return typeof e.screenX !== "number" ? null : { x: e.screenX, y: e.screenY };
    }
}
