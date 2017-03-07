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
    aclDialog: HTMLDialogElement;
    okDialog: HTMLDialogElement;

    constructor(private objService: ObjService,
      private changeDetector: ChangeDetectorRef,
      private http: PlominoHTTPAPIService,
    ) {
      this.importExportDialog = <HTMLDialogElement> 
        document.querySelector('#db-import-export-dialog');
      this.aclDialog = <HTMLDialogElement> 
        document.querySelector('#db-acl-dialog');
      this.okDialog = <HTMLDialogElement> 
        document.querySelector('#ok-dialog');

      if (!this.importExportDialog.showModal) {
        dialogPolyfill.registerDialog(this.importExportDialog);
      }

      if (!this.okDialog.showModal) {
        dialogPolyfill.registerDialog(this.okDialog);
      }

      if (!this.aclDialog.showModal) {
        dialogPolyfill.registerDialog(this.aclDialog);
      }

      this.importExportDialog.querySelector('.mdl-dialog__actions button')
      .addEventListener('click', () => {
        this.importExportDialog.close();
      });

      this.okDialog.querySelector('.mdl-dialog__actions button')
      .addEventListener('click', () => {
        this.okDialog.close();
      });

      this.aclDialog.querySelector('.mdl-dialog__actions button')
      .addEventListener('click', () => {
        this.aclDialog.close();
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

    private showACL() {
      const contentBlock = this.aclDialog
        .querySelector('.mdl-dialog__content');
      const accessRightsBlock = contentBlock.querySelector('#acl-access-rights');
      const accessUserRolesBlock = contentBlock.querySelector('#acl-user-roles');
      const accessSpcActionBlock = contentBlock.querySelector('#acl-spc-action-rights');

      const prepareACLContent = () => {
        accessRightsBlock.innerHTML = 
          `<p><div class="mdl-spinner mdl-js-spinner is-active"></div></p>`;
        accessUserRolesBlock.innerHTML = 
          `<p><div class="mdl-spinner mdl-js-spinner is-active"></div></p>`;
        accessSpcActionBlock.innerHTML = 
          `<p><div class="mdl-spinner mdl-js-spinner is-active"></div></p>`;
        
        componentHandler.upgradeDom();
      };

      prepareACLContent();

      const updateACLContent = (content: string) => {
        const $parsedVD = $(content);
        const $importExportPlominoForm = $parsedVD.find('#content .pat-autotoc.autotabs');
        $importExportPlominoForm.find('legend').remove();
        const $fieldSets = $importExportPlominoForm.find('fieldset');

        const accessRightsBlockHTML = $fieldSets.first().html();
        const accessUserRolesBlockHTML = $fieldSets.slice(1, 2).first().html();
        const accessSpcActionBlockHTML = $fieldSets.last().html();
        
        accessRightsBlock.innerHTML = `<p>${ accessRightsBlockHTML }</p>`;
        accessUserRolesBlock.innerHTML = `<p>${ accessUserRolesBlockHTML }</p>`;
        accessSpcActionBlock.innerHTML = `<p>${ accessSpcActionBlockHTML }</p>`;

        $(this.aclDialog).find('form').submit((submitEvent: Event) => {
          submitEvent.preventDefault();
          submitEvent.stopPropagation();

          const form = <HTMLFormElement> submitEvent.currentTarget;
          const formData = new FormData(form);
          
          this.http.postWithOptions(
            form.action.replace('++resource++Products.CMFPlomino/ide/', ''),
            formData, new RequestOptions({
              headers: new Headers({})
            })
          )
          .map((response: Response) => {
            if (response.status === 500) {
              throw response.json().error_type;
            }
            else {
              return response;
            }
          })
          .catch((error: any) => {
            this.okDialog
              .querySelector('.mdl-dialog__content')
              .innerHTML = `<p>${ error }</p>`;
            this.okDialog.showModal();
            return Observable.throw(error);
          })
          .subscribe((response: Response) => {
            let result = response.text();
            updateACLContent(result);
          });
        });
      };
      
      this.aclDialog.showModal();

      this.http.get(
        `${ window.location
            .pathname
            .replace('++resource++Products.CMFPlomino/ide/', '')
            .replace('/index.html', '')
          }/DatabaseACL`
      )
      .subscribe((response: Response) => {
        updateACLContent(response.text());
      });
    }

    private showImportExport() {
      const contentBlock = this.importExportDialog
        .querySelector('.mdl-dialog__content');

      const CSVImportationBlock = contentBlock.querySelector('#csv-importation');
      const JSONImportExportBlock = contentBlock.querySelector('#json-import-export');

      CSVImportationBlock.innerHTML = 
        `<p><div class="mdl-spinner mdl-js-spinner is-active"></div></p>`;
      JSONImportExportBlock.innerHTML = 
        `<p><div class="mdl-spinner mdl-js-spinner is-active"></div></p>`;
      
      componentHandler.upgradeDom();
      this.importExportDialog.showModal();

      /**
       * load import/export form
       */
      this.http.get(
        `${ window.location
            .pathname
            .replace('++resource++Products.CMFPlomino/ide/', '')
            .replace('/index.html', '')
          }/DatabaseReplication`
      )
      .subscribe((response: Response) => {
        const $parsedVD = $(response.text());
        const $importExportPlominoForm = $parsedVD.find('#content .pat-autotoc.autotabs');
        $importExportPlominoForm.find('legend').remove();
        const $fieldSets = $importExportPlominoForm.find('fieldset');
        const CSVImportationBlockHTML = $fieldSets.first().html();
        const JSONImportExportBlockHTML = $fieldSets.last().html();
        
        CSVImportationBlock.innerHTML = `<p>${ CSVImportationBlockHTML }</p>`;
        JSONImportExportBlock.innerHTML = `<p>${ JSONImportExportBlockHTML }</p>`;

        $(this.importExportDialog)
          .find('.actionButtons input#import_csv')
          .replaceWith(`
            <input type="hidden" name="import_csv" value="Import">
            <button type="submit"
              class="mdl-button mdl-button-js
                mdl-color-text--white
                mdl-button--raised mdl-color--blue-900">
              Import
            </button>
          `);

        componentHandler.upgradeDom();

        $(this.importExportDialog).find('form').submit((submitEvent: Event) => {
          submitEvent.preventDefault();
          submitEvent.stopPropagation();
          const form = <HTMLFormElement> submitEvent.currentTarget;
          const formData = new FormData(form);

          if (/^.+?manage_importation$/.test(form.action)) {
            formData.set('actionType', 'import');
          }

          this.http.postWithOptions(
            form.action.replace('++resource++Products.CMFPlomino/ide/', ''),
            formData, new RequestOptions({
              headers: new Headers({
                // 'Content-Type': 'multipart/form-data'
              })
            })
          )
          .map((response: Response) => {
            if (response.status === 500) {
              throw response.json().error_type;
            }
            else {
              return response;
            }
          })
          .catch((error: any) => {
            this.okDialog
              .querySelector('.mdl-dialog__content')
              .innerHTML = `<p>${ error }</p>`;
            this.okDialog.showModal();
            return Observable.throw(error);
          })
          .subscribe((response: Response) => {
            let result = response.text();
            if (response.url.indexOf('AsJSON') !== -1) {
              window.URL = (<any> window).webkitURL || window.URL;
              const jsonString = JSON.stringify(response.json(), undefined, 2);
              var link = document.createElement('a');
              link.download = 'data.json';
              var blob = new Blob([jsonString], { type: 'text/plain' });
              link.href = window.URL.createObjectURL(blob);
              link.click();
            }
            else {
              let start = result.indexOf('<div class="outer-wrapper">');
              let end = result.indexOf('<!--/outer-wrapper -->');
              result = result.slice(start, end);
              start = result.indexOf('<aside id="global_statusmessage">');
              end = result.indexOf('</aside>');
              result = result.slice(start, end + '</aside>'.length);

              this.okDialog
              .querySelector('.mdl-dialog__content')
              .innerHTML = `<p>${ $(result).text() }</p>`;

              // this.importExportDialog.close();
              this.okDialog.showModal();
            }
          });
        });
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


