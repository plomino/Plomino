import { PlominoHTTPAPIService } from './../../services/http-api.service';
import { 
    Component, 
    Input, 
    Output,
    EventEmitter, 
    ViewChild, 
    ElementRef,
    ChangeDetectorRef,
    ChangeDetectionStrategy
} from '@angular/core';

import { 
    Http, 
    Headers, 
    Response, 
    RequestOptions 
} from '@angular/http';

import { Observable } from 'rxjs/Rx';
import { ObjService } from '../../services/obj.service';
import { PloneHtmlPipe } from '../../pipes';

@Component({
    selector: 'plomino-palette-dbsettings',
    template: require('./dbsettings.component.html'),
    styles: [require('./dbsettings.component.css')],
    directives: [],
    providers: [ObjService],
    pipes: [PloneHtmlPipe],
    changeDetection: ChangeDetectionStrategy.OnPush
})

export class DBSettingsComponent {

    @ViewChild('dbform') el:ElementRef;

    dbForm: string = '';
    importExportDialog: HTMLDialogElement;

    constructor(private objService: ObjService,
      private changeDetector: ChangeDetectorRef,
      private http: PlominoHTTPAPIService,
    ) {
      this.importExportDialog = <HTMLDialogElement> 
        document.querySelector('#db-import-export-dialog');
      if (!this.importExportDialog.showModal) {
        dialogPolyfill.registerDialog(this.importExportDialog);
      }

      this.importExportDialog.querySelector('.close')
      .addEventListener('click', () => {
        this.importExportDialog.close();
      });
    }

    submitForm() {
        // this.el is the div that contains the Edit Form
        // We want to seralize the data in the form, submit it to the form
        // action. If the response is <div class="ajax_success">, we re-fetch
        // the form. Otherwise we update the displayed form with the response
        // (which may have validation failures etc.) 
        let form: HTMLFormElement = <HTMLFormElement> $(this.el.nativeElement).find('form').get(0);
        let formData: FormData = new FormData(form);
        
        formData.append('form.buttons.save', 'Save');
        
        this.objService.submitDB(formData)
            .flatMap((responseHtml: string) => {
                if (responseHtml.indexOf('dl.error') > -1) {
                    return Observable.of(responseHtml);
                } else {
                    return this.objService.getDB();
                }
            })
            .subscribe(responseHtml => {
                this.dbForm = responseHtml;
                this.changeDetector.markForCheck();
            }, err => { 
                console.error(err) 
            });
    }

    cancelForm() {
      this.getDbSettings();
    }

    ngOnInit() {
      this.getDbSettings();
    }

    private showImportExport() {
      const content = this.importExportDialog
        .querySelector('.mdl-dialog__content');

      content.innerHTML = `<div class="mdl-spinner mdl-js-spinner is-active"></div>`;
      this.importExportDialog.showModal();

      /**
       * load import/export form
       */
      this.http.get(`../../DatabaseReplication`)
      .subscribe((response: Response) => {
        let $parsedVD = $(response.toString());
        let $importExportPlominoForm = $parsedVD.find('#content .pat-autotoc.autotabs');
        content.innerHTML = $importExportPlominoForm.get(0).outerHTML;

        /* memory clean */
        $parsedVD.remove();
        $parsedVD = null;
        $importExportPlominoForm.remove();
        $importExportPlominoForm = null;
      });
    }

    private getDbSettings() {
      this.objService.getDB().subscribe(html => { 
        this.dbForm = html;
        this.changeDetector.markForCheck();
      }, err => { 
        console.error(err);
      });
    }

}


