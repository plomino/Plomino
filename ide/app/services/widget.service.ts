import { LabelsRegistryService } from './../editors/tiny-mce/services/labels-registry.service';
import { PlominoElementAdapterService } from './element-adapter.service';
import { LogService } from './log.service';
import { PlominoHTTPAPIService } from './http-api.service';
import { Subject, Observable } from 'rxjs/Rx';
import { Injectable } from '@angular/core';
import { Response } from '@angular/http';

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

  constructor(private http: PlominoHTTPAPIService,
  private adapter: PlominoElementAdapterService,
  private labelsRegistry: LabelsRegistryService,
  private log: LogService) { }

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

  getGroupLayout(
    baseUrl: string, input: PlominoFormGroupTemplate, templateMode?: boolean
  ): Observable<string> {
    // this.log.info('input', JSON.stringify(input));
    // this.log.extra('widget.service.ts getGroupLayout');
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
      '.plominoActionClass, .plominoLabelClass, .plominoSubformClass');
    let resultingElementsString = '';
    let contents = input.group_contents;
    let items$: PlominoIteratingLayoutElement[] = [];

    $elements.each((index: number, element: HTMLElement) => {
      let $element = $(element);
      let itemPromiseResolve: (value?: {} | PromiseLike<{}>) => void;
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
        case 'plominoSubformClass':
          items$.push({
            baseUrl: baseUrl,
            type: 'subform',
            el: $element,
            templateMode: Boolean(templateMode),
            itemPromise,
            itemPromiseResolve,
          });
          break;
        default:
      }
    });

    items$.forEach((item: PlominoIteratingLayoutElement) => {

      ({
        field: (item: PlominoIteratingLayoutElement) => 
          this.convertGroupFields(
            item.contents, item.baseUrl, item.el
          ),
        hidewhen: (item: PlominoIteratingLayoutElement) => 
          this.convertGroupHidewhens(
            item.contents, item.baseUrl, item.el
          ),
        label: (item: PlominoIteratingLayoutElement) => 
          this.convertLabel(
            item.baseUrl, item.el, 'group', item.contents
          ),
        subform: (item: PlominoIteratingLayoutElement) => 
          this.convertFormSubform(
            item.baseUrl, item.el
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
    .reduce((formString: string, formItem: string) => {
      return formString += formItem;
    }, '')
    .map((formString: string) => {
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
    // this.log.info('getFormLayout called', baseUrl);
    const $edIFrame = $(`iframe[id="${ baseUrl }_ifr"]`).contents();
    $edIFrame.css('opacity', 0);
    let $elements = $edIFrame.find('.plominoGroupClass, .plominoSubformClass, ' +
      '.plominoFieldClass:not(.plominoGroupClass .plominoFieldClass), ' +
      '.plominoHidewhenClass:not(.plominoGroupClass .plominoHidewhenClass), ' +
      '.plominoActionClass:not(.plominoGroupClass .plominoActionClass),' +
      ' .plominoLabelClass:not(.plominoGroupClass .plominoLabelClass)');

    const context = this;
    let promiseList: any[] = [];

    const widgetQueryData: { widget_type: string, id: string }[] = [];

    const $widgets = $edIFrame.find(
      '.plominoFieldClass, .plominoHidewhenClass, ' +
      '.plominoActionClass, .plominoSubformClass'
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
    const labelsRegistry = this.labelsRegistry.getRegistry();

    $elements.each(function () {
      let $element = $(this);
      let $class = $element.attr('class').split(' ')[0];
      let $groupId = '';

      if ($class === 'plominoGroupClass') {
        $groupId = $element.attr('data-groupid');
        promiseList.push(new Promise((resolve, reject) => {
          widgetsObservable$
          .subscribe((() => {
            context.convertFormGroups(baseUrl, $element, $groupId, labelsRegistry)
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
      else if ($class === 'plominoSubformClass') {
        promiseList.push(new Promise((resolve, reject) => {
           widgetsObservable$
          .subscribe((() => {
            context.convertFormSubform(baseUrl, $element)
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
            context.convertLabel(baseUrl, $element, 'form', [], labelsRegistry)
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
        `${baseUrl}/@@tinyform/example_widget?widgets=${JSON.stringify(widgetQueryData)}`,
        'widget.service.ts getFormLayout'
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

  private convertFormGroups(
    base: string, element: any, groupId: any, labelsRegistry?: Map<string, Object>
  ): Observable<any> {
    let $groupId = element.attr('data-groupid');
    let fields$: any[] = [];

    const randomId = Math.floor(Math.random() * 1e5) + 1e4 + 1;

    /**
     * decided to use the DOM
     */
    let $groupLayout = $(
      `<div id="tmp-cgroup-layout-id${randomId}" role="group"
        style="visibility: hidden; position: absolute"
        >${element.html()}</div>`
    );

    $('body').append($groupLayout);
    $groupLayout = $(`#tmp-cgroup-layout-id${randomId}`);

    let $elements = $groupLayout
      .find('.plominoGroupClass, .plominoSubformClass, ' + 
      '.plominoFieldClass:not(.plominoGroupClass .plominoFieldClass), ' + 
      '.plominoHidewhenClass:not(.plominoGroupClass .plominoHidewhenClass), ' + 
      '.plominoActionClass:not(.plominoGroupClass .plominoActionClass), ' + 
      '.plominoLabelClass:not(.plominoGroupClass .plominoLabelClass)');

    $elements.each((index: number, element: any) => {
      let $element = $(element);
      let itemPromiseResolve: any;
      const itemPromise = new Promise((resolve, reject) => {
        itemPromiseResolve = resolve;
      });
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
            el: $element,
            itemPromise,
            itemPromiseResolve,
          });
        case 'plominoFieldClass':
        case 'plominoActionClass':
          fields$.push({
            type: 'field',
            url: base,
            el: $element,
            itemPromise,
            itemPromiseResolve,
          });
          break;
        case 'plominoHidewhenClass':
          fields$.push({
            type: 'hidewhen',
            url: base,
            el: $element,
            itemPromise,
            itemPromiseResolve,
          });
          break;
        case 'plominoLabelClass':
          fields$.push({
            url: base,
            type: 'label',
            el: $element,
            itemPromise,
            itemPromiseResolve,
          });
          break;
        case 'plominoSubformClass':
          fields$.push({
            url: base,
            type: 'subform',
            el: $element,
            itemPromise,
            itemPromiseResolve,
          });
          break;
        default:
      }
    });

    fields$.forEach((item: any) => {

      ({
        group: (item: any) => 
          this.convertFormGroups(
            item.url, item.el, item.groupId, labelsRegistry
          ),
        field: (item: any) => 
          this.convertFormFields(
            item.url, item.el
          ),
        hidewhen: (item: any) => 
          this.convertFormHidewhens(
            item.url, item.el
          ),
        label: (item: any) => 
          this.convertLabel(
            item.url, item.el, 'group', [], labelsRegistry
          ),
        subform: (item: any) => 
          this.convertFormSubform(
            item.url, item.el
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

    return Observable.from(fields$)
    .map((item$) => {
      return Observable.fromPromise(item$.itemPromise);
    })
    .concatAll()
    .concatMap((result: string) => result)
    .reduce((formString: any, formItem: any) => {
      return formString += formItem;
    }, '')
    .map((groupString) => {
      const $wrongLabels = $groupLayout
      .find('span.mceEditable > span.mceEditable > .plominoLabelClass');
      
      $wrongLabels.each((i, wLabelElement) => {
        const $label = $(wLabelElement);
        $label.parent().parent().replaceWith($label.parent());
      });
      
      const result = $groupLayout.html();
      $groupLayout.remove();
      return this.wrapIntoGroup(result, $groupId);
    });
    
  }

  private convertGroupFields(
    ids: PlominoFormGroupContent[], base: string, element: JQuery
  ): Observable<string> {
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
      ).map((response) => {
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

  private convertGroupHidewhens(
    ids: PlominoFormGroupContent[], base: string, element: JQuery,
    template?: PlominoFormGroupTemplate): Observable<string> {
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

  private convertFormFields(base: string, element: any): Observable<string> {
    let $class = element.attr('class');
    let $type = $class.slice(7, -5).toLowerCase();
    let $id = element.text();
    let template: PlominoFormGroupContent = null;

    return (template 
      ? this.getWidget(base, $type, $id, template) 
      : this.getWidget(base, $type, $id)
      ).map((response) => {
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
  template?: PlominoFormGroupTemplate): Observable<string> {
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

  private convertFormSubform(base: string, element: JQuery): Observable<string> {
    let $class = element.attr('class');
    let $id = element.text();

    return this.getWidget(
      base, 'subform',
      $id === 'Subform' ? null : $id
    )
    .map((response) => {
      let $response = $(response);
      if ($response.length > 1) {
        $response = $(`<div>${response}</div>`);
      }
      return $response.addClass('mceNonEditable')
        .addClass($class).attr('data-plominoid', $id).get(0).outerHTML;
    });
  }

  private convertLabel(
    base: string, element: JQuery, 
    type: 'form' | 'group', ids: PlominoFormGroupContent[] = [],
    labelsRegistry?: Map<string, Object>
  ): Observable<string> {
    let $class = element.attr('class').split(' ')[0];
    let $type = $class.slice(7, -5).toLowerCase();

    if (element.parent().attr('contenteditable') !== 'false') {
      element.parent().attr('contenteditable', 'false');
    }

    let $id: string = null;
    let template: PlominoFormGroupContent = null;

    let tmpId = element.html();
    const hasAdvancedTitle = tmpId.indexOf(':') !== -1;

    if (hasAdvancedTitle) {
      tmpId = tmpId.split(':')[0];
    }

    if (ids.length) {
      const $idData = this.findId(ids, tmpId);
      $id = $idData.id;

      if ($idData && $idData.layout) {
        template = $idData;
      }
    } else {
      $id = tmpId;
    }

    // this.log.info('convertLabel', $class, $id, `${ base }/${ $id }`, 
    //   labelsRegistry ? labelsRegistry.get(`${ base }/${ $id }`) : null, template);
    // this.log.extra('widget.service.ts convertLabel');

    if (!template && labelsRegistry && labelsRegistry.has(`${ base }/${ $id }`)) {
      template = { id: $id, title: labelsRegistry.get(`${ base }/${ $id }`)['title'] };
      // labelsRegistry.delete(`${ base }/${ $id }`); // just in case
    }

    if (template && hasAdvancedTitle) {
      template.title = element.html();
    }

    return (template 
    ? this.getWidget(base, $type, $id, template) 
    : this.getWidget(base, $type, $id)
    ).map((response) => {
      const $response = $(response);
      const result = (type === 'group') ? $response.get(0).outerHTML : `${response}`;
      return this.adapter.endPoint('label', result);
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

  private findId(newIds: PlominoFormGroupContent[], id: string) {
    return _.find(newIds, (newId: PlominoFormGroupContent) => {
      return newId.id.indexOf(id) > -1;
    });
  }

  private getWidget(baseUrl: string, type: string, id: string, 
  content?: PlominoFormGroupContent): Observable<string> {
    // this.log.info('type', type, 'id', id, 'content', content);
    // this.log.extra('widget.service.ts getWidget');
    if (content && type === 'label') {
      const splitTitle = content.title.split(':');
      if (splitTitle.length === 2) {
        content.title = splitTitle[1];
      }
      return Observable.of(
        `<span class="plominoLabelClass mceNonEditable"
          ${ splitTitle.length === 2 ? ` data-advanced="1"` : '' }
          ${ id ? ` data-plominoid="${ id }"` : '' }>${ content.title }</span>`
      );
    }
    const splitId = id ? id.split(':') : [];
    if (!content && id && type === 'label' && splitId.length === 2) {
      return Observable.of(
        `<span class="plominoLabelClass mceNonEditable"
          data-advanced="1"
          data-plominoid="${ splitId[0] }">${ splitId[1] }</span>`
      );
    }
    if (content && type === 'field') {
      return Observable.of(content.layout);
    }

    const cachedResult = this.getWidgetCacheData(baseUrl, type, id);
    if (cachedResult) {
      return Observable.of(cachedResult);
    }

    return this.http.get(
      `${baseUrl}/@@tinyform/example_widget?widget_type=${type}${ id ? `&id=${id}` : '' }`,
      'widget.service.ts getWidget'
      )
      .map((response: Response) => {
        const result = response.json();
        this.setWidgetCacheData(baseUrl, type, id, result);
        return result;
      });
  }  
}
