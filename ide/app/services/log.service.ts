/* tslint:disable */
import { Injectable } from '@angular/core';

@Injectable()
export class LogService {
  debugMode = false;
  ieMode: boolean = '-ms-scroll-limit' in document.documentElement.style 
        && '-ms-ime-align' in document.documentElement.style;

  constructor() {
    this.debugMode = true; // todo: auto-detect debug using angular environment
  }

  info(...args: any[]) {
    if (!this.debugMode) { return; }
    if (!this.ieMode) { args.unshift('color: blue'); }
    args.unshift(`${ this.ieMode || '%c' }${(new Date()).toLocaleTimeString()} debug info:`);
    (<any>console).info(...args);
  }

  warn(...args: any[]) {
    if (!this.debugMode) { return; }
    if (!this.ieMode) { args.unshift('color: navy;font-weight: bold'); }
    args.unshift(`${ this.ieMode || '%c' }${(new Date()).toLocaleTimeString()} debug warn:`);
    (<any>console).info(...args);
  }

  extra(info: string) {
    if (!this.debugMode) { return; }
    if (!this.ieMode) {
      (<any>console).info(`%c---------------------> ${info}`, 'color: darkgreen');
    }
    else {
      (<any> console).info(info);
    }
  }

  error(...args: any[]) {
    if (!this.ieMode) { args.unshift('color: red'); }
    args.unshift(`${ this.ieMode || '%c' }${(new Date()).toLocaleTimeString()} error:`);
    (<any>console).info(...args);
  }

  startTimer(name = Math.random().toString()): string {
    if (this.debugMode) {
      console.time(name);
    }
    return name;
  }

  stopTimer(name: string) {
    if (!this.debugMode) { return; }
    console.timeEnd(name);
  }
}
/* tslint:enable */
