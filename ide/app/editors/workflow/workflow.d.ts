interface ReceiverEvent {
    dragEvent: DragEvent;
    eventName: "enter" | "leave" | "start" | "end" | "drop" | "over";
    dragServiceType: string;
    wfNode?: HTMLElement;
    item?: PlominoWorkflowItem;
}

interface PlominoNodeIndexKey {
    id: number;
    item: PlominoWorkflowItem;
    parent: PlominoWorkflowItem;
    parentIndex: number;
}

interface PlominoWorkflowItem {
    id?: number;
    title?: string;
    form?: string;
    user?: string;
    process?: string;
    condition?: string;
    view?: string;
    goto?: string;
    gotoLabel?: string;
    notes?: string;
    type?: string;
    selected?: boolean;
    macroId?: number;
    macroText?: string;
    macroDesc?: string;

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
    dragData: { title: string; type: string };
    mouseEvent: DragEvent;
}

interface KVChangeEvent {
    key: string;
    value: string;
}
