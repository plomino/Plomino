import {Injectable} from '@angular/core';

import {Subject, Observable} from 'rxjs/Rx'

@Injectable()
export class FormsService {
    private paletteTabChangeEventSource: Subject<any> = new Subject();
    private formSettingsSaveEventSource: Subject<any> = new Subject();
    private formContentSaveEventSource: Subject<any> = new Subject();

    private FORM_SETTINGS_TAB_INDEX:number = 2;

    paletteTabChange$: Observable<any> = this.paletteTabChangeEventSource.asObservable();
    formSettingsSave$: Observable<any> = this.formSettingsSaveEventSource.asObservable();
    formContentSave$: Observable<any> = this.formContentSaveEventSource.asObservable();

    formSettingsSaving: boolean = false;
    formContentSaving: boolean = false;
    formSaving: boolean = false;

    constructor() {

    }

    changePaletteTab(tabIndex: number) {
        this.paletteTabChangeEventSource.next(tabIndex);
    }

    saveForm() {
        if (this.formSaving) return;
        this.formSaving = true;

        this.changePaletteTab(this.FORM_SETTINGS_TAB_INDEX);

        this.saveFormSettings(() => {
            this.saveFormContent(() => {
                this.formSaving = false;
            });
        });
    }

    saveFormSettings(cb: any) {
        this.formSettingsSaveEventSource.next(() => {
            cb();
        });
    }

    saveFormContent(cb: any) {
        this.formContentSaveEventSource.next(() => {
            cb();
        });
    }

    getIdFromUrl(url: any) {
        let arr = url.split('/');
        return arr[arr.length - 1];
    }

    setIdForUrl(url: any, id: number) {
        let arr = url.split('/');
        arr[arr.length - 1] = id;
        return arr.join('/');
    }

}