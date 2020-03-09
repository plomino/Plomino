import { Pipe, PipeTransform } from "@angular/core";

@Pipe({
    name: "extractName",
})
export class ExtractNamePipe implements PipeTransform {
    transform(url: string): string {
        return url.split("/").pop();
    }
}
