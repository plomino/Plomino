import { LogService } from './log.service';
import {Injectable} from '@angular/core';

import {Subject, Observable, } from 'rxjs/Rx'

@Injectable()
export class FormsService {
    private paletteTabChangeEventSource: Subject<any> = new Subject();
    private formSettingsSaveEventSource: Subject<any> = new Subject();
    private formContentSaveEventSource: Subject<any> = new Subject();
    private formIdChangedEventSource: Subject<{oldId: any, newId: any}> 
      = new Subject<{oldId: any, newId: any}>();
    private getFormContentBeforeSaveSource: Subject<any> = new Subject();
    private onFormContentBeforeSaveSource: Subject<any> = new Subject();

    private FORM_SETTINGS_TAB_INDEX:number = 2;

    paletteTabChange$: Observable<any> = this.paletteTabChangeEventSource.asObservable();
    formSettingsSave$: Observable<any> = this.formSettingsSaveEventSource.asObservable();
    formContentSave$: Observable<any> = this.formContentSaveEventSource.asObservable();
    formIdChanged$: Observable<{oldId: any, newId: any}> = this.formIdChangedEventSource.asObservable();
    getFormContentBeforeSave$: Observable<any> = this.getFormContentBeforeSaveSource.asObservable();
    onFormContentBeforeSave$: Observable<any> = this.onFormContentBeforeSaveSource.asObservable();

    formSettingsSaving: boolean = false;
    formContentSaving: boolean = false;
    formSaving: boolean = false;

    constructor(private log: LogService) {

    }

    getFormContentBeforeSave(id:any) {
      this.getFormContentBeforeSaveSource.next({
        id: id
      });
    }

    onFormContentBeforeSave(data:{id:any, content:any}) {
      this.onFormContentBeforeSaveSource.next({
        id: data.id,
        content: data.content
      });
    }

    changePaletteTab(tabIndex: number) {
        this.paletteTabChangeEventSource.next(tabIndex);
    }

    saveForm(id: any, changeTab = true) {
        this.log.info('saveForm called, this.formSaving', this.formSaving);
        
        if (this.formSaving) return;
        this.formSaving = true;

        if (changeTab) {
            this.changePaletteTab(this.FORM_SETTINGS_TAB_INDEX);
        }

        this.saveFormSettings(id, () => {
            this.saveFormContent(id, () => {
                this.formSaving = false;
            });
        });
    }

    saveFormSettings(id:any, cb: any) {
        this.formSettingsSaveEventSource.next({
            formUniqueId: id,
            cb: cb
        });
    }

    saveFormContent(id:any, cb: any) {
        this.formContentSaveEventSource.next({
            formUniqueId: id,
            cb: cb
        });
    }

    changeFormId(data:{oldId: any, newId: any}) {
        this.formIdChangedEventSource.next(data)
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
