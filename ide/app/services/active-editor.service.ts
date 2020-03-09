import { Subject } from "rxjs/Rx";
import { Injectable } from "@angular/core";

@Injectable()
export class PlominoActiveEditorService {
    editorURL: string = null;
    private editorLoadingPushSubject: Subject<boolean> = new Subject<boolean>();
    private editorLoadingPush$ = this.editorLoadingPushSubject.asObservable();
    private editorSavedPushSubject: Subject<boolean> = new Subject<boolean>();
    private editorSavedPush$ = this.editorSavedPushSubject.asObservable();

    constructor() {}

    setActive(editorURL: string, fixEditors = false) {
        /* hide all another editors */
        this.editorURL = editorURL;

        if (fixEditors) {
            $("plomino-tiny-mce").css({
                position: "fixed",
                top: 0,
                left: 0,
                "pointer-events": "none",
                "z-index": -111111,
            });

            if (editorURL !== null) {
                const edId = editorURL.split("/").pop();
                $(`plomino-tiny-mce:has(textarea[id="${edId}"])`).removeAttr("style");
            }
        }
    }

    turnActiveEditorToLoadingState(state = true) {
        this.editorLoadingPushSubject.next(state);
    }

    turnActiveEditorToSavedState() {
        this.editorSavedPushSubject.next(true);
    }

    onLoadingPush() {
        return this.editorLoadingPush$;
    }

    onSavedPush() {
        return this.editorSavedPush$;
    }

    getActive(): TinyMceEditor {
        return tinymce.get(this.editorURL ? this.editorURL.split("/").pop() : null);
    }
}
