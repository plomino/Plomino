/* tslint:disable */
import { Injectable } from '@angular/core';

@Injectable()
export class LogService {
  debugMode: boolean = false;

  constructor() {
    this.debugMode = true; // todo: auto-detect debug using angular environment
  }

  info(...args: any[]) {
    if (!this.debugMode) { return; }
    args.unshift('color: blue');
    args.unshift(`%c${(new Date()).toLocaleTimeString()} debug info:`);
    (<any>console).info(...args);
  }

  extra(info: string) {
    if (!this.debugMode) { return; }
    (<any>console).info(`%c---------------------> ${info}`, 'color: darkgreen');
  }

  error(...args: any[]) {
    args.unshift('color: red');
    args.unshift(`%c${(new Date()).toLocaleTimeString()} error:`);
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
