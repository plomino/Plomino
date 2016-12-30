import { Injectable } from '@angular/core';

import 'jquery';
declare let $: any;

@Injectable()
export class WidgetService {
  groupId: string = null;

  getLayout(input: any): any {
    console.info(`Input data in widget service`, input);
    console.info(this.wrappIntoGroup(input.layout, input.groupid));
  }

  private getExampleWidget(widgetType: string, id: string): any {
  
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
}