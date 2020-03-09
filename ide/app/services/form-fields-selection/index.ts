import { PlominoElementAdapterService } from "./../element-adapter.service";
import { PlominoActiveEditorService } from "./../active-editor.service";
import { LogService } from "./../log.service";
import { IField } from "./../../interfaces/field.interface";
import { BehaviorSubject, Observable } from "rxjs/Rx";
import { Injectable } from "@angular/core";

@Injectable()
export class PlominoFormFieldsSelectionService {
    private activeField$: BehaviorSubject<IField> = new BehaviorSubject(null);

    constructor(
        private activeEditorService: PlominoActiveEditorService,
        private log: LogService,
        private adapter: PlominoElementAdapterService
    ) {}

    flushActiveField() {
        this.activeField$.next(null);
    }

    selectField(fieldData: IField | "none"): void {
        let field: IField = null;

        this.log.info("selectField", fieldData, this.adapter.getSelectedBefore());

        if (fieldData && fieldData !== "none" && !fieldData.id && fieldData.type === "subform") {
            setTimeout(() => {
                const $selected = $(this.activeEditorService.getActive().getBody()).find('[data-mce-selected="1"]');
                this.log.info("hacked id", $selected.data("plominoid"));
                fieldData.id = $selected.data("plominoid");

                if (typeof fieldData.id === "undefined" && $selected.hasClass("plominoSubformClass")) {
                    fieldData.id = "Subform";
                }

                if (fieldData && <any>fieldData !== "none" && fieldData.id) {
                    field = Object.assign(
                        {},
                        {
                            id: fieldData.id,
                            url: `${fieldData.parent}/${fieldData.id}`,
                            type: fieldData.type,
                        }
                    );
                }

                this.activeField$.next(field);
            }, 100);
        } else {
            if (fieldData && fieldData !== "none" && fieldData.id) {
                field = Object.assign(
                    {},
                    {
                        id: fieldData.id,
                        url: `${fieldData.parent}/${fieldData.id}`,
                        type: fieldData.type,
                    }
                );
            }

            this.activeField$.next(field);
        }
    }

    selectNonExistingField(fieldData: IField): void {
        let field: IField = null;

        field = Object.assign(
            {},
            {
                id: `${fieldData.parent}/${fieldData.url}`,
                type: fieldData.type,
            }
        );

        this.activeField$.next(field);
    }

    getActiveField(): Observable<IField> {
        return this.activeField$.asObservable().share();
    }
}
