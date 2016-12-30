import { Injectable } from '@angular/core';

import 'jquery';
declare let $: any;

@Injectable()
export class WidgetService {
  groupId: string = null;

  getLayout(input: any): any {
    console.info(`Input data in widget service`, input, input.groupid);
    this.parseInput(input.layout, input.groupid);
    console.info(this.wrappIntoGroup(input.layout, input.groupid));
  }

  private getExampleWidget(type: string, id: string): any {
    let field: any;
    let action: any;
    let hidewhen: any;
    
    if (!id) {
      return;
    }
    
    switch(type) {
      case 'field':
        break;
      case 'subform':
        break;
      case 'action':
        break;
      case 'label':
        break;
      default:
    }
  }

  private wrappIntoGroup(content: string, groupId: string) {
    let group = $('<div></div>');
    return group.addClass('plominoGroupClass mceNonEditable')
              .attr('data-groupid', groupId)
              .html(content)
              .wrap('<div />')
              .parent()
              .unwrap()
              .html();
  }

  // Utils
  private parseInput(inputString: string, groupId: string) {
    let query = '.plominoActionClass,.plominoSubformClass,.plominoFieldClass';
    let foundElements = $(inputString).find(query)
    foundElements.each((index: number, element: any) => {
      let $elem = $(element);
      let type = $elem.attr('class').split(' ')[0].slice(7, -5).toLowerCase();
      let id = $elem.text();
      let sample = this.getExampleWidget(type, id);
      let $sample = $(sample);
      let elemClass = $sample.attr('class');
      let blocks = 'p,div,table,ul,li';
      let tag: string;
      let html: string;

      if ($sample.hasClass('plominoSubformClass') || 
          $sample.find(blocks) ||
          $sample.filter(blocks)) {
        tag = 'div';  
      } else {
        tag = 'span';
      }
      html = `<${tag} class="${elemClass} mceNonEditable"
                      data-plominoid="${groupId + '_' + id}">
                ${sample}
              </${tag}>`;
      $elem.replaceWith(html)
          .wrap('<span />')
          .parent()
          .addClass('mceEditable');
    });

    query = '.plominoLabelClass';
    foundElements = $(inputString).find(query);
    foundElements.each((index: number, element: any) => {
      let $elem = $(element);
      if ($elem.text()) {
        let id = $elem.text;
        let html = this.getExampleWidget('label', id);
        $elem.replaceWith(html)
          .wrap('<span />')
          .parent()
          .addClass('mceEditable');
      } 
    });

    query = '.plominoHidewhenClass,.plominoCacheClass';
    foundElements = $(inputString).find(query);
    foundElements.each((index: number, element: any) => {
      let $elem = $(element);
      let type = $elem.attr('class').slice(7, -5).toLowerCase();
      if ($elem.text().indexOf(':') > -1) {
        let pos = $elem.text().split(':')[1];
        let id = $elem.text().split(':')[1];
        $($elem).html('&nbsp;')
          .addClass('mceNonEditable')
          .attr('data-plomino-position', pos)
          .attr('data-plominoid', id)
          .wrap('<span />')
          .parent()
          .addClass('mceEditable');
      }
    });

    console.log(inputString);
  }
}