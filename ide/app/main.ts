import 'babel-polyfill';
import { enableProdMode } from '@angular/core';
import {bootstrap}    from '@angular/platform-browser-dynamic';
import {HTTP_PROVIDERS} from '@angular/http';
import {disableDeprecatedForms, provideForms} from '@angular/forms';
import {AppComponent} from './app.component';
import { DND_PROVIDERS } from 'ng2-dnd';
import { PlominoBlockPreloaderComponent } from "./utility";

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
window['materialPromise'] = <Promise<any>> new Promise(
    (resolve, reject) => {
    window['materialPromiseResolve'] = resolve;
    window['materialPromiseReject'] = reject;
});

// console.info = () => {};

enableProdMode();
bootstrap(AppComponent, [
    HTTP_PROVIDERS,
    DND_PROVIDERS,
    PlominoBlockPreloaderComponent,
    disableDeprecatedForms(),
    provideForms()
]);
