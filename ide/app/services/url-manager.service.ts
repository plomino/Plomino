import { PlominoTabsManagerService } from "./tabs-manager/index";
import { LogService } from "./log.service";
import { Injectable } from "@angular/core";

@Injectable()
export class URLManagerService {
    constructor(private log: LogService, private tabsManagerService: PlominoTabsManagerService) {}

    rebuildURL(openedTabs: PlominoTab[]): void {
        const url = openedTabs.map(tab => tab.url.split("/").pop()).join(",");
        this.setURL(url);
    }

    restoreTabsFromURL(): void {
        const urlItems = this.parseURLString();

        if (!urlItems.length) {
            /* on start, if not tabs to open, then start on Service */
            window["materialPromise"].then(() => {
                setTimeout(() => {
                    this.tabsManagerService.openTab({
                        id: "workflow",
                        url: "workflow",
                        label: "Workflow",
                        editor: "workflow",
                    });
                }, 100);
            });
        } else {
            this.tabsManagerService.setOpenedTabActive = false;
            let i = 0;

            for (const urlItem of urlItems) {
                if (++i === urlItems.length) {
                    this.tabsManagerService.setOpenedTabActive = true;
                }

                if (urlItem === "workflow") {
                    window["materialPromise"].then(() => {
                        this.tabsManagerService.openTab({
                            id: "workflow",
                            url: "workflow",
                            label: "Workflow",
                            editor: "workflow",
                        });
                    });
                } else {
                    window["materialPromise"].then(() => {
                        const $resource = $(`.tree-node--name:contains("${urlItem}")`).filter(
                            (i, node: HTMLElement) =>
                                $(node)
                                    .text()
                                    .trim() === urlItem
                        );

                        if (!$resource.length) {
                            return;
                        }

                        const tabData = {
                            editor: {
                                PlominoForm: "layout",
                                PlominoView: "view",
                            }[$resource.attr("data-type")],
                            label: $resource
                                .next()
                                .text()
                                .trim(),
                            url: $resource.attr("id").replace("tree_", ""),
                            id: urlItem,
                        };

                        this.tabsManagerService.openTab(tabData);
                    });
                }
            }
        }
    }

    parseURLString(): string[] {
        const result = window.location.hash.replace("#t=", "").split(",");
        return result.length && Boolean(result[0]) ? result : [];
    }

    private setURL(url: string): void {
        window.location.hash = url ? `#t=${url}` : "";
    }
}
