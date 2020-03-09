require([
    "jquery",
    "pat-base",
    "mockup-patterns-modal",
    "mockup-patterns-select2",
    "mockup-patterns-sortable",
    "mockup-patterns-backdrop",
    "mockup-utils",
    "pat-registry",
], function($, Base, Modal, Select2, Sortable, Backdrop, utils, registry) {
    "use strict";
    if (window["registryPromise"]) {
        window["registryPromiseResolve"](registry);
    }
    var MacroWidget = Base.extend({
        name: "plominomacros",
        parser: "mockup",
        trigger: ".plomino-macros",
        defaults: {},
        init: function() {
            var self = this;
            //self.rules = JSON.parse(self.$el.attr('data-rules'));
            self.form_urls = JSON.parse(self.$el.attr("data-form-urls"));

            var selectdata = [];
            for (var group in self.form_urls) {
                selectdata.push({
                    text: group,
                    children: self.form_urls[group].map(function(macro) {
                        if (macro.title != undefined) {
                            return { id: macro.id, text: macro["title"] };
                        }
                    }),
                });
            }

            self.select2_args = {
                data: selectdata,
                separator: "\t", //important, needs to match with python code
                //orderable:true,
                multiple: true,
                allowNewItems: false,
                placeholder: "add a new rule",
                formatSelection: self.formatMacro,
            };

            if (self.$el.closest("dialog").length) {
                self.select2_args.dropdownParent = self.$el.closest("dialog").find(".mdl-dialog__content");
            }

            var html = "";
            self.item = self.$el.find("li").last()[0].outerHTML;
            //            self.rules.map(function(rule) {
            //                html += self.item;
            //            });
            self.$el.prepend(html);
            self.ids = {};
            //            self.rules.push([]);
            var i = 0;
            self.$el.find("input").each(function(index, el) {
                //var rule = self.rules[i];
                var rule = [];
                if (el.value != "") {
                    rule = el.value.split("\t");
                }

                if (rule.map == undefined) {
                    //else rule is old style and not a list of macros yet
                    rule = [rule];
                }
                rule = rule.map(function(macro_json) {
                    if (macro_json == "") {
                        return;
                    }
                    try {
                        var macro = JSON.parse(macro_json);
                        if (macro["_macro_id_"]) {
                            self.ids[macro["_macro_id_"]] = true;
                        }
                        return { id: macro_json, text: "" };
                    } catch (e) {
                        return;
                    }
                });
                self.initInput.bind({ widget: self })(el, rule);
                i++;
            });
            self.cleanup_inputs.bind({ widget: self })();

            self.backdrop = new Backdrop(self.$el, { closeOnEsc: true, closeOnClick: false });
            self.loading = utils.Loading({ backdrop: self.backdrop });
        },
        initInput: function(el, rule) {
            var self = this.widget;
            new Select2($(el), self.select2_args);
            // Select2 pattern orderable is broken. need to do it ourselves
            var select = $(el);
            select.select2("data", rule);

            /* if its a workflow modal then create radio near using event */
            jQuery(window["macrosSelectorRefreshEvent"]).trigger("macros_selector_refresh");

            if ($(el).prop("disabled")) {
                select.enable(false);
                self.disabled = true;
            }

            if (
                select.closest(".plomino-macros-rule").length &&
                !select.closest("#wf-item-settings-dialog__wd").length
            ) {
                var isDisabled =
                    select
                        .closest(".plomino-macros-rule")
                        .get(0)
                        .querySelector(".select2-search-choice") === null;
                select
                    .closest(".plomino-macros-rule")
                    .prepend(
                        isDisabled
                            ? '<i class="material-icons" ' +
                                  'style="color: lightgray; cursor: not-allowed">more_vert</i>'
                            : '<i class="material-icons">more_vert</i>'
                    );
            }

            select.change(function(evt) {
                var macro_select = $(evt.target);
                if (evt.added != undefined) {
                    var url = evt.added.id;
                    var text = evt.added.text;

                    // first pop the value that just got added out until after the popup
                    var values = macro_select.select2("data");
                    values.pop();
                    macro_select.select2("data", values);

                    self.edit_macro.bind({ widget: self })(macro_select, url, text, {}, values.length);
                } else if (evt.removed != undefined) {
                    var id = evt.removed.id;
                    self.cleanup_inputs.bind({ widget: self })();
                }

                //evt.stopPropagation();
                //evt.preventDefault();
                return false;
            });
        },
        cleanup_inputs: function() {
            /**
             * swap 2 html elements and save all bounded data
             * @param {HTMLElement} obj1
             * @param {HTMLElement} obj2
             */
            var swapHTMLElements = function swapHTMLElements(obj1, obj2) {
                // save the location of obj2
                var parent2 = obj2.parentNode;
                var next2 = obj2.nextSibling;
                // special case for obj1 is the next sibling of obj2
                if (next2 === obj1) {
                    // just put obj1 before obj2
                    parent2.insertBefore(obj1, obj2);
                } else {
                    // insert obj2 right before obj1
                    obj1.parentNode.insertBefore(obj2, obj1);

                    // now insert obj1 where obj2 was
                    if (next2) {
                        // if there was an element after obj2, then insert obj1 right before that
                        parent2.insertBefore(obj1, next2);
                    } else {
                        // otherwise, just append as last child
                        parent2.appendChild(obj1);
                    }
                }
            };

            var self = this.widget;
            var count = self.$el.find(".select2-container").size();
            // remove any empty rules
            self.$el.find(".select2-container").each(function(index, el) {
                var select = $(el);
                var values = select.select2("data");

                try {
                    // console.log('yo', values.map(function (v) {
                    //     return JSON.parse(v.id)._macro_id_
                    //   }).join('+'));
                    $(el).attr(
                        "data-macro-values",
                        values
                            .map(function(v) {
                                return JSON.parse(v.id)._macro_id_;
                            })
                            .join("+")
                    );
                } catch (e) {}

                if (values.length == 0 && index < count - 1) {
                    setTimeout(function() {
                        $(el)
                            .closest("li")
                            .remove();
                        $(
                            ".plomino-macros-rule.item-dragging.dragging,#select2-drop-mask," +
                                ".select2-drop.select2-drop-multi.select2-display-none.select2-drop-active"
                        ).remove();
                    }, 1);
                } else {
                    // find the exisitng tags and make them editable
                    //TODO: should only do once
                    if (!self.disabled) {
                        $(el)
                            .find(".select2-search-choice")
                            .each(function(i, el) {
                                $(el).on("click", function(evt) {
                                    evt.preventDefault();
                                    //TODO: how to get the value for this rendered one?
                                    var value = values[i];
                                    var macro = JSON.parse(value.id);
                                    var edit_url = null;
                                    var formid = macro["Form"];

                                    self.edit_macro.bind({ widget: self })(select, formid, macro.title, macro, i);
                                });
                            });
                    }
                    /* sortable choices */
                    /**
                     * @type {HTMLElement}
                     */
                    var draggingChoiceElement = null;
                    var dragChoiceDelayTimer = null;
                    var dragChoiceAllowed = true;
                    $(el)
                        .find(".select2-choices .select2-search-choice")
                        .each(function() {
                            /**
                             * @type {HTMLElement}
                             */
                            var element = this;
                            element.draggable = true;
                            /**
                             * @param {DragEvent} dragEvent DragEvent
                             */
                            element.ondragstart = function startDragChoice(dragEvent) {
                                var macro = element.innerText.trim().replace(/^more_vert/, "");
                                dragEvent.dataTransfer.setData("Text", macro);
                                draggingChoiceElement = element;
                                clearTimeout(dragChoiceDelayTimer);
                                dragChoiceAllowed = true;
                            };
                            /**
                             * @param {DragEvent} dragEvent DragEvent
                             */
                            element.ondragover = function overDragChoice(dragEvent) {
                                dragEvent.preventDefault();
                            };
                            /**
                             * @param {DragEvent} dragEvent DragEvent
                             */
                            element.ondragenter = function enterDragChoice(dragEvent) {
                                /* element - overing element */
                                if (dragChoiceAllowed) {
                                    var detectorClass = ".select2-search-choice-close";
                                    if (
                                        draggingChoiceElement &&
                                        element.innerText !== draggingChoiceElement.innerText &&
                                        element.querySelector(detectorClass) !== null &&
                                        draggingChoiceElement.querySelector(detectorClass) !== null
                                    ) {
                                        swapHTMLElements(draggingChoiceElement, element);
                                        $(el).select2("onSortEnd");
                                        dragChoiceAllowed = false;
                                        dragChoiceDelayTimer = setTimeout(function() {
                                            dragChoiceAllowed = true;
                                        }, 200);
                                    }
                                }
                            };
                        });
                }
                // if last one is not empty add a new one
                if (index == count - 1 && values.length > 0) {
                    // add a new input at the bottom
                    var item = $(self.item).appendTo(self.$el);
                    item.find("input").each(function(index, el) {
                        self.initInput.bind({ widget: self })($(el), []);
                    });
                }
            });
            /* sortable choices */
            /**
             * @type {HTMLElement}
             */
            var draggingRuleElement = null;
            var dragRuleDelayTimer = null;
            var dragRuleAllowed = true;

            self.$el.find("li.plomino-macros-rule").each(function() {
                /**
                 * @type {HTMLElement}
                 */
                var element = this;
                var eDragDisabled = element.querySelector(".select2-search-choice") === null;
                var leftVertDragIcon = element.querySelector(".material-icons:first-child");

                if (eDragDisabled) {
                    leftVertDragIcon.outerHTML =
                        '<i class="material-icons" ' + 'style="color: lightgray; cursor: not-allowed">more_vert</i>';
                    return true;
                }

                leftVertDragIcon.outerHTML = '<i class="material-icons">more_vert</i>';

                element.draggable = true;
                /**
                 * @param {DragEvent} dragEvent DragEvent
                 */
                element.ondragstart = function startDragRule(dragEvent) {
                    var macro = element.innerText.trim().replace(/more_vert/g, "");
                    dragEvent.dataTransfer.setData("Text", macro);
                    draggingRuleElement = element;
                    clearTimeout(dragRuleDelayTimer);
                    dragRuleAllowed = true;
                };
                /**
                 * @param {DragEvent} dragEvent DragEvent
                 */
                element.ondragover = function overDragRule(dragEvent) {
                    dragEvent.preventDefault();
                };
                /**
                 * @param {DragEvent} dragEvent DragEvent
                 */
                element.ondragenter = function enterDragRule(dragEvent) {
                    /* element - overing element */
                    if (dragRuleAllowed) {
                        var detectorClass = ".select2-container";
                        if (
                            draggingRuleElement &&
                            element.innerText !== draggingRuleElement.innerText &&
                            element.querySelector(detectorClass) !== null &&
                            draggingRuleElement.querySelector(detectorClass) !== null
                        ) {
                            swapHTMLElements(draggingRuleElement, element);
                            dragRuleAllowed = false;
                            dragRuleDelayTimer = setTimeout(function() {
                                dragRuleAllowed = true;
                            }, 200);
                        }
                    }
                };
            });
        },
        formatMacro: function(macro) {
            if (macro.text) {
                return macro.text;
            }
            var macro = JSON.parse(macro.id);
            var formid = macro.Form;
            if (formid == "or" || formid == "and" || formid == "nor") {
                return macro.title;
            }
            var type = "do";
            if (formid.startsWith("macro_condition_")) {
                type = "if";
            }
            return (
                '<span class="plomino_edit_macro">' +
                '<i class="material-icons">more_vert</i><i>' +
                type +
                "</i>&nbsp;" +
                macro.title +
                '<i class="icon-pencil"></i></span>'
            );
        },
        edit_macro: function(macro_select, formid, text, data, index) {
            var uniqueId = data._macro_id_;
            if (window["macrojs_edit_macro_hold_" + uniqueId]) {
                return;
            } else {
                window["macrojs_edit_macro_hold_" + uniqueId] = true;
                setTimeout(function() {
                    delete window["macrojs_edit_macro_hold_" + uniqueId];
                }, 1800);
            }
            var self = this.widget;

            // find the url for formid
            var edit_url = null;
            for (var type_ in self.form_urls) {
                self.form_urls[type_].map(function(url) {
                    if (url.id == formid) {
                        edit_url = url.url;
                    }
                });
            }
            var macroid = data["_macro_id_"];

            if (edit_url[0] == "#" && self.ids[macroid]) {
                // It's an AND etc, and its already been added
                return;
            }
            if (edit_url == null) {
                new Modal($(macro_select), {
                    title: "Macro not found",
                    html: "<div>Macro not found</div>",
                }).show();
                return;
            }

            //ensure we have an unique id since select2 doesn't allow two items the same
            var i = 1;
            while (macroid == undefined || self.ids[macroid]) {
                macroid = formid + "_" + i;
                i++;
            }
            data["_macro_id_"] = macroid;
            // try {
            //   console.log('demo', values.map(function (v) {
            //     return JSON.parse(v.id)._macro_id_
            //   }).join('+'));
            // } catch (e) {}
            self.ids[macroid] = true;

            //Special case. Urls that start with # have no popup
            if (edit_url.startsWith("#")) {
                var values = macro_select.select2("data");
                data["title"] = text;
                data["Form"] = formid;
                values.push({ id: JSON.stringify(data), text: text });
                macro_select.select2("data", values);
                self.cleanup_inputs.bind({ widget: self })();
                return;
            }

            // decode the json, work out the form to call
            // do ajax POST request
            // popup modal
            // on success find and remove old json, replace it will new json

            self.backdrop.show();
            self.loading.show(true);

            jQuery
                .ajax({
                    url: edit_url,
                    type: "POST",
                    traditional: true,
                    data: data,
                })
                .done(function(html) {
                    self.loading.hide();
                    self.backdrop.hide();
                    var edit_modal = new Modal(self.$el, {
                        html: html,
                        position: "middle top", // import to be at the top so it doesn't reposition inside the iframe
                        actions: {
                            "input.plominoSave": {
                                onSuccess: function(modal, response, state, xhr, form) {
                                    // If validation_errors is in the form, the form submit failed
                                    if ($(response).find("#validation_errors").length > 0) {
                                        return false;
                                    } else if (response.errors) {
                                        return false;
                                    }
                                    modal.hide();

                                    // find the old value (if there) and replace it
                                    var values = macro_select.select2("data");
                                    // replace the item added with json
                                    var formdata = {};
                                    $.map(response, function(value, key) {
                                        formdata[key] = value.raw;
                                    });
                                    formdata["Form"] = formid;

                                    if (formdata.title == undefined) {
                                        formdata["title"] = text;
                                    }
                                    var i = 1;
                                    var macroid = undefined;
                                    while (macroid == undefined || self.ids[macroid]) {
                                        macroid = formdata["Form"] + "_" + i;
                                        i++;
                                    }
                                    formdata["_macro_id_"] = macroid;
                                    self.ids[macroid] = true;
                                    values[index] = { id: JSON.stringify(formdata), text: "" };
                                    macro_select.select2("data", values);

                                    // console.log('after save', values.map(function (v) {
                                    //   return JSON.parse(v.id)._macro_id_
                                    // }).join('+'));
                                    // console.log('cleanup_inputs called after save');
                                    self.cleanup_inputs.bind({ widget: self })();

                                    return false;
                                },
                                onError: function(response) {
                                    var removeFormErrors = function removeFormErrors() {
                                        document
                                            .querySelectorAll(".plone-modal-body .plominoFieldGroup.error")
                                            .forEach(function(htmlGroupElement) {
                                                htmlGroupElement.classList.remove("field");
                                                htmlGroupElement.classList.remove("error");
                                                var fieldErrorBox = htmlGroupElement.querySelector(".fieldErrorBox");
                                                fieldErrorBox.parentNode.removeChild(fieldErrorBox);
                                            });
                                    };

                                    var errorOnField = function errorOnField(fieldId, msg) {
                                        var field = document.querySelector(
                                            ".plone-modal-body .plominoFieldGroup #" + fieldId
                                        );
                                        var fieldParagraph = field.parentElement.parentElement;
                                        var fieldErrorBox = document.createElement("div");
                                        fieldErrorBox.classList.add("fieldErrorBox");
                                        var fieldErrorBoxError = document.createElement("div");
                                        fieldErrorBoxError.classList.add("error");
                                        fieldErrorBoxError.innerHTML = msg;
                                        fieldErrorBox.appendChild(fieldErrorBoxError);
                                        fieldParagraph.parentNode.insertBefore(fieldErrorBox, fieldParagraph);
                                        fieldParagraph.parentNode.classList.add("field");
                                        fieldParagraph.parentNode.classList.add("error");
                                    };

                                    if (response.responseJSON.errors) {
                                        removeFormErrors();
                                        response.responseJSON.errors.forEach(function(errorObject) {
                                            errorOnField(errorObject.field, errorObject.error);
                                        });
                                    }
                                    return false;
                                },
                            },
                            //                    'input.plominoCancel': {
                            //                        onClick: add_row.hide()
                            //                    }
                        },
                    }).show();
                });
        },
    });

    if (window["MacroWidgetPromise"]) {
        window["MacroWidgetPromiseResolve"](MacroWidget);
    }
    return MacroWidget;
});

// For the macro popup
require(["jquery", "pat-base", "mockup-patterns-modal"], function($, Base, Modal) {
    "use strict";
    var PlominoMacros = Base.extend({
        name: "plominomacropopup",
        parser: "mockup",
        trigger: ".plomino-macro",
        defaults: {},
        init: function() {
            var self = this;
            // Remove any onclick values
            $(".plominoClose", self.$modal).each(function() {
                this.removeAttribute("onclick");
            });
            // Remove validation error links
            $("#validation_errors a").each(function() {
                $(this).replaceWith(function() {
                    return $("<span>" + $(this).html() + "</span>");
                });
            });
            self.render();
        },
        render: function() {
            var self = this;
            // Close the modal when the close button is clicked
            $(".plominoClose", self.$modal)
                .off("click")
                .on("click", function(e) {
                    e.stopPropagation();
                    e.preventDefault();
                    $(e.target).trigger("destroy.plone-modal.patterns");
                });
        },
    });
    if (window["PlominoMacrosPromise"]) {
        window["PlominoMacrosPromiseResolve"](PlominoMacros);
    }
    return PlominoMacros;
});
