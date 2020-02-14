import { Pipe } from '@angular/core';
import { DomSanitizationService } from '@angular/platform-browser';

@Pipe({name: 'safePloneHtml'})
export class PloneHtmlPipe {

    constructor(protected sanitizer: DomSanitizationService) {
        this.sanitizer = sanitizer;
    }

    transform(html: string) {
        // We only want the html inside the outer-wrapper
        if (html) {
            let start = html.indexOf('<div class="outer-wrapper">');
            let end = html.indexOf('<!--/outer-wrapper -->');

            if (start === -1) {
              start = html.indexOf('<article id="portal-column-content">');
              end = html.lastIndexOf('</article>');
            }
            
            html = html.slice(start, end);
        }
        return this.sanitizer.bypassSecurityTrustHtml(html);
    }
}
