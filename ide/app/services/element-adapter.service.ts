import { LogService } from './log.service';
import { Injectable } from '@angular/core';

@Injectable()
export class PlominoElementAdapterService {
  /**
   * this service is end-point for each element on the markup
   */
  constructor(private log: LogService) {}

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
}
