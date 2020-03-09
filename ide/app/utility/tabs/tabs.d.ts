interface PlominoTabUnit {
    id: string;
    url: string;
    editor: "layout" | "workflow" | "code" | "view";
    label: string;
    isDirty?: boolean;
}
