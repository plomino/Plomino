export default class FormDataPolyfill {
    prototype: FormData;
    append(name: any, value: any, blobName?: string): void;
    delete(name: string): void;
    entries(): Iterator<any>;
    values(): Iterator<any>;
    keys(): Iterator<any>;
    get(name: string): any;
    set(name: string, value: any, filename?: any): any;
    getAll(name: string): any[];
    has(name: string): boolean;
    _blob(): Blob;
    _asNative(): FormData;
}
