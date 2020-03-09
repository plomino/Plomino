import { LogService } from "./log.service";
import { Injectable } from "@angular/core";

import { Subject, Observable } from "rxjs/Rx";

@Injectable()
export class FormsService {
    private paletteTabChangeEventSource: Subject<any> = new Subject();
    private formSettingsSaveEventSource: Subject<any> = new Subject();
    private formContentSaveEventSource: Subject<any> = new Subject();
    private formIdChangedEventSource: Subject<{ oldId: any; newId: any }> = new Subject<{ oldId: any; newId: any }>();
    private getFormContentBeforeSaveSource: Subject<any> = new Subject();
    private onFormContentBeforeSaveSource: Subject<any> = new Subject();
    private formRemovedEventSource: Subject<string> = new Subject();
    private tinyMCEPatternData: Subject<{ formId: string; data: string }> = new Subject();

    public latestTinyMCEPatternData: { formId: string; data: string } = null;

    private FORM_SETTINGS_TAB_INDEX = 2;

    paletteTabChange$: Observable<any> = this.paletteTabChangeEventSource.asObservable();
    formSettingsSave$: Observable<any> = this.formSettingsSaveEventSource.asObservable();
    formContentSave$: Observable<any> = this.formContentSaveEventSource.asObservable();
    formIdChanged$: Observable<{ oldId: any; newId: any }> = this.formIdChangedEventSource.asObservable();
    formRemoved$: Observable<string> = this.formRemovedEventSource.asObservable();
    tinyMCEPatternData$ = this.tinyMCEPatternData.asObservable();
    getFormContentBeforeSave$: Observable<any> = this.getFormContentBeforeSaveSource.asObservable();
    onFormContentBeforeSave$: Observable<any> = this.onFormContentBeforeSaveSource.asObservable();

    formSettingsSaving = false;
    formContentSaving = false;
    formSaving = false;

    constructor(private log: LogService) {}

    getFormContentBeforeSave(id: any) {
        this.getFormContentBeforeSaveSource.next({
            id: id,
        });
    }

    onFormContentBeforeSave(data: { id: any; content: any }) {
        this.onFormContentBeforeSaveSource.next({
            id: data.id,
            content: data.content,
        });
    }

    newTinyMCEPatternData(data: { formId: string; data: string }) {
        this.tinyMCEPatternData.next(data);
    }

    changePaletteTab(tabIndex: number) {
        this.paletteTabChangeEventSource.next(tabIndex);
    }

    saveForm(id: any, changeTab = true, loadingSignal: boolean = null) {
        this.log.info("saveForm called, this.formSaving", this.formSaving);

        if (this.formSaving) return;
        this.formSaving = true;

        if (changeTab) {
            this.changePaletteTab(this.FORM_SETTINGS_TAB_INDEX);
        }

        this.saveFormSettings(id, () => {
            this.saveFormContent(id, () => {
                this.formSaving = false;
                loadingSignal = false;
            });
        });
    }

    saveFormSettings(id: any, cb: any) {
        this.formSettingsSaveEventSource.next({
            url: id,
            cb: cb,
        });
    }

    saveFormContent(id: any, cb: any) {
        this.formContentSaveEventSource.next({
            url: id,
            cb: cb,
        });
    }

    changeFormId(data: { oldId: string; newId: string }) {
        this.formIdChangedEventSource.next(data);
    }

    removeForm(formId: string) {
        this.formRemovedEventSource.next(formId);
    }

    getIdFromUrl(url: any) {
        const arr = url.split("/");
        return arr[arr.length - 1];
    }

    setIdForUrl(url: any, id: number) {
        const arr = url.split("/");
        arr[arr.length - 1] = id;
        return arr.join("/");
    }
}
