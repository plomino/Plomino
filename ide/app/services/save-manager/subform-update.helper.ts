import { Observable } from "rxjs/Rx";

export function updateRelatedSubformsAfterFormSave(saveProcess: any) {
    if (!saveProcess.isWorking()) {
        return Observable.of(true);
    }
    return Observable.of(true)
        .flatMap(() => {
            const updates$: Observable<boolean>[] = [];

            /** using cached data */

            /** cache from tabContentStates */
            const states: [
                string,
                {
                    content: string;
                    pattern?: string;
                }
            ][] = saveProcess.tabsManagerService.getAllStates();

            states.forEach(state => {
                if (!state[1].content) {
                    return true;
                }
                const cachedTabId = state[0];
                if (cachedTabId === saveProcess.originalFormID) {
                    return true;
                }
                const content = state[1].content;
                const pattern = state[1].pattern;
                const $content = $(`<div>${content}</div>`); // virtual DOM
                $content
                    .find(`.plominoSubformClass[data-plominoid="${saveProcess.originalFormID}"]`)
                    .each((i, subformElement) => {
                        const $founded = $(subformElement);
                        let updatedSubformURL = `${window.location.pathname
                            .replace("++resource++Products.CMFPlomino/ide/", "")
                            .replace("/index.html", "")}/${cachedTabId}`;
                        updatedSubformURL += "/@@tinyform/example_widget";
                        updatedSubformURL += saveProcess.nextFormID;

                        /** flush the data in the cache to prevent problems */
                        saveProcess.tabsManagerService.flushTabContentState(cachedTabId);
                        saveProcess.objService.flushFormSettingsCache(cachedTabId);

                        // updates$.push(
                        //   saveProcess.http.get(updatedSubformURL)
                        //     .map((response: Response) => {
                        // const result = saveProcess.widgetService.getGroupLayout(state[0], {
                        //   id: Math.floor(Math.random() * 1e10 + 1e10).toString(),
                        //   layout: response.json()
                        // })
                        // .map((result: string) => {
                        //   try {
                        //     const $result = $(result);
                        //     $result.find('input,textarea,button')
                        //       .removeAttr('name').removeAttr('id');
                        //     $result.find('span')
                        //       .removeAttr('data-plominoid').removeAttr('data-mce-resize');
                        //     $result.removeAttr('data-groupid');
                        //     $result.find('div').removeAttr('data-groupid');
                        //     const subformHTML = $($result.html()).html();
                        //     $founded.html(subformHTML);
                        //     $founded.attr('data-plominoid', saveProcess.nextFormID);
                        //     // editor.setDirty(true);

                        //     /** save $founded back to cache */
                        //     saveProcess.tabsManagerService.saveTabContentState(
                        //       cachedTabId, {
                        //         content: $content.html(),
                        //         pattern
                        //       }
                        //     );
                        //   }
                        //   catch (e) {
                        //     console.warn(e);
                        //   }

                        //   return true;
                        // });

                        //   return Observable.of(true);
                        // })
                        // );
                    });
            });

            /** using editors (temporary disabled) */
            /*tinymce.editors*/ [].forEach((editor: TinyMceEditor) => {
                /**
                 * update all subforms while parent form changed
                 */
                if (editor === null) {
                    return true;
                }

                let edBody: any;

                try {
                    edBody = editor.getBody();
                } catch (e) {
                    return true;
                }
                $(edBody)
                    .find(`.plominoSubformClass[data-plominoid="${saveProcess.originalFormID}"]`)
                    .each((i, subformElement) => {
                        const $founded = $(subformElement);
                        let updatedSubformURL = `${window.location.pathname
                            .replace("++resource++Products.CMFPlomino/ide/", "")
                            .replace("/index.html", "")}/${editor.id}`;
                        updatedSubformURL += "/@@tinyform/example_widget";
                        updatedSubformURL += saveProcess.nextFormID;

                        updates$.push(
                            saveProcess.http
                                .post(updatedSubformURL, JSON.stringify({ widget_type: "subform", id: "" }))
                                .map((response: Response) => {
                                    return saveProcess.widgetService
                                        .getGroupLayout(editor.id, {
                                            id: Math.floor(Math.random() * 1e10 + 1e10).toString(),
                                            layout: response.json(),
                                        })
                                        .map((result: string) => {
                                            try {
                                                const $result = $(result);
                                                $result
                                                    .find("input,textarea,button")
                                                    .removeAttr("name")
                                                    .removeAttr("id");
                                                $result
                                                    .find("span")
                                                    .removeAttr("data-plominoid")
                                                    .removeAttr("data-mce-resize");
                                                $result.removeAttr("data-groupid");
                                                $result.find("div").removeAttr("data-groupid");
                                                const subformHTML = $($result.html()).html();
                                                $founded.html(subformHTML);
                                                $founded.attr("data-plominoid", saveProcess.nextFormID);
                                                editor.setDirty(true);
                                            } catch (e) {}

                                            return true;
                                        });
                                })
                        );
                    });
            });

            return updates$.length ? Observable.forkJoin(updates$) : Observable.of([true]);
        })
        .map(() => true);
}
