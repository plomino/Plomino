class BrowserHelper {
    private isIE: boolean = null;

    testIE() {
        if (this.isIE === null) {
            const ieVersion = (function() {
                if (new RegExp("MSIE ([0-9]{1,}[.0-9]{0,})").exec(navigator.userAgent) != null) {
                    return parseFloat(RegExp.$1);
                } else {
                    return false;
                }
            })();
            const isIE =
                "-ms-scroll-limit" in document.documentElement.style &&
                "-ms-ime-align" in document.documentElement.style;

            this.isIE = Boolean(ieVersion) || isIE;
        } else {
            return this.isIE;
        }
    }

    fixIEStartup() {
        if (this.testIE()) {
            setTimeout(() => {
                $("#application-loader").css("display", "none");
            }, 2000);
        }
    }
}

const browserHelper = new BrowserHelper();
export { browserHelper };
