interface PlominoIFrameMouseMove {
  originalEvent: MouseEvent;
  draggingService: any;
  editorId: string;
}

interface PlominoIFrameMouseLeave {
  draggingService: any;
}

interface PlominoDraggingData {
  'templateId'?: string;
  'template'?: PlominoFormGroupTemplate;
  'resolver': (data?: any) => void;
  '@type': string;
  'parent'?: string;
  'resolved': boolean;
  'eventData'?: any;
}

interface PlominoFormGroupContent {
  id: string;
  layout: string;
  old_id: string;
  title: string;
}

interface PlominoFormGroupTemplate {
  layout: string;
  description: string;
  group: string;
  id: string;
  title: string;
  group_contents?: PlominoFormGroupContent[];
}

interface TinyMceObservable {
  off: (name?: string, callback?: Function) => Object
  on: (name: string, callback: Function) => Object
  fire: (name: string, args?: Object, bubble?: boolean) => Event
}

interface TinyMceEditor extends TinyMceObservable {
  destroy: (automatic: boolean) => void
  remove: () => void
  hide: () => void
  setDirty: (dirty: boolean) => void
  show: () => void
  getContent: (args?: Object) => string
  getDoc: () => any
  setContent: (content: string, args?: Object) => string
  focus: (skip_focus?: boolean) => void
  undoManager: TinyMceUndoManager
  settings: Object
  selection?: any
  buttons?: any
  dom?: any
  execCommand: (command: string, user_interface: boolean, value: string, extra?: any) => boolean
}

interface TinyMceUndoManager {
  undo: () => Object
  clear: () => void
  hasUndo: () => boolean
}

interface TinyMceEvent {

}

interface TinyMceStatic extends TinyMceObservable {
  init: (settings: Object) => void;
  
  /**
   * This will execute the specified command on the currently selected editor instance
   * if it's an instance command.
   */
  execCommand: (command: string, user_interface: boolean, value: string) => boolean;
  activeEditor: TinyMceEditor;
  get: (id: string) => TinyMceEditor;
  EditorManager: any;
  DOM: any;
  dom: any;
}

declare var tinymce: TinyMceStatic;
