interface PlominoWorkflowItem {
  id?: number;
  title?: string;
  form?: string;
  user?: string;
  process?: string;
  condition?: string;
  view?: string;
  goto?: string;
  type?: string;
  selected?: boolean;
  macroId?: number;
  macroText?: string;

  /**
   * root means that this item is top element
   */
  root?: boolean;

  /**
   * dropping means that it is preview div with opacity
   */
  dropping?: boolean;

  children: PlominoWorkflowItem[];
}

interface WFDragEvent {
  dragData: { title: string, type: string },
  mouseEvent: DragEvent
}

interface KVChangeEvent {
  key: string;
  value: string;
}
