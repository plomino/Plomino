import { Injectable } from '@angular/core';

import 'jquery';
declare let $: any;
import 'lodash';
declare let _: any;

@Injectable()
export class WidgetService {

  exractedGroups: string = '';

  getLayout(input: any): any {
    return this.parseInput(input);
  }

  private parseInput(input: any) {
    let $elements = $('<div />').html(input.layout)
                      .find('.plominoGroupClass, .plominoFieldClass:not(.plominoGroupClass .plominoFieldClass), .plominoHidewhenClass:not(.plominoGroupClass .plominoHideWhenClass), .plominoActionClass:not(.plominoGroupClass .plominoActionClass)');
    let resultingElementsString = '';
    
    $elements.each((index: number, element: any) => {
      let $element = $(element);
      switch($element.attr('class').split(' ')[0]) {
        case 'plominoGroupClass':
          this.extractGroup($element, input.group_contents).then((result: string) => {
            resultingElementsString += result;
          });
          break;
        case 'plominoFieldClass':
          resultingElementsString += this.convertField($element, input.group_contents);
          break;
        case 'plominoHidewhenClass':
          resultingElementsString += this.convertHidewhen($element, input.group_contents);
          break;
        case 'plominoActionClass':
          resultingElementsString += this.convertAction($element, input.group_contents);
          break;
        default: 
      };
    });
    
    return this.wrapIntoGroup(resultingElementsString, input.groupId);
  }

  private extractGroup(element: any, contents: any[]) {
    return new Promise((resolve) => {
      this.convertGroup(element, contents);
      resolve(this.exractedGroups);
    })
  }

  private convertGroup(element: any, contents: any[]) {
    let $group = element.find('.plominoGroupClass');
    if ($group.length) {
      this.convertGroup($group, contents);
    }
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