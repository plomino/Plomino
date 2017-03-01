import { LabelsRegistryService } from './../editors/tiny-mce/services/labels-registry.service';
import { LogService } from './log.service';
import { Injectable } from '@angular/core';

@Injectable()
export class PlominoElementAdapterService {
  private $previousSelectedElement: JQuery;
  private $latestSelectedElement: JQuery;

  /**
   * this service is end-point for each element on the markup
   */
  constructor(private log: LogService, 
  private labelsRegistry: LabelsRegistryService) {}

  endPoint(type: string, source: string) {
    this.log.info('endPoint', type, source);
    if (type === 'label') {
      const $source = $(source);
      /**
       * make labels editable
       */
      source = $source.removeClass('mceNonEditable')
        .addClass('mceEditable').get(0).outerHTML;

      /**
       * <span class="plominoLabelClass mceNonEditable" 
          data-mce-resize="false" 
          data-plominoid="text_1_2_3_4_5_6_7">
          <span class="plominoLabelClass mceEditable"
          data-plominoid="text_1_2_3_4_5_6_7">Untitled9</span>    
        </span>
       */
      if ($source.find('.plominoLabelClass').length) {
        // do something
      }
    }
    return source;
  }

  select($element: JQuery) {
    this.$previousSelectedElement = this.$latestSelectedElement;
    this.$latestSelectedElement = $element;

    this.log.info('selected', this.$latestSelectedElement);
    this.log.info('after', this.$previousSelectedElement);
    this.log.extra('element-adapter.service.ts select');

    /**
     * if $element is label - make it listen to input event
     */
    if ($element.hasClass('plominoLabelClass')) {
      $('iframe:visible').contents().find('.plominoLabelClass').off('input.adapter');
      $element.on('input.adapter', ($event) => {
        const labelAdvanced = Boolean($element.attr('data-advanced'));
        // do nothing at this moment
        this.log.info(labelAdvanced);
      });
    }

    /**
     * if it was the label before - turn field title to unsaved state
     */
    const $before = this.$previousSelectedElement;
    if ($before && $before.hasClass('plominoLabelClass')
      && !Boolean($before.attr('data-advanced'))
    ) {
      const fieldId = `${ tinymce.activeEditor.id }/${ $before.attr('data-plominoid') }`;
      const fieldTitle = this.labelsRegistry.get(fieldId) || 'Untitled';
      $before.html(fieldTitle);
    }
  }

  getSelectedBefore() {
    return this.$previousSelectedElement;
  }

  getSelected() {
    return this.$latestSelectedElement;
  }
}
