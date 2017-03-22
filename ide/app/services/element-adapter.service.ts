import { LabelsRegistryService } from './../editors/tiny-mce/services/labels-registry.service';
import { LogService } from './log.service';
import { Injectable } from '@angular/core';

@Injectable()
export class PlominoElementAdapterService {
  private $previousSelectedElement: JQuery;
  private $latestSelectedElement: JQuery;
  private $latestSelectedPosition: JQuery;

  /**
   * this service is end-point for each element on the markup
   */
  constructor(private log: LogService, 
  private labelsRegistry: LabelsRegistryService) {}

  endPoint(type: string, source: string) {
    // this.log.info('endPoint', type, source);
    if (type === 'label') {
      const $source = $(source);
      /**
       * make labels editable
       */
      source = $source.removeClass('mceNonEditable').get(0).outerHTML;

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

  /**
   * difference with the select is that position not exactly selected element like field
   */
  selectPosition($position: JQuery) {
    this.$latestSelectedPosition = $position;
  }

  select($element: JQuery) {
    this.$previousSelectedElement = this.$latestSelectedElement;
    this.$latestSelectedElement = $element;

    this.log.info('selected', this.$latestSelectedElement);
    this.log.info('after', this.$previousSelectedElement);
    this.log.extra('element-adapter.service.ts select');

    /** blur */
    $('iframe:visible').contents()
      .find('.plominoLabelClass')
      .filter((i, element) => element !== $element.get(0))
      .removeClass('mceEditable')
      .removeAttr('contenteditable')
      // .attr('contenteditable', 'false')
      // .addClass('mceNonEditable');
  
    /**
     * if $element is label - make it listen to input event
     */
    if ($element.hasClass('plominoLabelClass')) {
      $('iframe:visible').contents()
        .find('.plominoLabelClass').off('.adapter');

      $element
        .one('dblclick.adapter', () => {
          $element
            .removeClass('mceNonEditable')
            .attr('contenteditable', 'true')
            .addClass('mceEditable');
        });

      this.log.info('element input.adapter event attached', $element.get(0));
      $element.on('input.adapter', ($event) => {
        this.log.info('input.adapter', $element.html());
        const labelAdvanced = Boolean($element.attr('data-advanced'));

        if (!labelAdvanced) {
          const selectedId = $element.attr('data-plominoid');
          const temporaryTitle = 
            $element.html().replace(/&nbsp;/g, ' ')
              .replace(/^(.+?)?<br>$/, '$1')
              .replace(/\s+/g, ' ').trim();
          this.labelsRegistry.update(
            `${ tinymce.activeEditor.id }/${ selectedId }`,
            temporaryTitle, 'temporary_title'
          );

          const $allTheSame = $('iframe:visible').contents()
            .find(`.plominoLabelClass[data-plominoid="${ selectedId }"]`)
            .filter((i, element) => element !== $element.get(0) 
              && !Boolean($(element).attr('data-advanced')));

          $allTheSame.html(temporaryTitle);
        }
      });
    }

    /**
     * if it was the label before - turn field title to unsaved state
     */
    // const $before = this.$previousSelectedElement;
    // if ($before && $before.hasClass('plominoLabelClass')
    //   && !Boolean($before.attr('data-advanced'))
    // ) {
    //   const fieldId = `${ tinymce.activeEditor.id }/${ $before.attr('data-plominoid') }`;
    //   const fieldTitle = this.labelsRegistry.get(fieldId) || 'Untitled';
    //   $before.html(fieldTitle);
    // }
  }

  getSelectedBefore() {
    return this.$previousSelectedElement;
  }

  getSelected() {
    return this.$latestSelectedElement;
  }

  getSelectedPosition() {
    return this.$latestSelectedPosition;
  }
}
