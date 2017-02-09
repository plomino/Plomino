import { Injectable } from '@angular/core';

import { Http, Response } from '@angular/http';

import { Observable } from 'rxjs/Rx';

import 'jquery';
declare let $: any;
import 'lodash';
declare let _: any;

@Injectable()
export class WidgetService {

  isTemplate: boolean = true;

  constructor(private http: Http) { }

  getGroupLayout(baseUrl: string, input: any): Observable<any> {
    // return new Promise((resolve) => {

      let $elements = $('<div />').html(input.layout)
                        .find('.plominoFieldClass, .plominoHidewhenClass, .plominoActionClass, .plominoLabelClass');
      let resultingElementsString = '';
      let contents = input.group_contents;
      let items$: any[] = [];
  
      $elements.each((index: number, element: any) => {
        let $element = $(element);
        
        switch($element.attr('class')) {
          case 'plominoFieldClass':
          case 'plominoActionClass':
            items$.push({
              type: 'field',
              contents: contents,
              baseUrl: baseUrl,
              el: $element
            });
            break;
          case 'plominoHidewhenClass':
            items$.push({
              type: 'hidewhen',
              contents: contents,
              baseUrl: baseUrl,
              el: $element
            });
            break;
          case 'plominoLabelClass':
            items$.push({
              type: 'label',
              contents: contents,
              baseUrl: baseUrl,
              el: $element
            });
            break;
          default:
        }
      });
      
      return Observable.from(items$)
                .concatMap((item: any) => {
                  if (item.type === 'hidewhen') {
                    return this.convertGroupHidewhens(item.contents, item.baseUrl, item.el);
                  }
                  
                  if (item.type === 'label') {
                    return this.convertLabel(item.baseUrl, item.el, 'group', item.contents);
                  }

                  return this.convertGroupFields(item.contents, item.baseUrl, item.el);
                })
                .reduce((formString: any, formItem: any) => {
                  return formString += formItem;
                }, '')
                .map((formString) => {
                  return this.wrapIntoGroup(formString, input.groupid);
                })
  }

  getFormLayout(baseUrl: string, layout: any): Observable<any> {
    let fields$: any[] = [];
    let $elements = $('<div />')
      .html(layout)
      .find('.plominoGroupClass, .plominoFieldClass:not(.plominoGroupClass .plominoFieldClass), .plominoHidewhenClass:not(.plominoGroupClass .plominoHidewhenClass), .plominoActionClass:not(.plominoGroupClass .plominoActionClass), .plominoLabelClass:not(.plominoGroupClass .plominoLabelClass)');

    $elements.each((index: number, element: any) => {
      let $element = $(element);
      let $class = $element.attr('class').split(' ')[0]
      let $groupId = '';

      if ($class === 'plominoGroupClass') {
        $groupId = $element.attr('data-groupid');
      }
      
      switch($class) {
        case 'plominoGroupClass':
          fields$.push({
            type: 'group',
            url: baseUrl,
            groupId: $groupId,
            el: $element
          });
          break;
        case 'plominoFieldClass':
        case 'plominoActionClass':
          fields$.push({
            type: 'field',
            url: baseUrl,
            el: $element
          });
          break;
        case 'plominoHidewhenClass':
          fields$.push({
            type: 'hidewhen',
            url: baseUrl,
            el: $element
          });
          break;
        case 'plominoLabelClass':
          fields$.push({
            type: 'label',
            url: baseUrl,
            el: $element
          });
          break;
        default:
      }
    });
    return Observable.from(fields$)
              .concatMap((fieldData: any) => {
                
                if (fieldData.type === 'group') {
                  return this.convertFormGroups(fieldData.url, fieldData.el, fieldData.groupId); 
                }

                if (fieldData.type === 'hidewhen') {
                  return this.convertFormHidewhens(fieldData.url, fieldData.el);
                }

                if (fieldData.type === 'label') {
                  return this.convertLabel(fieldData.url, fieldData.el, 'form');
                }

                return this.convertFormFields(fieldData.url, fieldData.el);
              })
              .reduce((formString: any, formItem: any) => {
                return formString += formItem;
              }, '');
  }

  private convertFormGroups(base: string, element: any, groupId: any): Observable<any> {
    let $groupId = element.attr('data-groupid');
    let fields$: any[] = [];

    let $elements = $('<div />')
      .html(element.html())
      .find('.plominoGroupClass, .plominoFieldClass:not(.plominoGroupClass .plominoFieldClass), .plominoHidewhenClass:not(.plominoGroupClass .plominoHidewhenClass), .plominoActionClass:not(.plominoGroupClass .plominoActionClass), .plominoLabelClass:not(.plominoGroupClass .plominoLabelClass)');  

    $elements.each((index: number, element: any) => {
      let $element = $(element);
      let $class = $element.attr('class').split(' ')[0];
      let $groupId = '';

      if ($class === 'plominoGroupClass') {
        $groupId = $element.attr('data-groupid');
      }

      switch($element.attr('class')) {
        case 'plominoGroupClass':
          fields$.push({
            type: 'group',
            url: base,
            groupId: $groupId,
            el: $element
          });
        case 'plominoFieldClass':
        case 'plominoActionClass':
          fields$.push({
            type: 'field',
            url: base,
            el: $element
          });
          break;
        case 'plominoHidewhenClass':
          fields$.push({
            type: 'hidewhen',
            url: base,
            el: $element
          });
          break;
        case 'plominoLabelClass':
          fields$.push({
            url: base,
            type: 'label',
            el: $element
          });
          break;
        default:
      }
    });

    return Observable.from(fields$)
              .concatMap((fieldData: any) => {
                if (fieldData.type === 'group') {
                  return this.convertFormGroups(fieldData.url, fieldData.el, fieldData.groupId); 
                }

                if (fieldData.type === 'hidewhen') {
                  return this.convertFormHidewhens(fieldData.url, fieldData.el);
                }

                if (fieldData.type === 'label') {
                  return this.convertLabel(fieldData.url, fieldData.el, 'group');
                }

                return this.convertFormFields(fieldData.url, fieldData.el);
              })
              .reduce((formString: any, formItem: any) => {
                return formString += formItem;
              }, '')
              .map((groupString) => {
                return this.wrapIntoGroup(groupString, $groupId);
              })
    
  }

  private convertGroupFields(ids: any[], base: string, element: any): Observable<any> {
    let $class = element.attr('class');
    let $type = $class.slice(7, -5).toLowerCase();
    let $id =  this.findId(ids, element.text()).id;
  
    return this.getWidget(base, $type, $id).map((response) => {
      let $response = $(response);
      let container = 'span';
      let content = '';

      if ($response.find("div,table,p").length) {
        container = "div";
      }
      
      if (response !== undefined) {
        content = `<${container} class="${$class} mceNonEditable" data-mce-resize="false" data-plominoid="${$id}">
                      ${response}
                   </${container}><br />`;
      } else {
        content = `<span class="${$class}">${$id}</span><br />`;
      }

      return this.wrapIntoEditable(content);
    });
  }

  private convertGroupHidewhens(ids: any[], base: string, element: any): Observable<any> {
    let $class = element.attr('class');
    let $type = $class.slice(7, -5).toLowerCase();
    let $position = element.text().split(':')[0];
    let $id = element.text().split(':')[1];
    let $newId = this.findId(ids, $id).id;

    let container = 'span';
    let content = `<${container} class="${$class} mceNonEditable" 
                              data-mce-resize="false"
                              data-plomino-position="${$position}" 
                              data-plominoid="${$newId}">
                    &nbsp;
                  </${container}>${ $position === 'start' ? '' : '<br />' }`;
    return Observable.of(this.wrapIntoEditable(content));
  }

  private convertFormFields(base: string, element: any): Observable<any> {
    console.info('convertFormFields', base, element);
    let $class = element.attr('class');
    let $type = $class.slice(7, -5).toLowerCase();
    let $id = element.text();

    return this.getWidget(base, $type, $id).map((response) => {
      let $response = $(response);
      let container = 'span';
      let content = '';
      let $newId: any;

      if ($response.find("div,table,p").length) {
        container = "div";
      }
      
      if (response != undefined) {
        content = `<${container} class="${$class} mceNonEditable" data-mce-resize="false" data-plominoid="${$id}">
                      ${response}
                   </${container}><br />`;
      } else {
        content = `<span class="${$class}">${$id}</span><br />`;
      }

      return content;
    });
  }

  private convertFormHidewhens(base: string, element: any): Observable<any> {
    let $class = element.attr('class');
    let $position = element.text().split(':')[0];
    let $id = element.text().split(':')[1];
  
    let container = 'div';
    let content = `<${container} class="${$class} mceNonEditable" 
                              data-mce-resize="false"
                              data-plomino-position="${$position}" 
                              data-plominoid="${$id}">
                    &nbsp;
                  </${container}>${ $position === 'start' ? '' : '<br />' }`;

    return Observable.of(content);
  }

  private convertLabel(base: string, element: any, type: 'form' | 'group', ids: any[] = []): Observable<any> {
    let $class = element.attr('class').split(' ')[0];
    let $type = $class.slice(7, -5).toLowerCase();
    let $id: any;

    if (ids.length) {
      $id = this.findId(ids, element.text()).id;
    } else {
      $id = element.text();
    }

    return this.getWidget(base, $type, $id)
              .map((response) => {
                if (type === 'group') {
                  return this.wrapIntoEditable(`${response}<br />`);
                } else {
                  return `${response}<br />`;
                } 
              });
  }

  private wrapIntoEditable(content: string): string {
    let $wrapper = $('<span />');
    return $wrapper.html(content)
              .addClass('mceEditable')
              .wrap('<div />')
              .parent()
              .html();
  }

  private wrapIntoGroup(content: string, groupId: string): string {
    let $wrapper = $('<div />');
    return $wrapper.html(content)
              .addClass('plominoGroupClass mceNonEditable')
              .attr('data-groupid', groupId)
              .wrap('<div />')
              .parent()
              .append('<br />')
              .html();
  }

  private findId(newIds: any[], id: any) {
    return _.find(newIds, (newId: any) => {
      return newId.id.indexOf(id) > -1;
    });
  }

  private getWidget(baseUrl: string, type: string, id: string) {
    return this.http.get(`${baseUrl}/@@tinyform/example_widget?widget_type=${type}&id=${id}`)
      .map((response: Response) => response.json());
  }  
}