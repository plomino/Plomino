declare function require(arg: string): any;

interface PlominoFormSaveProcessOptions {
    immediately: boolean;
    formURL: string;
    formData: any;
    labelsRegistryLink: any;
    httpServiceLink: any;
    activeEditorServiceLink: any;
    widgetServiceLink: any;
    objServiceLink: any;
    tabsManagerServiceLink: any;
}

interface PlominoTab {
    url: string;
    folder?: boolean;
    type?: string;
    children?: any[];
    label: string;
    formUniqueId?: any;
    showAdd?: boolean;
    active?: boolean;
    editor?: any;
    path?: any[];
    typeLabel?: string;
    typeNameUrl?: string;
    isField?: boolean;
}

interface HTMLDialogElement extends HTMLElement {
    open: boolean;
    returnValue: string;
    close: (returnValue?: string) => void;
    show: () => void;
    showModal: () => void;
}

interface PlominoFormDataAPIResponse {
    "@id": string;
    "@type": string;
    UID: string;
    ajax_include_head: any;
    ajax_load: any;
    beforeCreateDocument: string;
    beforeSaveDocument: string;
    created: string;
    description: string;
    document_id: string;
    document_title: string;
    dynamic_document_title: boolean;
    form_layout: string;
    form_method: string;
    helpers: any[];
    hide_default_actions: boolean;
    id: string;
    isMulti: boolean;
    isPage: boolean;
    isSearchForm: boolean;
    items: { "@id": string; "@type": string; description: string; title: string }[];
    items_total: number;
    modified: string;
    onCreateDocument: string;
    onDeleteDocument: string;
    onDisplay: string;
    onOpenDocument: string;
    onSaveDocument: string;
    onSearch: string;
    parent: { "@id": string; "@type": string; description: string; title: string };
    resources_css: any;
    resources_js: any;
    review_state: string;
    search_formula: string;
    search_view: any;
    store_dynamic_document_title: boolean;
    title: string;
}

interface PlominoFieldDataAPIResponse extends PlominoFormDataAPIResponse {
    field_type: string;
    selectionlist: any;
}

interface PlominoFieldTreeObject {
    name: string;
    type: string;
    parent: string;
    resolved: boolean;
}

interface PlominoFieldRepresentationObject {
    id: string;
    formUniqueId?: any;
    type: string;
    url?: string;
    parent?: string;
}

interface PlominoFieldSettingsFormDataObject {
    id: string;
    title: string;
    type: string;
    widget: string;
}

interface PlominoFieldUpdatesStreamEvent {
    fieldData: PlominoFieldRepresentationObject;
    newData: PlominoFieldSettingsFormDataObject;
    newId: string;
}

interface PlominoUpdatingItemData {
    base: string;
    type: string;
    newId: string;
    oldTemplate: HTMLElement;
    newTitle?: string;
}

interface PlominoLayoutElementReplaceData {
    newTemplate: string;
    item?: PlominoUpdatingItemData;
    oldTemplate: HTMLElement;
}

interface PlominoIFrameMouseMove {
    originalEvent: MouseEvent;
    draggingService: any;
    editorId: string;
    $group?: JQuery;
}

interface PlominoIFrameMouseLeave {
    draggingService: any;
}

interface PlominoDraggingData {
    templateId?: string;
    existingElementId?: string;
    template?: PlominoFormGroupTemplate;
    resolver: (data?: any) => void;
    "@type": string;
    parent?: string;
    resolved: boolean;
    eventData?: any;
}

interface PlominoFormGroupContent {
    id: string;
    layout?: string;
    old_id?: string;
    title: string;
}

interface PlominoFormGroupTemplate {
    layout: string;
    description?: string;
    group?: string;
    groupid?: string;
    id: string;
    title?: string;
    group_contents?: PlominoFormGroupContent[];
}

interface InsertTemplateEvent extends PlominoFormGroupTemplate {
    parent: string;
    target: HTMLElement;
}

interface InsertFieldEvent {
    "@type": string;
    type?: string;
    title: string;
    name?: string;
    action_type?: string;
    displayed_field?: string;
    form_layout?: string;
    target?: HTMLElement | true;
    subformHTML?: string;
}

interface AddFieldResponse {
    created: string;
    title?: string;
    "@id"?: string;
    id?: string;
    formUniqueId?: string;
    parent?: { "@id": string };
}

interface PlominoIteratingLayoutElement {
    type: string;
    contents?: PlominoFormGroupContent[];
    baseUrl: string;
    el: JQuery;
    templateMode: boolean;
    itemPromise: Promise<any>;
    itemPromiseResolve: (value?: {} | PromiseLike<{}>) => void;
}

interface TinyMceObservable {
    off: (name?: string, callback?: Function) => Record<string, any>;
    on: (name: string, callback: Function) => Record<string, any>;
    fire: (name: string, args?: Record<string, any>, bubble?: boolean) => Event;
}

interface TinyMceEditor extends TinyMceObservable {
    destroy: (automatic: boolean) => void;
    remove: () => void;
    onInit: { add: (func: () => void) => void };
    onChange: { add: (func: (e: any) => void) => void };
    onKeyDown: { add: (func: (e: KeyboardEvent) => void) => void };
    onKeyUp: { add: (func: (e: KeyboardEvent) => void) => void };
    onNodeChange: { add: (func: (nodeChangeEvent: any) => void) => void };
    onActivate: { add: (func: (e: any) => void) => void };
    onMouseDown: { add: (func: (ev: MouseEvent) => void) => void };
    hide: () => void;
    setDirty: (dirty: boolean) => void;
    isDirty: () => boolean;
    show: () => void;
    getContent: (args?: Record<string, any>) => string;
    getContainer: (args?: Record<string, any>) => HTMLElement;
    getBody: () => string;
    getDoc: () => any;
    setContent: (content: string, args?: Record<string, any>) => string;
    onSaveContent: any;
    addMenuItem: any;
    focus: (skip_focus?: boolean) => void;
    undoManager: TinyMceUndoManager;
    settings: Record<string, any>;
    selection?: any;
    buttons?: any;
    dom?: any;
    id?: string;
    execCommand: (command: string, user_interface: boolean, value: string, extra?: any) => boolean;
}

interface TinyMceUndoManager {
    undo: () => Record<string, any>;
    clear: () => void;
    hasUndo: () => boolean;
}

interface TinyMceEvent {}

interface TinyMceStatic extends TinyMceObservable {
    init: (settings: Record<string, any>) => void;

    /**
     * This will execute the specified command on the currently selected editor instance
     * if it's an instance command.
     */
    execCommand: (command: string, user_interface: boolean, value: string) => boolean;
    activeEditor: TinyMceEditor;
    get: (id: string | number) => TinyMceEditor;
    editors: TinyMceEditor[];
    EditorManager: any;
    DOM: any;
    dom: any;
}

declare let tinymce: TinyMceStatic;
declare let dialogPolyfill: any;

// Type definitions for material-design-lite v1.1.3
// Project: https://getmdl.io
// Definitions by: Brad Zacher <https://github.com/bradzacher/>
// Definitions: https://github.com/DefinitelyTyped/DefinitelyTyped

declare namespace MaterialDesignLite {
    interface ComponentHandler {
        /**
         * Searches existing DOM for elements of our component type and upgrades them
         * if they have not already been upgraded.
         */
        upgradeDom(): void;
        /**
         * Searches existing DOM for elements of our component type and upgrades them
         * if they have not already been upgraded.
         *
         * @param {string} jsClass the programatic name of the element class we
         * need to create a new instance of.
         */
        upgradeDom(jsClass: string): void;
        /**
         * Searches existing DOM for elements of our component type and upgrades them
         * if they have not already been upgraded.
         *
         * @param {string} jsClass the programatic name of the element class we
         * need to create a new instance of.
         * @param {string} cssClass the name of the CSS class elements of this
         * type will have.
         */
        upgradeDom(jsClass: string, cssClass: string): void;

        /**
         * Upgrades a specific element rather than all in the DOM.
         *
         * @param {!Element} element The element we wish to upgrade.
         */
        upgradeElement(element: HTMLElement): void;
        /**
         * Upgrades a specific element rather than all in the DOM.
         *
         * @param {!Element} element The element we wish to upgrade.
         * @param {string} jsClass Optional name of the class we want to upgrade
         * the element to.
         */
        upgradeElement(element: HTMLElement, jsClass: string): void;

        /**
         * Upgrades a specific list of elements rather than all in the DOM.
         *
         * @param {!Element} elements
         * The elements we wish to upgrade.
         */
        upgradeElements(elements: HTMLElement): void;
        /**
         * Upgrades a specific list of elements rather than all in the DOM.
         *
         * @param {!Array<!Element>} elements
         * The elements we wish to upgrade.
         */
        upgradeElements(elements: Array<HTMLElement>): void;
        /**
         * Upgrades a specific list of elements rather than all in the DOM.
         *
         * @param {!NodeList} elements
         * The elements we wish to upgrade.
         */
        upgradeElements(elements: NodeList): void;
        /**
         * Upgrades a specific list of elements rather than all in the DOM.
         *
         * @param {!HTMLCollection} elements
         * The elements we wish to upgrade.
         */
        upgradeElements(elements: HTMLCollection): void;

        /**
         * Upgrades all registered components found in the current DOM. This is
         * automatically called on window load.
         */
        upgradeAllRegistered(): void;

        /**
         * Allows user to be alerted to any upgrades that are performed for a given
         * component type
         *
         * @param {string} jsClass The class name of the MDL component we wish
         * to hook into for any upgrades performed.
         * @param {function(!HTMLElement)} callback The function to call upon an
         * upgrade. This function should expect 1 parameter - the HTMLElement which
         * got upgraded.
         */
        registerUpgradedCallback(jsClass: string, callback: (element: HTMLElement) => any): void;

        /**
         * Registers a class for future use and attempts to upgrade existing DOM.
         *
         * @param {componentHandler.ComponentConfigPublic} config the registration configuration
         */
        register(config: ComponentConfigPublic): void;

        /**
         * Downgrade either a given node, an array of nodes, or a NodeList.
         *
         * @param {!Node} nodes The list of nodes.
         */
        downgradeElements(nodes: Node): void;
        /**
         * Downgrade either a given node, an array of nodes, or a NodeList.
         *
         * @param {!Array<!Node>} nodes The list of nodes.
         */
        downgradeElements(nodes: Array<Node>): void;
        /**
         * Downgrade either a given node, an array of nodes, or a NodeList.
         *
         * @param {!NodeList} nodes The list of nodes.
         */
        downgradeElements(nodes: NodeList): void;
    }
    interface ComponentConfigPublic {
        constructor(element: HTMLElement): void;
        classAsString: string;
        cssClass: string;
        widget?: string | boolean;
    }
}

declare let componentHandler: MaterialDesignLite.ComponentHandler;

interface FormData {
    append(name: any, value: any, blobName?: string): void;
    delete(name: string): void;
    entries(): Iterator<any>;
    values(): Iterator<any>;
    keys(): Iterator<any>;
    get(name: string): any;
    set(name: string, value: any, filename?: any): any;
    getAll(name: string): any[];
    has(name: string): boolean;
}

declare namespace FormData {
    interface Dictionary<T> {
        [key: string]: T;
    }
}

declare var FormData: {
    prototype: FormData;
    new (form?: HTMLFormElement): FormData;
};
