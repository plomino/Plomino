import {Injectable} from 'angular2/core';
import {DATA} from './mock-tree';

@Injectable()
export class TreeService {
    getTree() {
        return Promise.resolve(DATA);
    }
}
