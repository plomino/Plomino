import { Injectable, EventEmitter } from '@angular/core';

@Injectable()
export class LabelsRegistryService {
  private labelsRegistry: Map<string, Object> = new Map<string, Object>();
  private updated: EventEmitter<any> = new EventEmitter();

  constructor() { }

  update(id: string, value: string, key = 'title', muteEvent = false) {
    const tmp = this.labelsRegistry.get(id);
    
    if (!tmp) {
      this.labelsRegistry.set(id, { [key]: value.trim() });
    }
    else {
      tmp[key] = value.trim();
      this.labelsRegistry.set(id, tmp);
    }

    if (!muteEvent) {
      this.updated.next(true);
    }
  }

  remove(id: string) {
    this.labelsRegistry.delete(id);
  }

  removeForm(url: string) {
    this.labelsRegistry.forEach((value, key) => {
      if (key.indexOf(url) !== -1) {
        this.labelsRegistry.delete(key);
      }
    })
  }

  onUpdated() {
    return this.updated.asObservable();
  }

  getRegistry() {
    return this.labelsRegistry;
  }

  get(id: string, key = 'temporary_title') {
    if (this.labelsRegistry.has(id) 
      && !this.labelsRegistry.get(id)[key]
      && key === 'temporary_title'
      && this.labelsRegistry.get(id)['title']
    ) {
      this.update(id, this.labelsRegistry.get(id)['title'], 'temporary_title');
    }
    return this.labelsRegistry.has(id) ? this.labelsRegistry.get(id)[key] : null;
  }

  replace(oldId: string, newId: string, title: string) {
    this.labelsRegistry.delete(oldId);
    this.labelsRegistry.set(newId, { title });
    this.updated.next(true);
  }
}
