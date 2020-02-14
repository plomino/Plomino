import { PlominoTabsManagerService } from './../../../services/tabs-manager/index';
import { ACEEditorComponent } from './../../../editors/ace-editor/ace-editor.component';
import { PlominoViewEditorComponent } from './../../../editors/view-editor/view-editor.component';
import { PlominoWorkflowComponent } from './../../../editors/workflow/index';
import { TinyMCEComponent } from './../../../editors/tiny-mce/tiny-mce.component';
import { Component, Input, OnChanges, NgZone } from '@angular/core';

@Component({
  selector: 'plomino-tab',
  template: require('./plomino-tab.component.html'),
  directives: [
    TinyMCEComponent, 
    PlominoWorkflowComponent, 
    PlominoViewEditorComponent,
    ACEEditorComponent,
  ],
})

export class PlominoTabComponent implements OnChanges {
  @Input() isActive = true;
  @Input() isDirty = false;
  @Input() id: string;
  @Input() url: string;
  @Input() label: string;
  @Input() editor: 'layout'|'workflow'|'code'|'view';

  constructor(private zone: NgZone, 
    private tabsManagerService: PlominoTabsManagerService) { }

  ngOnChanges(data: any) {
    if (data.url) {
      const editor = this.editor;
      this.editor = null;
      this.zone.run(() => {}); 
      setTimeout(() => {
        this.editor = editor;
        this.zone.run(() => {});
      });
    }
  }

  onLoadingStateChange(state: boolean) {
    console.log('onLoadingStateChange', this.id, state);
  }

  onDirtyStateChange(state: boolean) {
    this.tabsManagerService.setTabDirty({
      id: this.id.replace('tab-content_', ''), 
      label: this.label, editor: this.editor, url: this.url
    }, state);
  }

  onLayoutFieldSelected(fieldData: any) {
    console.log('onLayoutFieldSelected', this.id, fieldData);
  }
}
