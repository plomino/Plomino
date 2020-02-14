import 'babel-polyfill';
import { enableProdMode } from '@angular/core';
import { HTTP_PROVIDERS } from '@angular/http';
import { AppComponent } from './app.component';
import { DND_PROVIDERS } from 'ng2-dnd';
import { PlominoBlockPreloaderComponent } from "./utility";
// import { DeprecatedFormsModule } from '@angular/common';
// import { BrowserModule } from "@angular/platform-browser";
import { bootstrap } from '@angular/platform-browser-dynamic';
import { disableDeprecatedForms, provideForms } from "@angular/forms";
// import 'underscore';


window['_'] = require('underscore');
const templateFunction = window['_'].template.bind(_);
window['_']['template'] = (template: string, options: any = null) => {
  return options ? templateFunction(template)(options) 
    : templateFunction(template);
};

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

// future RC5 migration:

// @NgModule({
//   declarations: [AppComponent, PlominoBlockPreloaderComponent],
//   providers: [HTTP_PROVIDERS, DND_PROVIDERS],
//   imports: [BrowserModule, FormsModule],
//   bootstrap:  [AppComponent],
// })
// class MyAppModule{}

// platformBrowserDynamic().bootstrapModule(MyAppModule);
