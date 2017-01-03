import { Injectable } from '@angular/core';

import 'jquery';
declare let $: any;
import 'lodash';
declare let _: any;

@Injectable()
export class WidgetService {

  getLayout(input: any): any {
    return this.parseInput(input.layout, input.groupid, input.group_contents);
  }

  private parseInput(layout: any, id: any, contents: any[]) {
    let $elements = $('<div />').html(layout)
                      .find('.plominoGroupClass, .plominoFieldClass:not(.plominoGroupClass .plominoFieldClass), .plominoHidewhenClass:not(.plominoGroupClass .plominoHideWhenClass), .plominoActionClass:not(.plominoGroupClass .plominoActionClass)');
    let resultingElementsString = '';
    
    $elements.each((index: number, element: any) => {
      let $element = $(element);
      switch($element.attr('class').split(' ')[0]) {
        case 'plominoGroupClass':
          resultingElementsString += this.convertGroup($element, id, contents);
          break;
        case 'plominoFieldClass':
          resultingElementsString += this.convertField($element, contents);
          break;
        case 'plominoHidewhenClass':
          resultingElementsString += this.convertHidewhen($element, contents);
          break;
        case 'plominoActionClass':
          resultingElementsString += this.convertAction($element, contents);
          break;
        default: 
      };
    });
    
    return this.wrapIntoGroup(resultingElementsString, id);
  }

  private convertGroup(group: any, groupId: any, contents: any[]) {
    let $elements = $('<div />').html(group.html())
                        .find('.plominoGroupClass, .plominoFieldClass:not(.plominoGroupClass .plominoFieldClass), .plominoHidewhenClass:not(.plominoGroupClass .plominoHideWhenClass), .plominoActionClass:not(.plominoGroupClass .plominoActionClass)');
    
    let resultingElementsString = '';

    $elements.each((index: number, element: any) => {
      let $element = $(element);
      switch($element.attr('class').split(' ')[0]) {
        case 'plominoGroupClass':
          resultingElementsString += this.convertGroup($element, groupId, contents);
          break;
        case 'plominoFieldClass':
          resultingElementsString += this.convertField($element, contents);
          break;
        case 'plominoHidewhenClass':
          resultingElementsString += this.convertHidewhen($element, contents);
          break;
        case 'plominoActionClass':
          resultingElementsString += this.convertAction($element, contents);
          break;
        default: 
      };
    });

    return this.wrapIntoGroup(resultingElementsString, groupId);
  }

  private convertHidewhen(element: any, contents: any[]): string { 
    let container = 'span';
    let $content = this.getContent(element);
    let $id = $content.split(':')[1]; 
    let $position = $content.split(':')[0];
    let id = this.findId(contents, $id);
    
    let result = `<${container} class="plominoHidewhenClass" 
                                data-plominoid="${id}"
                                data-plomino-position="${$position}">
      &nbsp;
    </${container}>`;
    
    return this.wrapIntoEditable(result, '<span />');
  }

  private convertField(element: any, contents: any[]): string { 
    let container = 'span';
    let $content = this.getContent(element);
    let id = this.findId(contents, $content);
    
    let result = `<${container} class="plominoFieldClass" data-plominoid="${id}">
        <input value="${id}" />
    </${container}><br />`;
  
    return this.wrapIntoEditable(result);
  }

  private convertAction(element: any, contents: any[]): string {
    let container = 'span';
    let $content = this.getContent(element);
    let id = this.findId(contents, $content);
    
    let result = `<${container} class="plominoActionClass" data-plominoid="${id}">
        <input id="${id}" class="context" name="${id}" value="${id}" type="button">
    </${container}><br />`;
  
    return this.wrapIntoEditable(result);
  }

  // Utils 
  private wrapIntoEditable(content: string, container: string = '<span />') {
    let $container = $(container);
    return $container.addClass('mceEditable')
              .html(content)
              .wrap('<div />')
              .parent()
              .html();
  }

  private wrapIntoGroup(content: any, groupId: string) {
    let group = $('<div />');
    return group.addClass('plominoGroupClass mceNonEditable')
              .attr('data-groupid', groupId)
              .html(content)
              .wrap('<div />')
              .parent()
              .append('<br />')
              .html();
  }

  private getContent(element: any) {
    return element.text().trim();
  }
    
  private findId(options: string[], target: string) {
    return _.find(options, (option: string) => {
      return option.indexOf(target) > -1;
    });
  }  
}