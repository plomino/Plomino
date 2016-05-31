import {Component, Input} from '@angular/core';

@Component({
    selector: 'my-popover',
    template: require("./popover.component.html"),
    styles: [require("./popover.component.css")]
})
export class PopoverComponent {
    @Input() name: string;
    @Input() desc: string;
}
