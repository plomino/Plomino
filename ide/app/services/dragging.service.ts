import { TemplatesService } from './templates.service';
import { Injectable } from '@angular/core';

import { Subject } from 'rxjs/Subject';
import { Observable } from 'rxjs/Observable';

@Injectable()
export class DraggingService {
  draggingData$: Subject<any> = new Subject<any>();
  currentDraggingData: DraggingData = null;
  currentDraggingTemplateCode: string;

  constructor(private templateService: TemplatesService) {}
  
  setDragging(data?: any): void {
    this.currentDraggingTemplateCode = '';

    if (data !== false) {
      this.currentDraggingData = <DraggingData>data;
      // preload the widget code
      let {parent, templateId} = this.currentDraggingData;
      
      this.templateService
      .getTemplate(parent, templateId)
      .subscribe((widgetCode: string) => {
        this.currentDraggingTemplateCode = widgetCode;
      });
    }
    else {
      this.currentDraggingData = null;
    }
    
    this.draggingData$.next(data);
  }

  somethingIsDragging(): boolean {
    return this.currentDraggingData !== null;
  }

  getDragging(): Observable<any> {
    return this.draggingData$.asObservable();
  }
}
