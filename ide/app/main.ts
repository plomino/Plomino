import { enableProdMode } from '@angular/core';
import {bootstrap}    from '@angular/platform-browser-dynamic';
import {HTTP_PROVIDERS} from '@angular/http';
import {disableDeprecatedForms, provideForms} from '@angular/forms';
import {AppComponent} from './app.component';
import {DND_PROVIDERS} from 'ng2-dnd/ng2-dnd';

window['MacroWidgetPromise'] = <Promise<any>> new Promise(
    (resolve, reject) => {
    window['MacroWidgetPromiseResolve'] = resolve;
});
window['PlominoMacrosPromise'] = <Promise<any>> new Promise(
    (resolve, reject) => {
    window['PlominoMacrosPromiseResolve'] = resolve;
});
window['registryPromise'] = <Promise<any>> new Promise(
    (resolve, reject) => {
    window['registryPromiseResolve'] = resolve;
});

// console.info = () => {};

enableProdMode();
bootstrap(AppComponent, [
    HTTP_PROVIDERS,
    DND_PROVIDERS,
    disableDeprecatedForms(),
    provideForms()
]);
