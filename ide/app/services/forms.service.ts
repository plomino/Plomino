import {Injectable} from '@angular/core';

import {Subject, Observable} from 'rxjs/Rx'

@Injectable()
export class FormsService {
    private formSettingsSaveEventSource: Subject<any> = new Subject();
    private formContentSaveEventSource: Subject<any> = new Subject();

    formSettingsSave$: Observable<any> = this.formSettingsSaveEventSource.asObservable();
    formContentSave$: Observable<any> = this.formContentSaveEventSource.asObservable();

    formSettingsSaving: boolean = false;
    formContentSaving: boolean = false;

    constructor() {

    }

    saveForm() {
        this.saveFormSettings();
        this.saveFormContent();
    }

    saveFormSettings() {
        if (!this.formSettingsSaving) {
            this.formSettingsSaving = true;
            this.formSettingsSaveEventSource.next(() => {
                this.formSettingsSaving = false;
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