import { Injectable } from '@angular/core';

@Injectable()
export class LabelsRegistryService {
  private labelsRegistry: Map<string, Object> = new Map<string, Object>();
  constructor() { }

  update(id: string, title: string) {
    this.labelsRegistry.set(id, { title });
  }

  getRegistry() {
    return this.labelsRegistry;
  }

  get(id: string, key = 'title') {
    return this.labelsRegistry.has(id) ? this.labelsRegistry.get(id)[key] : null;
  }

  replace(oldId: string, newId: string, title: string) {
    this.labelsRegistry.delete(oldId);
    this.labelsRegistry.set(newId, { title });
  }
}
