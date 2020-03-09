import { Injectable } from "@angular/core";

@Injectable()
export class PlominoPaletteManagerService {
    constructor() {}

    public resizeInnerScrollingContainers() {
        const $wrapper = $(".palette-wrapper .mdl-tabs__panel");
        const $containers76 = $(".scrolling-container--76");
        const $containers66 = $(".scrolling-container--66");
        const $containers0 = $(".scrolling-container--0");
        const height = parseInt($wrapper.css("height").replace("px", ""), 10);
        $containers76.css("height", `${height - 76}px`);
        $containers66.css("height", `${height - 66}px`);
        $containers0.css("height", `${height}px`);
    }
}
