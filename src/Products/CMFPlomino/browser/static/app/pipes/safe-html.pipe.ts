import { Pipe } from '@angular/core';
import { DomSanitizationService } from '@angular/platform-browser';

@Pipe({name: 'safePloneHtml'})
export class PloneHtmlPipe {

    constructor(protected sanitizer: DomSanitizationService) {
        this.sanitizer = sanitizer;
    }

    transform(html:string) {
        // We only want the html inside the outer-wrapper
        if (html) {
            var start = html.indexOf('<div class="outer-wrapper">');
            var end = html.indexOf('<!--/outer-wrapper -->');
            html = html.slice(start, end)
        }
        return this.sanitizer.bypassSecurityTrustHtml(html);
    }
}