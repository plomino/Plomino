import { PlominoDBService } from "./../../services/db.service";
import { ElementService } from "./../../services/element.service";
import { Observable } from "rxjs/Rx";
import { Headers, Response, RequestOptions } from "@angular/http";
import { PlominoHTTPAPIService } from "./../../services/http-api.service";
import { Injectable } from "@angular/core";

@Injectable()
export class PlominoViewsAPIService {
    constructor(
        private http: PlominoHTTPAPIService,
        private elementService: ElementService,
        private dbService: PlominoDBService
    ) {}

    fetchViewTableHTML(url: string): Observable<string> {
        return this.http.get(`${url}/view`).map((response: Response) => response.text());
    }

    fetchViewTableDataJSON(url: string): Observable<PlominoViewData> {
        return this.http
            .get(`${url}/tojson`)
            .map((response: Response) => response.json())
            .catch((err: any) => {
                return Observable.of({ rows: [], total: 0, displayed: 0 });
            });
    }

    fetchViewTableColumnsJSON(url: string): Observable<PlominoVocabularyViewData> {
        let reqURL = this.getPloneLink() + "/@@getVocabulary?name=plone.app.vocabularies.Catalog";
        reqURL += "&query={%22criteria%22:[{%22i%22:%22path%22,%22o%22:%22";
        reqURL += "plone.app.querystring.operation.string.path%22,%22v%22:%22/";
        reqURL += url
            .split("/")
            .slice(-2)
            .join("/");
        reqURL += "::1%22}],%22sort_on%22:%22getObjPositionInParent%22,";
        reqURL += "%22sort_order%22:%22ascending%22}&batch={%22page%22:1,%22size%22:100}";
        reqURL += "&attributes=[%22id%22,%22Type%22]";
        return this.http
            .get(reqURL)
            .map((response: Response) => response.json())
            .catch((err: any) => {
                return Observable.of({ results: [], total: 0 });
            });
    }

    fetchViewTable(
        url: string,
        static_rendering: boolean
    ): Observable<[string, PlominoVocabularyViewData, PlominoViewData]> {
        if (static_rendering) {
            url += url.indexOf("?") === -1 ? "?" : "&";
            url = url + "static_rendering=true";
        }

        const html$ = this.fetchViewTableHTML(url);
        const json$ = this.fetchViewTableColumnsJSON(url);
        const jsonData$ = this.fetchViewTableDataJSON(url);
        return <Observable<[string, PlominoVocabularyViewData, PlominoViewData]>>(
            Observable.forkJoin(html$, json$, jsonData$)
        );
    }

    addNewAction(url: string, id = "default-action"): Observable<AddFieldResponse> {
        const field = {
            title: "default-action",
            action_type: "OPENFORM",
            "@type": "PlominoAction",
        };
        return this.elementService.postElement(url, field);
    }

    addNewColumn(url: string, id = "default-column"): Observable<string> {
        const token = this.getCSRFToken();
        const form = new FormData();

        form.append("form.widgets.IShortName.id", id);
        form.append("form.widgets.IBasic.title", id);
        form.append("form.widgets.displayed_field:list", "--NOVALUE--");
        form.append("form.widgets.displayed_field-empty-marker", "1");
        form.append("form.widgets.hidden_column-empty-marker", "1");
        form.append("ajax_load", "");
        form.append("ajax_include_head", "");
        form.append("form.widgets.IHelpers.helpers:list", "");
        form.append("form.widgets.formula", "");
        form.append("form.widgets.IBasic.description", "");
        form.append("form.buttons.save", "Save");
        form.append("_authenticator", token);

        return this.http
            .postWithOptions(
                `${url}/++add++PlominoColumn`,
                form,
                new RequestOptions({}),
                "views-api.service.ts addNewColumn"
            )
            .map((response: Response) => {
                return response.url
                    .replace("/view", "")
                    .split("/")
                    .pop();
            });
    }

    reOrderItem(url: string, id: string, delta: number, subsetIds: string[]): Observable<any> {
        const token = this.getCSRFToken();

        const options = {
            delta,
            id,
            subsetIds,
            _authenticator: token,
        };

        return this.http
            .postWithOptions(
                `${url}/fc-itemOrder`,
                $.param(options),
                new RequestOptions({
                    headers: new Headers({
                        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                        "X-CSRF-TOKEN": token,
                        "X-Requested-With": "XMLHttpRequest",
                    }),
                }),
                "views-api.service.ts dragColumn"
            )
            .map((response: Response) => response.json());
    }

    getCSRFToken() {
        const authenticator = document.getElementsByName("_authenticator");
        const token = (<HTMLInputElement>authenticator[0]).value;
        return token;
    }

    getPloneLink() {
        const dbLink = this.dbService.getDBLink();
        return dbLink
            .split("/")
            .slice(0, -1)
            .join("/");
    }
}
