import { TinyMCEFormContentManagerService } from './../../editors/tiny-mce/content-manager/content-manager.service';
import { Injectable } from '@angular/core';

@Injectable()
export class PlominoSaveManagerService {

  private savedStates: Map<string, string> = new Map<string, string>();

  constructor(private contentManager: TinyMCEFormContentManagerService) { }

  nextEditorSavedState(editorId: string, state: string): void {
    this.savedStates.set(editorId, state);
  }

  isEditorUnsaved(editorId: string): boolean {
    if (this.savedStates.has(editorId)) {
      return this.savedStates.get(editorId)
        !== this.contentManager.getContent(editorId);
    }
    else {
      return true;
    }
  }
}
