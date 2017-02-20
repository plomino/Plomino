import { Injectable } from '@angular/core';
import { Response } from '@angular/http';

import { Observable } from 'rxjs/Rx';

import { ElementService } from '../../../services';

import 'jquery';
declare let $: any;

@Injectable()
export class UpdateFieldService {
  
  constructor(private elementService: ElementService) { }

  updateField(item: any): Observable<any> {
    if (item.type === 'Hidewhen') {
      let result = Object.assign({}, { 
        newTemplate: this.wrapHidewhen2(item.type, item.newId, item.oldTemplate),
        item: item
      }, { 
        oldTemplate: item.oldTemplate 
      });

      return Observable.of(result);
    }
    
    // TODO: Replace assign with passing data through operators in sequence
    // tiny-mce.component.ts 307 -> 323
    return this.getElementLayout(item).map((itemTemplate: any) => {
      if (item.type === 'Field' || 'Action') {
        return Object.assign({}, { 
          newTemplate: this.wrapFieldOrAction(item.type, item.newId, itemTemplate),
          item: item
        }, { 
          oldTemplate: item.oldTemplate 
        });

      } else if (item.type === 'Label') {
        return Object.assign({}, { 
          newTemplate: itemTemplate 
        }, { 
          oldTemplate: item.oldTemplate 
        });
      }
    });
  }


  private getElementLayout(element: any): Observable<Response> {
    return this.elementService.getWidget(
      element.base, element.type.toLowerCase(), element.newId
    );
  }

  private wrapElement(elType: string, id: string, content: string) {
    switch(elType) {
      case 'plominoField':
      case 'plominoAction':
        return this.wrapFieldOrAction(elType, id, content);
      case 'plominoHidewhen':
        return this.wrapHidewhen(elType, id, content);
      default:
    }
  }

  private wrapFieldOrAction(elType: string, id: string, contentString: string) {  
    let $response = $(contentString);
    let $class = `plomino${elType}Class`;

    let container = 'span';
    let content = '';
    let $newId: any;

    if ($response.find("div,table,p").length) {
      container = "div";
    }
    
    if (contentString != undefined) {
      content = `
        <${container} class="${$class} mceNonEditable" 
          data-mce-resize="false" 
          data-plominoid="${id}">
          ${contentString}    
        </${container}>`;
    } else {
      content = `<span class="${$class}">${id}</span>`;
    }

    return content;
  }

  private wrapHidewhen2(elType: string, id: string, contentString: string) {
    let $element = $(contentString); 
    let $class = $element.attr('class');
    // let $position = $element.text().split(':')[0];
    // let $id = $element.text().split(':')[1];
    let $position = $element.data('plominoPosition');
    // let $id = $element.data('plominoid');
  
    let container = 'span';
    let content = `
      <${container} class="${$class}"
        data-present-method="convertFormHidewhens" 
        data-mce-resize="false"
        content-editable="false"
        data-plomino-position="${$position}" 
        data-plominoid="${id}">
        &nbsp;
      </${container}>`;

    return content;
  }

  private wrapHidewhen(elType: string, id: string, contentString: string) {
    let $element = $(contentString); 
    let $class = $element.attr('class');
    let $position = $element.text().split(':')[0];
    let $id = $element.text().split(':')[1];
  
    let container = 'span';
    let content = `
      <${container} class="${$class}"
        data-present-method="convertFormHidewhens" 
        data-mce-resize="false"
        content-editable="false"
        data-plomino-position="${$position}" 
        data-plominoid="${$id}">
        &nbsp;
      </${container}>${ $position === 'start' ? '' : '<br />' }`;

    return content;
  }
}
