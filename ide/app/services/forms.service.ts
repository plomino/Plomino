import {Injectable} from '@angular/core';

import {Subject, Observable} from 'rxjs/Rx'

@Injectable()
export class FormsService {
    private paletteTabChangeEventSource: Subject<any> = new Subject();
    private formSettingsSaveEventSource: Subject<any> = new Subject();
    private formContentSaveEventSource: Subject<any> = new Subject();

    paletteTabChange$: Observable<any> = this.paletteTabChangeEventSource.asObservable();
    formSettingsSave$: Observable<any> = this.formSettingsSaveEventSource.asObservable();
    formContentSave$: Observable<any> = this.formContentSaveEventSource.asObservable();

    formSettingsSaving: boolean = false;
    formContentSaving: boolean = false;

    constructor() {

    }

    changePaletteTab(tabIndex:number) {
        this.paletteTabChangeEventSource.next(tabIndex);
    }

    saveForm() {
        this.changePaletteTab(2);
        this.saveFormSettings(() => {
            this.saveFormContent();
        });
    }

    saveFormSettings(cb:any) {
        if (!this.formSettingsSaving) {
            this.formSettingsSaving = true;
            this.formSettingsSaveEventSource.next(() => {
                this.formSettingsSaving = false;
                cb();
            });
        }
    }

    saveFormContent() {
        if (!this.formContentSaving) {
            this.formContentSaving = true;
            this.formContentSaveEventSource.next(() => {
                this.formContentSaving = false;
            });
        }
    }

}