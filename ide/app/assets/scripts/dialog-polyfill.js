!(function() {
    function e(e) {
        for (; e && e !== document.body; ) {
            var t = window.getComputedStyle(e),
                o = function(e, o) {
                    return !(void 0 === t[e] || t[e] === o);
                };
            if (
                t.opacity < 1 ||
                o("zIndex", "auto") ||
                o("transform", "none") ||
                o("mixBlendMode", "normal") ||
                o("filter", "none") ||
                o("perspective", "none") ||
                "isolate" === t.isolation ||
                "fixed" === t.position ||
                "touch" === t.webkitOverflowScrolling
            )
                return !0;
            e = e.parentElement;
        }
        return !1;
    }
    function t(e) {
        for (; e; ) {
            if ("dialog" === e.localName) return e;
            e = e.parentElement;
        }
        return null;
    }
    function o(e) {
        e && e.blur && e != document.body && e.blur();
    }
    function i(e, t) {
        for (var o = 0; o < e.length; ++o) if (e[o] == t) return !0;
        return !1;
    }
    function n(e) {
        if (
            ((this.dialog_ = e),
            (this.replacedStyleTop_ = !1),
            (this.openAsModal_ = !1),
            e.hasAttribute("role") || e.setAttribute("role", "dialog"),
            (e.show = this.show.bind(this)),
            (e.showModal = this.showModal.bind(this)),
            (e.close = this.close.bind(this)),
            "returnValue" in e || (e.returnValue = ""),
            "MutationObserver" in window)
        ) {
            var t = new MutationObserver(this.maybeHideModal.bind(this));
            t.observe(e, { attributes: !0, attributeFilter: ["open"] });
        } else {
            var o,
                i = !1,
                n = function() {
                    i ? this.downgradeModal() : this.maybeHideModal(), (i = !1);
                }.bind(this),
                a = function(e) {
                    var t = "DOMNodeRemoved";
                    (i |= e.type.substr(0, t.length) === t), window.clearTimeout(o), (o = window.setTimeout(n, 0));
                };
            ["DOMAttrModified", "DOMNodeRemoved", "DOMNodeRemovedFromDocument"].forEach(function(t) {
                e.addEventListener(t, a);
            });
        }
        Object.defineProperty(e, "open", { set: this.setOpen.bind(this), get: e.hasAttribute.bind(e, "open") }),
            (this.backdrop_ = document.createElement("div")),
            (this.backdrop_.className = "backdrop"),
            this.backdrop_.addEventListener("click", this.backdropClick_.bind(this));
    }
    var a = window.CustomEvent;
    (a && "object" != typeof a) ||
        ((a = function(e, t) {
            t = t || {};
            var o = document.createEvent("CustomEvent");
            return o.initCustomEvent(e, !!t.bubbles, !!t.cancelable, t.detail || null), o;
        }),
        (a.prototype = window.Event.prototype)),
        (n.prototype = {
            get dialog() {
                return this.dialog_;
            },
            maybeHideModal: function() {
                (this.dialog_.hasAttribute("open") && document.body.contains(this.dialog_)) || this.downgradeModal();
            },
            downgradeModal: function() {
                this.openAsModal_ &&
                    ((this.openAsModal_ = !1),
                    (this.dialog_.style.zIndex = ""),
                    this.replacedStyleTop_ && ((this.dialog_.style.top = ""), (this.replacedStyleTop_ = !1)),
                    this.backdrop_.parentNode && this.backdrop_.parentNode.removeChild(this.backdrop_),
                    r.dm.removeDialog(this));
            },
            setOpen: function(e) {
                e
                    ? this.dialog_.hasAttribute("open") || this.dialog_.setAttribute("open", "")
                    : (this.dialog_.removeAttribute("open"), this.maybeHideModal());
            },
            backdropClick_: function(e) {
                if (this.dialog_.hasAttribute("tabindex")) this.dialog_.focus();
                else {
                    var t = document.createElement("div");
                    this.dialog_.insertBefore(t, this.dialog_.firstChild),
                        (t.tabIndex = -1),
                        t.focus(),
                        this.dialog_.removeChild(t);
                }
                var o = document.createEvent("MouseEvents");
                o.initMouseEvent(
                    e.type,
                    e.bubbles,
                    e.cancelable,
                    window,
                    e.detail,
                    e.screenX,
                    e.screenY,
                    e.clientX,
                    e.clientY,
                    e.ctrlKey,
                    e.altKey,
                    e.shiftKey,
                    e.metaKey,
                    e.button,
                    e.relatedTarget
                ),
                    this.dialog_.dispatchEvent(o),
                    e.stopPropagation();
            },
            focus_: function() {
                var e = this.dialog_.querySelector("[autofocus]:not([disabled])");
                if ((!e && this.dialog_.tabIndex >= 0 && (e = this.dialog_), !e)) {
                    var t = ["button", "input", "keygen", "select", "textarea"],
                        i = t.map(function(e) {
                            return e + ":not([disabled])";
                        });
                    i.push('[tabindex]:not([disabled]):not([tabindex=""])'),
                        (e = this.dialog_.querySelector(i.join(", ")));
                }
                o(document.activeElement), e && e.focus();
            },
            updateZIndex: function(e, t) {
                if (e < t) throw new Error("dialogZ should never be < backdropZ");
                (this.dialog_.style.zIndex = e), (this.backdrop_.style.zIndex = t);
            },
            show: function() {
                this.dialog_.open || (this.setOpen(!0), this.focus_());
            },
            showModal: function() {
                if (this.dialog_.hasAttribute("open"))
                    throw new Error(
                        "Failed to execute 'showModal' on dialog: The element is already open, and therefore cannot be opened modally."
                    );
                if (!document.body.contains(this.dialog_))
                    throw new Error("Failed to execute 'showModal' on dialog: The element is not in a Document.");
                if (!r.dm.pushDialog(this))
                    throw new Error("Failed to execute 'showModal' on dialog: There are too many open modal dialogs.");
                e(this.dialog_.parentElement) &&
                    console.warn(
                        "A dialog is being shown inside a stacking context. This may cause it to be unusable. For more information, see this link: https://github.com/GoogleChrome/dialog-polyfill/#stacking-context"
                    ),
                    this.setOpen(!0),
                    (this.openAsModal_ = !0),
                    r.needsCentering(this.dialog_)
                        ? (r.reposition(this.dialog_), (this.replacedStyleTop_ = !0))
                        : (this.replacedStyleTop_ = !1),
                    this.dialog_.parentNode.insertBefore(this.backdrop_, this.dialog_.nextSibling),
                    this.focus_();
            },
            close: function(e) {
                if (!this.dialog_.hasAttribute("open"))
                    throw new Error(
                        "Failed to execute 'close' on dialog: The element does not have an 'open' attribute, and therefore cannot be closed."
                    );
                this.setOpen(!1), void 0 !== e && (this.dialog_.returnValue = e);
                var t = new a("close", { bubbles: !1, cancelable: !1 });
                this.dialog_.dispatchEvent(t);
            },
        });
    var r = {};
    (r.reposition = function(e) {
        var t = document.body.scrollTop || document.documentElement.scrollTop,
            o = t + (window.innerHeight - e.offsetHeight) / 2;
        e.style.top = Math.max(t, o) + "px";
    }),
        (r.isInlinePositionSetByStylesheet = function(e) {
            for (var t = 0; t < document.styleSheets.length; ++t) {
                var o = document.styleSheets[t],
                    n = null;
                try {
                    n = o.cssRules;
                } catch (e) {}
                if (n)
                    for (var a = 0; a < n.length; ++a) {
                        var r = n[a],
                            s = null;
                        try {
                            s = document.querySelectorAll(r.selectorText);
                        } catch (e) {}
                        if (s && i(s, e)) {
                            var l = r.style.getPropertyValue("top"),
                                d = r.style.getPropertyValue("bottom");
                            if ((l && "auto" != l) || (d && "auto" != d)) return !0;
                        }
                    }
            }
            return !1;
        }),
        (r.needsCentering = function(e) {
            var t = window.getComputedStyle(e);
            return (
                "absolute" == t.position &&
                !(("auto" != e.style.top && "" != e.style.top) || ("auto" != e.style.bottom && "" != e.style.bottom)) &&
                !r.isInlinePositionSetByStylesheet(e)
            );
        }),
        (r.forceRegisterDialog = function(e) {
            if (
                (e.showModal &&
                    console.warn("This browser already supports <dialog>, the polyfill may not work correctly", e),
                "dialog" !== e.localName)
            )
                throw new Error("Failed to register dialog: The element is not a dialog.");
            new n(e);
        }),
        (r.registerDialog = function(e) {
            e.showModal || r.forceRegisterDialog(e);
        }),
        (r.DialogManager = function() {
            this.pendingDialogStack = [];
            var e = this.checkDOM_.bind(this);
            (this.overlay = document.createElement("div")),
                (this.overlay.className = "_dialog_overlay"),
                this.overlay.addEventListener(
                    "click",
                    function(t) {
                        (this.forwardTab_ = void 0), t.stopPropagation(), e([]);
                    }.bind(this)
                ),
                (this.handleKey_ = this.handleKey_.bind(this)),
                (this.handleFocus_ = this.handleFocus_.bind(this)),
                (this.zIndexLow_ = 1e5),
                (this.zIndexHigh_ = 100150),
                (this.forwardTab_ = void 0),
                "MutationObserver" in window &&
                    (this.mo_ = new MutationObserver(function(t) {
                        var o = [];
                        t.forEach(function(e) {
                            for (var t, i = 0; (t = e.removedNodes[i]); ++i)
                                if (t instanceof Element)
                                    if ("dialog" === t.localName) o.push(t);
                                    else {
                                        var n = t.querySelector("dialog");
                                        n && o.push(n);
                                    }
                        }),
                            o.length && e(o);
                    }));
        }),
        (r.DialogManager.prototype.blockDocument = function() {
            document.documentElement.addEventListener("focus", this.handleFocus_, !0),
                document.addEventListener("keydown", this.handleKey_),
                this.mo_ && this.mo_.observe(document, { childList: !0, subtree: !0 });
        }),
        (r.DialogManager.prototype.unblockDocument = function() {
            document.documentElement.removeEventListener("focus", this.handleFocus_, !0),
                document.removeEventListener("keydown", this.handleKey_),
                this.mo_ && this.mo_.disconnect();
        }),
        (r.DialogManager.prototype.updateStacking = function() {
            for (var e, t = this.zIndexHigh_, o = 0; (e = this.pendingDialogStack[o]); ++o)
                e.updateZIndex(--t, --t), 0 === o && (this.overlay.style.zIndex = --t);
            var i = this.pendingDialogStack[0];
            if (i) {
                var n = i.dialog.parentNode || document.body;
                n.appendChild(this.overlay);
            } else this.overlay.parentNode && this.overlay.parentNode.removeChild(this.overlay);
        }),
        (r.DialogManager.prototype.containedByTopDialog_ = function(e) {
            for (; (e = t(e)); ) {
                for (var o, i = 0; (o = this.pendingDialogStack[i]); ++i) if (o.dialog === e) return 0 === i;
                e = e.parentElement;
            }
            return !1;
        }),
        (r.DialogManager.prototype.handleFocus_ = function(e) {
            if (
                !this.containedByTopDialog_(e.target) &&
                (e.preventDefault(), e.stopPropagation(), o(e.target), void 0 !== this.forwardTab_)
            ) {
                var t = this.pendingDialogStack[0],
                    i = t.dialog,
                    n = i.compareDocumentPosition(e.target);
                return (
                    n & Node.DOCUMENT_POSITION_PRECEDING &&
                        (this.forwardTab_ ? t.focus_() : document.documentElement.focus()),
                    !1
                );
            }
        }),
        (r.DialogManager.prototype.handleKey_ = function(e) {
            if (((this.forwardTab_ = void 0), 27 === e.keyCode)) {
                e.preventDefault(), e.stopPropagation();
                var t = new a("cancel", { bubbles: !1, cancelable: !0 }),
                    o = this.pendingDialogStack[0];
                o && o.dialog.dispatchEvent(t) && o.dialog.close();
            } else 9 === e.keyCode && (this.forwardTab_ = !e.shiftKey);
        }),
        (r.DialogManager.prototype.checkDOM_ = function(e) {
            var t = this.pendingDialogStack.slice();
            t.forEach(function(t) {
                e.indexOf(t.dialog) !== -1 ? t.downgradeModal() : t.maybeHideModal();
            });
        }),
        (r.DialogManager.prototype.pushDialog = function(e) {
            var t = (this.zIndexHigh_ - this.zIndexLow_) / 2 - 1;
            return (
                !(this.pendingDialogStack.length >= t) &&
                (1 === this.pendingDialogStack.unshift(e) && this.blockDocument(), this.updateStacking(), !0)
            );
        }),
        (r.DialogManager.prototype.removeDialog = function(e) {
            var t = this.pendingDialogStack.indexOf(e);
            t != -1 &&
                (this.pendingDialogStack.splice(t, 1),
                0 === this.pendingDialogStack.length && this.unblockDocument(),
                this.updateStacking());
        }),
        (r.dm = new r.DialogManager()),
        document.addEventListener(
            "submit",
            function(e) {
                var o = e.target;
                if (o && o.hasAttribute("method") && "dialog" === o.getAttribute("method").toLowerCase()) {
                    e.preventDefault();
                    var i = t(e.target);
                    if (i) {
                        var n,
                            a = [document.activeElement, e.explicitOriginalTarget],
                            r = ["BUTTON", "INPUT"];
                        a.some(function(t) {
                            if (t && t.form == e.target && r.indexOf(t.nodeName.toUpperCase()) != -1)
                                return (n = t.value), !0;
                        }),
                            i.close(n);
                    }
                }
            },
            !0
        ),
        (r.forceRegisterDialog = r.forceRegisterDialog),
        (r.registerDialog = r.registerDialog),
        "function" == typeof define && "amd" in define
            ? define(function() {
                  return r;
              })
            : "object" == typeof module && "object" == typeof module.exports
            ? (module.exports = r)
            : (window.dialogPolyfill = r);
})();
