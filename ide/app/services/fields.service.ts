import { IField } from "./../interfaces/field.interface";
import { LogService } from "./log.service";
import { PlominoHTTPAPIService } from "./http-api.service";
import { Response } from "@angular/http";
import { Injectable } from "@angular/core";

import { Subject } from "rxjs/Subject";
import { Observable } from "rxjs/Observable";

@Injectable()
export class FieldsService {
    viewColumnInserted: Subject<string> = new Subject<string>();
    viewActionInserted: Subject<string> = new Subject<string>();
    viewReIndex: Subject<any> = new Subject<any>();
    viewColumnCreated: Subject<any> = new Subject<any>();
    viewColumnUpdated: Subject<any> = new Subject<any>();

    deleteSelectedColumn: Subject<string> = new Subject<string>();
    deleteSelectedAction: Subject<string> = new Subject<string>();

    private insertionStream$: Subject<InsertFieldEvent> = new Subject<InsertFieldEvent>();
    private updatesStream$: Subject<PlominoFieldUpdatesStreamEvent> = new Subject<PlominoFieldUpdatesStreamEvent>();

    constructor(private http: PlominoHTTPAPIService, private log: LogService) {}

    onReIndexItems() {
        return this.viewReIndex.asObservable();
    }

    /**
     * happens when you save new column in field settings
     */
    onColumnCreated() {
        return this.viewColumnCreated.asObservable();
    }

    /**
     * happens when you save existing column in field settings
     */
    onColumnUpdated() {
        return this.viewColumnUpdated.asObservable();
    }

    onDeleteSelectedViewColumn(): Observable<string> {
        return this.deleteSelectedColumn.asObservable();
    }

    onDeleteSelectedViewAction(): Observable<string> {
        return this.deleteSelectedAction.asObservable();
    }

    onNewColumn() {
        return this.viewColumnInserted.asObservable();
    }

    onNewAction() {
        return this.viewActionInserted.asObservable();
    }

    insertField(field: InsertFieldEvent) {
        this.log.info("insertField", field);
        this.insertionStream$.next(field);
    }

    updateField(fieldData: IField, newFieldData: PlominoFieldSettingsFormDataObject, id: string) {
        this.updatesStream$.next(<PlominoFieldUpdatesStreamEvent>{
            fieldData: fieldData,
            newData: newFieldData,
            newId: id,
        });
    }

    listenToUpdates(): Observable<PlominoFieldUpdatesStreamEvent> {
        return this.updatesStream$.asObservable();
    }

    getTemplate(formUrl: string, widgetType: string) {
        return this.http
            .post(
                `${formUrl}/@@tinyform/example_widget`,
                JSON.stringify({ widget_type: widgetType }),
                "fields.service.ts getTemplate"
            )
            .map((response: Response) => {
                return response.json();
            });
    }

    getInsertion(): Observable<InsertFieldEvent> {
        return this.insertionStream$.asObservable();
    }
}
