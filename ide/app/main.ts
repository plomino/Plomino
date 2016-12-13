import {bootstrap}    from '@angular/platform-browser-dynamic'
import {HTTP_PROVIDERS} from '@angular/http';
import {disableDeprecatedForms, provideForms} from '@angular/forms';
import {AppComponent} from './app.component';
import {DND_PROVIDERS} from 'ng2-dnd';

bootstrap(AppComponent,
[
    HTTP_PROVIDERS,
    DND_PROVIDERS,
    disableDeprecatedForms(),
    provideForms()
]);
