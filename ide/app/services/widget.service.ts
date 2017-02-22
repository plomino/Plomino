import { Subject } from 'rxjs/Rx';
import { Observable } from 'rxjs/Observable';
import { Injectable } from '@angular/core';

import { Http, Response } from '@angular/http';

@Injectable()
export class WidgetService {

  isTemplate: boolean = true;

  widgetsCache: {
    [formUrl: string]: {
      [id: string]: {
        [widget_type: string]: string
      }
    }
  } = {};

  constructor(private http: Http) { }

  getWidgetCacheData(formUrl: string, widgetType: string, id: string): string {
    if (!this.widgetsCache.hasOwnProperty(formUrl)) {
      return null;
    }

    if (!this.widgetsCache[formUrl].hasOwnProperty(id)) {
      return null;
    }

    if (!this.widgetsCache[formUrl][id].hasOwnProperty(widgetType)) {
      return null;
    }

    return this.widgetsCache[formUrl][id][widgetType];
  }

  setWidgetCacheData(formUrl: string, widgetType: string, id: string, data: string) {
    if (!this.widgetsCache.hasOwnProperty(formUrl)) {
      this.widgetsCache[formUrl] = {};
    }
    if (!this.widgetsCache[formUrl].hasOwnProperty(id)) {
      this.widgetsCache[formUrl][id] = {};
    }
    
    this.widgetsCache[formUrl][id][widgetType] = data;
  }

  getGroupLayout(baseUrl: string, input: any, templateMode?: boolean): Observable<any> {
    if (input.title === "template_dummy2")
      console.info('getGroupLayout', input);
    /**
     * decided to use the DOM
     */
    let $groupLayout = $(
      `<div id="tmp-group-layout-id${input.id}" role="group"
        style="visibility: hidden; position: absolute"
        >${input.layout}</div>`
    );

    $('body').append($groupLayout);
    $groupLayout = $(`#tmp-group-layout-id${input.id}`);

    let $elements = $groupLayout
      .find('.plominoFieldClass, .plominoHidewhenClass, ' +
      '.plominoActionClass, .plominoLabelClass');
    let resultingElementsString = '';
    let contents = input.group_contents;
    let items$: any[] = [];

    $elements.each((index: number, element: any) => {
      let $element = $(element);
      let itemPromiseResolve: any;
      const itemPromise = new Promise((resolve, reject) => {
        itemPromiseResolve = resolve;
      });
      
      switch($element.attr('class')) {
        case 'plominoFieldClass':
        case 'plominoActionClass':
          items$.push({
            type: 'field',
            contents: contents,
            baseUrl: baseUrl,
            el: $element,
            templateMode: Boolean(templateMode),
            itemPromise,
            itemPromiseResolve,
          });
          break;
        case 'plominoHidewhenClass':
          items$.push({
            type: 'hidewhen',
            contents: contents,
            baseUrl: baseUrl,
            el: $element,
            templateMode: Boolean(templateMode),
            itemPromise,
            itemPromiseResolve,
          });
          break;
        case 'plominoLabelClass':
          items$.push({
            type: 'label',
            contents: contents,
            baseUrl: baseUrl,
            el: $element,
            templateMode: Boolean(templateMode),
            itemPromise,
            itemPromiseResolve,
          });
          break;
        default:
      }
    });

    items$.forEach((item: any) => {

      ({
        field: (item: any) => 
          this.convertGroupFields(
            item.contents, item.baseUrl, item.el
          ),
        hidewhen: (item: any) => 
          this.convertGroupHidewhens(
            item.contents, item.baseUrl, item.el
          ),
        label: (item: any) => 
          this.convertLabel(
            item.baseUrl, item.el, 'group', item.contents
          ),
      }[item.type])(item)
      .subscribe((result: string) => {
        item.el.replaceWith($(result));

        $groupLayout
        .find('p > span.mceEditable > .plominoLabelClass').each((i, lElement) => {
          let $tmpLabel = $(lElement);
          if ($tmpLabel.next().length && $tmpLabel.next().prop('tagName') === 'BR') {
            let $parentPTag = $tmpLabel.parent().parent();
            $parentPTag.replaceWith($parentPTag.html());
          }
        });
        
        item.itemPromiseResolve(result);
      });
    });
    
    return Observable.from(items$)
    .map((item$) => {
      return Observable.fromPromise(item$.itemPromise);
    })
    .concatAll()
    .concatMap((result: string) => result)
    .reduce((formString: any, formItem: any) => {
      return formString += formItem;
    }, '')
    .map((formString: any) => {
      if ($groupLayout.children().last().length && 
      $groupLayout.children().last().prop('tagName') === 'P' && 
      $groupLayout.children().last().html().trim().length === 0) {
        $groupLayout.children().last().remove();
      }

      const $wrongLabels = $groupLayout
      .find('span.mceEditable > span.mceEditable > .plominoLabelClass');
      
      $wrongLabels.each((i, wLabelElement) => {
        const $label = $(wLabelElement);
        $label.parent().parent().replaceWith($label.parent());
      });
      
      const result = $groupLayout.html();
      $groupLayout.remove();
      return this.wrapIntoGroup(result, input.groupid);
    });
  }

  loadAndParseTemplatesLayout(baseUrl: string, template: PlominoFormGroupTemplate) {
    return this.getGroupLayout(baseUrl, template, true);
  }

  getFormLayout(baseUrl: string) {

    const $edIFrame = $(`iframe[id="${ baseUrl }_ifr"]`).contents();
    console.info('IFRAME LOADED', $edIFrame.find('#tinymce').html());
    $edIFrame.css('opacity', 0);
    let $elements = $edIFrame.find('.plominoGroupClass, ' +
      '.plominoFieldClass:not(.plominoGroupClass .plominoFieldClass), ' +
      '.plominoHidewhenClass:not(.plominoGroupClass .plominoHidewhenClass), ' +
      '.plominoActionClass:not(.plominoGroupClass .plominoActionClass),' +
      ' .plominoLabelClass:not(.plominoGroupClass .plominoLabelClass)');

    const context = this;
    let promiseList: any[] = [];

    const widgetQueryData: { widget_type: string, id: string }[] = [];

    const $widgets = $edIFrame.find(
      '.plominoFieldClass, .plominoHidewhenClass, ' +
      '.plominoActionClass, .plominoLabelClass'
    );

    $widgets.each(function () {
      const $widget = $(this);
      if ($widget.hasClass('mceNonEditable')) {
        return true;
      }

      const id = $widget.text();
      const widget_type = $widget.attr('class').split(' ')[0]
        .replace('plomino', '').replace('Class', '').toLowerCase();

      widgetQueryData.push({ widget_type, id });
    });

    const widgetsFromServer = new Subject<any>();
    const widgetsObservable$: Observable<any> = widgetsFromServer.asObservable();

    $elements.each(function () {
      let $element = $(this);
      let $class = $element.attr('class').split(' ')[0];
      let $groupId = '';

      if ($class === 'plominoGroupClass') {
        $groupId = $element.attr('data-groupid');
        console.info('plominoGroupClass');
        promiseList.push(new Promise((resolve, reject) => {
          widgetsObservable$
          .subscribe((() => {
            context.convertFormGroups(baseUrl, $element, $groupId)
            .subscribe((result: any) => {
              $element.replaceWith(result);
              resolve();
            });
          }));
        }));
      }
      else if ($class === 'plominoFieldClass' ||
               $class === 'plominoActionClass') {
        promiseList.push(new Promise((resolve, reject) => {
           widgetsObservable$
          .subscribe((() => {
            context.convertFormFields(baseUrl, $element)
            .subscribe((result: any) => {
              $element.replaceWith(result);
              resolve();
            });
          }));
        }));
      }
      else if ($class === 'plominoHidewhenClass') {
        promiseList.push(new Promise((resolve, reject) => {
          widgetsObservable$
          .subscribe((() => {
            context.convertFormHidewhens(baseUrl, $element)
            .subscribe((result: any) => {
              $element.replaceWith(result);
              resolve();
            });
          }));
        }));
      }
      else if ($class === 'plominoLabelClass') {
        promiseList.push(new Promise((resolve, reject) => {
          widgetsObservable$
          .subscribe((() => {
            context.convertLabel(baseUrl, $element, 'form')
            .subscribe((result: any) => {
              $element.replaceWith(result);
              resolve();
            });
          }));
        }));
      }
      
    });

    if (widgetQueryData.length) {
      this.http.get(
        `${baseUrl}/@@tinyform/example_widget?widgets=${JSON.stringify(widgetQueryData)}`
      )
      .subscribe((response: Response) => {
        response.json().forEach((result: any) => {
          this.setWidgetCacheData(
            baseUrl, result.widget_type, result.id, result.html
          );
        });
        widgetsFromServer.next('loaded succeed');
      });
    }
    else {
      widgetsFromServer.next('blank form');
    }

    return promiseList;
  }

  private convertFormGroups(base: string, element: any, groupId: any): Observable<any> {
    console.info('convertFormGroups element', element);
    let $groupId = element.attr('data-groupid');
    let fields$: any[] = [];

    let $elements = $('<div />')
      .html(element.html())
      .find('.plominoGroupClass, ' + 
      '.plominoFieldClass:not(.plominoGroupClass .plominoFieldClass), ' + 
      '.plominoHidewhenClass:not(.plominoGroupClass .plominoHidewhenClass), ' + 
      '.plominoActionClass:not(.plominoGroupClass .plominoActionClass), ' + 
      '.plominoLabelClass:not(.plominoGroupClass .plominoLabelClass)');  

    

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

    const $idData = this.findId(ids, element.text());
    let $id = $idData.id;
    let template: PlominoFormGroupContent = null;

    if ($idData && $idData.layout) {
      template = $idData;
    }
  
    return (template 
      ? this.getWidget(base, $type, $id, template) 
      : this.getWidget(base, $type, $id)
      ).map((response: any) => {
      let $response = $(response);
      let container = 'span';
      let content = '';

      if ($response.find("div,table,p").length) {
        container = "div";
      }
      
      if (response !== undefined) {
        content = `<${container} data-present-method="convertGroupFields_1"
                  class="${$class} mceNonEditable" data-mce-resize="false"
                  data-plominoid="${$id}">
                      ${response}
                   </${container}>`;
      } else {
        content = `<span data-present-method="convertGroupFields_2" class="${$class}">${$id}</span>`;
      }

      return template ? content : this.wrapIntoEditable(content);
    });
  }

  private convertGroupHidewhens(ids: any[], base: string, element: any,
  template?: PlominoFormGroupTemplate): Observable<any> {
    let $class = element.attr('class');
    let $type = $class.slice(7, -5).toLowerCase();
    let $position = element.text().split(':')[0];
    let $id = element.text().split(':')[1];
    let $newId = this.findId(ids, $id).id;

    let container = 'span';
    let content = `<${container} class="${$class} mceNonEditable" 
                              data-present-method="convertGroupHidewhens"
                              data-mce-resize="false"
                              data-plomino-position="${$position}" 
                              data-plominoid="${$newId}">
                    &nbsp;
                  </${container}>`;
    return Observable.of(this.wrapIntoEditable(content));
  }

  private convertFormFields(base: string, element: any): Observable<any> {
    let $class = element.attr('class');
    let $type = $class.slice(7, -5).toLowerCase();
    let $id = element.text();
    let template: PlominoFormGroupContent = null;

    return (template 
      ? this.getWidget(base, $type, $id, template) 
      : this.getWidget(base, $type, $id)
      ).map((response: any) => {
      let $response = $(response);
      let container = 'span';
      let content = '';
      let $newId: any;

      if ($response.find("div,table,p").length) {
        container = "div";
      }
      
      if (response != undefined) {
        content = `<${container} data-present-method="convertFormFields_1" 
                    class="${$class} mceNonEditable" data-mce-resize="false"
                    contenteditable="false"
                    data-plominoid="${$id}">
                      ${response}
                   </${container}>`;
      } else {
        content = `<span data-present-method="convertFormFields_2" class="${$class}">${$id}</span>`;
      }

      return content;
    });
  }

  private convertFormHidewhens(base: string, element: any,
  template?: PlominoFormGroupTemplate): Observable<any> {
    let $class = element.attr('class');
    let $position = element.text().split(':')[0];
    let $id = element.text().split(':')[1];
  
    let container = 'span';
    let content = `<${container} class="${$class} mceNonEditable" 
                              data-mce-resize="false"
                              data-present-method="convertFormHidewhens"
                              data-plomino-position="${$position}" 
                              data-plominoid="${$id}">
                    &nbsp;
                  </${container}>`;
    
    return Observable.of(content);
  }

  private convertLabel(base: string, element: any, type: 'form' | 'group', ids: any[] = []): Observable<any> {
    let $class = element.attr('class').split(' ')[0];
    let $type = $class.slice(7, -5).toLowerCase();

    let $id: any = null;
    let template: PlominoFormGroupContent = null;

    if (ids.length) {
      const $idData = this.findId(ids, element.text());
      $id = $idData.id;

      if ($idData && $idData.layout) {
        template = $idData;
      }
    } else {
      $id = element.text();
    }

    return (template 
    ? this.getWidget(base, $type, $id, template) 
    : this.getWidget(base, $type, $id)
    ).map((response) => {
      const $response = $(response);
      if ($response.length === 1 && $response.prop('tagName') === 'P') {
        response = $response.html();
      }
      let result = '';
      if (type === 'group') {
        result = this.wrapIntoEditable(`${response}<br />`);
      } else {
        result = `${response}<br />`;
      }
      return result;
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
    // console.info('wrap', content, groupId);
    let $wrapper = $('<div />');
    return $wrapper.html(content)
              .addClass('plominoGroupClass mceNonEditable')
              .attr('data-groupid', groupId)
              // .attr('contenteditable', 'false')
              .wrap('<div />')
              .parent()
              // .append('<br />')
              .html();
  }

  private findId(newIds: any[], id: any) {
    return _.find(newIds, (newId: any) => {
      return newId.id.indexOf(id) > -1;
    });
  }

  private getWidget(baseUrl: string, type: string, id: string, 
  content?: PlominoFormGroupContent) {
    // console.info('getWidget type', type, 'id', id, 'content', content);
    if (content && type === 'label') {
      return Observable.of(
        `<span class="plominoLabelClass mceNonEditable">${ content.title }</span>`
      );
    }
    if (content && type === 'field') {
      return Observable.of(content.layout);
    }

    const cachedResult = this.getWidgetCacheData(baseUrl, type, id);
    if (cachedResult) {
      return Observable.of(cachedResult);
    }

    return this.http.get(`${baseUrl}/@@tinyform/example_widget?widget_type=${type}&id=${id}`)
      .map((response: Response) => {
        const result = response.json();
        this.setWidgetCacheData(baseUrl, type, id, result);
        return result;
      });
  }  
}
