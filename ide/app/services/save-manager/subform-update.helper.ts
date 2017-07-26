import { Observable } from 'rxjs/Rx';

export function updateRelatedSubformsAfterFormSave(saveProcess: any) {
  if (!saveProcess.isWorking()) { return Observable.of(true); }
  return Observable.of(true).flatMap(() => {
    const updates$: Observable<boolean>[] = [];

    tinymce.editors.forEach((editor: TinyMceEditor) => {
      /**
       * update all subforms while parent form changed
       */
      if (editor === null) {
        return true;
      }
      
      let edBody: any;

      try {
        edBody = editor.getBody();
      }
      catch (e) {
        return true;
      }
      $(edBody).find(
        `.plominoSubformClass[data-plominoid="${ saveProcess.originalFormID }"]`
      ).each((i, subformElement) => {
        const $founded = $(subformElement);
        let updatedSubformURL = `${ 
          window.location.pathname
          .replace('++resource++Products.CMFPlomino/ide/', '')
          .replace('/index.html', '')
        }/${ editor.id }`;
        updatedSubformURL += '/@@tinyform/example_widget?widget_type=subform&id=';
        updatedSubformURL += saveProcess.nextFormID;
        
        updates$.push(saveProcess.http.get(updatedSubformURL)
          .map((response: Response) => {
            return saveProcess.widgetService.getGroupLayout(editor.id, {
              id: Math.floor(Math.random() * 1e10 + 1e10).toString(),
              layout: response.json()
            })
            .map((result: string) => {
              try {
                const $result = $(result);
                $result.find('input,textarea,button')
                  .removeAttr('name').removeAttr('id');
                $result.find('span')
                  .removeAttr('data-plominoid').removeAttr('data-mce-resize');
                $result.removeAttr('data-groupid');
                $result.find('div').removeAttr('data-groupid');
                const subformHTML = $($result.html()).html();
                $founded.html(subformHTML);
                $founded.attr('data-plominoid', saveProcess.nextFormID);
                editor.setDirty(true);
              }
              catch (e) {}

              return true;
            });
          }));
      });
    });

    return updates$.length ? Observable.forkJoin(updates$) : Observable.of([true]);
  })
  .map(() => true);
}
