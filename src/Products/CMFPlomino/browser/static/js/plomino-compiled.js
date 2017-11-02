require(["jquery","pat-base","mockup-patterns-texteditor"],function(e,t,r){"use strict";return t.extend({name:"plominoformula",parser:"mockup",trigger:".plomino-formula",defaults:{},init:function(){var t=this;t.$el.width();t.$el.hide();var i=e("<pre></pre>");i.appendTo(t.$el.parent()),t.ace=new r(i),t.ace.init(),setTimeout(function(){t.ace.editor.getSession().setMode("ace/mode/python"),i.css("width","100%"),t.ace.editor.resize(),t.ace.setText(t.$el.val()),t.ace.editor.on("change",function(){t.$el.val(t.ace.editor.getValue())})},200)}})}),define("/Users/quang.nguyen/PlominoWorkflow/src/Products/CMFPlomino/browser/static/js/formula.js",function(){}),require(["jquery","pat-base"],function(e,t){"use strict";return t.extend({name:"plominotable",parser:"mockup",trigger:".plomino-table",defaults:{},init:function(){var e=this;e.init_search(),e.init_sorting(),e.refresh({}),e.params={}},refresh:function(){var t=this;if(t.options.source){t.$el.find("tr:not(.header-row)").remove();var r=t.$el.find("tr.header-row.count");r.find("td").text("Loading..."),e.get(t.options.source,t.params,function(e){for(var i="",n=0;n<e.rows.length;n++){var o=e.rows[n];if(i+="<tr>","True"!==t.options.hideCheckboxes&&(i+="<td>",i+='<input type="checkbox" name="sdoc" value="'+o[0]+'" />',i+="</td>"),i+='<td><a href="'+t.options.source+"/../document/"+o[0]+'">'+o[1]+"</a></td>",o.length>2)for(var a=2;a<o.length;a++)i+="<td>"+o[a]+"</td>";i+="</tr>"}e.rows.length>1?r.find("td").text(e.rows.length+" documents"):r.find("td").text(e.rows.length+" document"),r.before(i)})}},init_search:function(){var t=this,r=e('<input type="text" placeholder="Search"/>');t.$el.before(r),r.on("submit",function(){return!1});var i,n=!1;r.on("keyup",function(){var r=e('#plomino-view input[type="text"]').val();r.length<3&&!n||(i&&clearTimeout(i),i=setTimeout(function(){t.params.search=r,t.refresh(),n=!!r,clearTimeout(i)},1e3))})},init_sorting:function(){var t=this;t.$el.find("th").on("click",function(){t.$el.find("th").removeClass("icon-down-dir icon-up-dir");var r=e(this).attr("data-column");r==t.params.sorton?t.params.reverse=1==t.params.reverse?0:1:(t.params.sorton=r,t.params.reverse=0),0===t.params.reverse?e(this).addClass("icon-down-dir"):e(this).addClass("icon-up-dir"),t.refresh()})}})}),define("/Users/quang.nguyen/PlominoWorkflow/src/Products/CMFPlomino/browser/static/js/table.js",function(){}),require(["jquery","pat-base"],function(e,t){"use strict";return t.extend({name:"plominodynamic",parser:"mockup",trigger:"#plomino_form",defaults:{},init:function(){var t=this;t.refresh(this.$el),this.$el.find(":input").change(function(e){t.refresh(e.target)}),t.hidewhen_html={},t.$el.find(".plomino-hidewhen").each(function(r,i){t.hidewhen_html[e(i).attr("data-hidewhen")]=e(i).html()})},refresh:function(t){var r=this,i=r.getCurrentInputs();r.options.docid&&(i._docid=r.options.docid),i._hidewhens=r.getHidewhens(),i._fields=r.getDynamicFields(),i._validation=t.id,(i._hidewhens.length>0||i._fields.length>0)&&e.post(r.options.url+"/dynamic_evaluation",e.param(i,!0),function(e){r.applyHidewhens(e.hidewhens),r.applyDynamicFields(e.fields)},"json")},getCurrentInputs:function(){var t,r,i,n,o,a,s={},l=e("form").serialize().split("&");for(t in l)i=(r=l[t].split("="))[0],n=decodeURIComponent(r[1].replace(/\+/g,"%20")),i in s&&(o=s[i],a=[],Array.isArray(o)||(a.push(o),o=a),o.push(n),n=o),s[i]=n;return s},getHidewhens:function(){var t=[];return this.$el.find(".plomino-hidewhen").each(function(r,i){t.push(e(i).attr("data-hidewhen"))}),t},getDynamicFields:function(){var t=[];return this.$el.find(".dynamicfield").each(function(r,i){t.push(e(i).attr("data-dynamicfield"))}),t},applyHidewhens:function(e){for(var t=this,r=0;r<e.length;r++){var i=e[r][0],n=e[r][1],o=e[r][2],a=t.$el.find('.plomino-hidewhen[data-hidewhen="'+i+'"]');n?(a.hide(),o&&(a.html(t.hidewhen_html[i]),a.find(":input").change(function(e){t.refresh(e.target)}))):a.show()}},applyDynamicFields:function(e){for(var t=this,r=0;r<e.length;r++){var i=e[r][0],n=e[r][1];t.$el.find('.dynamicfield[data-dynamicfield="'+i+'"]').text(n)}}})}),define("/Users/quang.nguyen/PlominoWorkflow/src/Products/CMFPlomino/browser/static/js/dynamic.js",function(){}),require(["jquery","pat-base","mockup-patterns-modal","mockup-patterns-select2"],function(e,t,r,i){"use strict";return t.extend({name:"plominodatagrid",parser:"mockup",trigger:".plomino-datagrid",defaults:{},init:function(){var e=this;if(e.fields=e.$el.attr("data-fields").split(","),e.columns=e.$el.attr("data-columns").split(","),e.input=e.$el.find('input[type="hidden"]'),e.values=JSON.parse(e.input.val()),e.rows=JSON.parse(e.$el.find("table").attr("data-rows")),e.col_number=e.fields.length,e.associated_form=e.$el.attr("data-associated-form"),e.$el.attr("data-form-urls"))e.form_urls=JSON.parse(e.$el.attr("data-form-urls"));else{var t=/(.*)\/(.*)\/OpenForm\?(.*)/.exec(e.$el.attr("data-form-url"))[2];e.form_urls=[{url:e.$el.attr("data-form-url"),id:t}]}e.render()},setValue:function(e){var t=this;t.input.val(e),t.input.change()},render:function(){for(var t=this,i=t.$el.find("table"),n="<tr><th></th>",o=0;o<t.col_number;o++)n+="<th>"+t.columns[o]+"</th>";n+="</tr>";for(var a=0;a<t.rows.length;a++){for(var s=t.form_url,l=t.associated_form,d=0;d<t.form_urls.length;d++)if(t.form_urls[d].id==l){s=t.form_urls[d].url;break}n+='<tr><td class="actions"><a class="edit-row" href="'+(s+="&"+e.param(t.values[a]))+'" data-formid="'+l+'"><i class="icon-pencil"></i></a>',n+='<a class="remove-row" href="#"><i class="icon-cancel"></i></a>',n+='<a class="up-row" href="#"><i class="icon-up-dir"></i></a>',n+='<a class="down-row" href="#"><i class="icon-down-dir"></i></a></td>';for(o=0;o<t.col_number;o++)n+="<td>"+(t.rows[a][o]?t.rows[a][o]:"")+"</td>";n+="</tr>"}var c="";if(t.form_urls.length>1){for(c='<select class="form_select" data-pat="width:10em">',o=0;o<t.form_urls.length;o++){var u=t.form_urls[o];c+='<option value="'+u.url+'">'+u.title+"</option>"}c+="</select>"}void 0!=t.form_urls[0]&&(n+='<tr><td class="actions" colspan="5">'+c+'<a class="add-row" href="'+t.form_urls[0].url+'" data-formid="'+t.form_urls[0].id+'"><i class="icon-plus"></i></a></td></tr>'),i.html(n);var f=t.$el.find(".add-row");t.$el.find(".form_select").each(function(r,i){var n;e(i).change(function(){for(var r=e(i).val(),o=0;o<t.form_urls.length;o++)if(t.form_urls[o].url==r){n=t.form_urls[o].id;break}f.attr("href",r).attr("data-formid",n)})});var p=r.extend({render:function(t){var r=this;r.emit("render"),r.options.render.apply(r,[t]),r.emit("rendered"),e(".plominoClose").attr("onclick",'$(".plone-modal-close").click()')}});f.click(function(e){e.stopPropagation(),e.preventDefault();var r=t.$el.find(".add-row i");!function(e){new p(r,{ajaxUrl:f.attr("href"),ajaxType:"POST",position:"middle top",actions:{"input.plominoSave":{onSuccess:t.add.bind({grid:t,formid:f.attr("data-formid")}),onError:function(){return e.alert(response.responseJSON.errors.join("\n")),!1}}}}).show()}(window.top)}),t.$el.find(".edit-row").each(function(r,i){var n=e(i).attr("href").split("?",2);e(i).on("click",function(o){o.preventDefault(),jQuery.ajax({url:n[0],type:"POST",data:n[1]}).done(function(n){new p(t.$el,{html:n,position:"middle top",actions:{"input.plominoSave":{onSuccess:t.edit.bind({grid:t,row:r,formid:e(i).attr("data-formid")}),onError:function(){return window.alert(response.responseJSON.errors.join("\n")),!1}}}}).show()})})}),t.$el.find(".remove-row").each(function(r,i){e(i).click(function(){t.remove(t,r)})}),t.$el.find(".up-row").each(function(r,i){e(i).click(function(){t.up(t,r)})}),t.$el.find(".down-row").each(function(r,i){e(i).click(function(){t.down(t,r)})})},add:function(e,t,r,i,n){var o=this.grid,a=this.formid;if(!t.errors){e.hide();for(var s={},l=[],d=(n.serializeArray(),0);d<o.col_number;d++)void 0!=o.fields[d]&&o.fields[d]in t?l.push(t[o.fields[d]].rendered):l.push("");for(var c in t)s[c]=t[c].raw;s.Form=a,o.values.push(s),o.setValue(JSON.stringify(o.values)),o.rows.push(l),o.render()}return!1},edit:function(e,t,r,i,n){var o=this.grid,a=this.row,s=this.formid;if(!t.errors){e.hide();for(var l=[],d=0;d<o.col_number;d++)void 0!=o.fields[d]&&o.fields[d]in t?l.push(t[o.fields[d]].rendered):l.push("");o.values[a].Form=s;for(var c in t)o.values[a][c]=t[c].raw;o.setValue(JSON.stringify(o.values)),o.rows[a]=l,o.render()}return!1},remove:function(e,t){return e.values.splice(t,1),e.setValue(JSON.stringify(e.values)),e.rows.splice(t,1),e.render(),!1},up:function(e,t){if(0!=t)return e.values.splice(t-1,0,e.values.splice(t,1)[0]),e.setValue(JSON.stringify(e.values)),e.rows.splice(t-1,0,e.rows.splice(t,1)[0]),e.render(),!1},down:function(e,t){if(t!=e.values.length-1)return e.values.splice(t,0,e.values.splice(t+1,1)[0]),e.setValue(JSON.stringify(e.values)),e.rows.splice(t,0,e.rows.splice(t+1,1)[0]),e.render(),!1}})}),define("/Users/quang.nguyen/PlominoWorkflow/src/Products/CMFPlomino/browser/static/js/datagrid.js",function(){}),require(["jquery","pat-base"],function(e,t){"use strict";return t.extend({name:"plominomultipage",parser:"mockup",trigger:'body.template-page.portaltype-plominoform #plomino_form input[name="plomino_current_page"]',defaults:{},init:function(){var e=this.$el.parents("#plomino_form").attr("action"),t={multipage:"multipage"};history.pushState(t,"",e)}})}),define("/Users/quang.nguyen/PlominoWorkflow/src/Products/CMFPlomino/browser/static/js/multipage.js",function(){}),require(["jquery","pat-base","mockup-patterns-modal","mockup-patterns-select2","mockup-patterns-sortable","mockup-patterns-backdrop","mockup-utils","pat-registry"],function(e,t,r,i,n,o,a,s){"use strict";return t.extend({name:"plominomacros",parser:"mockup",trigger:".plomino-macros",defaults:{},init:function(){var e=this;e.form_urls=JSON.parse(e.$el.attr("data-form-urls"));var t=[];for(var r in e.form_urls)t.push({text:r,children:e.form_urls[r].map(function(e){if(void 0!=e.title)return{id:e.id,text:e.title}})});e.select2_args={data:t,separator:"\t",multiple:!0,allowNewItems:!1,placeholder:"add a new rule",formatSelection:e.formatMacro};e.item=e.$el.find("li").last()[0].outerHTML,e.$el.prepend(""),e.ids={};var i=0;e.$el.find("input").each(function(t,r){var n=[];""!=r.value&&(n=r.value.split("\t")),void 0==n.map&&(n=[n]),n=n.map(function(t){if(""!=t){var r=JSON.parse(t);return r._macro_id_&&(e.ids[r._macro_id_]=!0),{id:t,text:""}}}),e.initInput.bind({widget:e})(r,n),i++}),e.cleanup_inputs.bind({widget:e})(),e.backdrop=new o(e.$el,{closeOnEsc:!0,closeOnClick:!1}),e.loading=a.Loading({backdrop:e.backdrop})},initInput:function(t,r){var n=this.widget;new i(e(t),n.select2_args);var o=e(t);o.select2("data",r),o.change(function(t){var r=e(t.target);if(void 0!=t.added){var i=t.added.id,o=t.added.text,a=r.select2("data");a.pop(),r.select2("data",a),n.edit_macro.bind({widget:n})(r,i,o,{},a.length)}else if(void 0!=t.removed){t.removed.id;n.cleanup_inputs.bind({widget:n})()}return!1})},cleanup_inputs:function(){var t=this.widget,r=t.$el.find(".select2-container").size();t.$el.find(".select2-container").each(function(i,o){var a=e(o),s=a.select2("data");0==s.length&&i<r-1?e(o).closest("li").remove():(e(o).find(".select2-search-choice").each(function(r,i){e(i).on("click",function(e){e.preventDefault();var i=s[r],n=JSON.parse(i.id),o=n.Form;t.edit_macro.bind({widget:t})(a,o,n.title,n,r)})}),new n(e(o).find(".select2-choices"),{selector:".select2-search-choice",drop:function(){e(o).select2("onSortEnd")}})),i==r-1&&s.length>0&&e(t.item).appendTo(t.$el).find("input").each(function(r,i){t.initInput.bind({widget:t})(e(i),[])})}),new n(t.$el,{selector:".plomino-macros-rule"})},formatMacro:function(e){if(e.text)return e.text;var t=(e=JSON.parse(e.id)).Form;if("or"==t||"and"==t||"nor"==t)return e.title;var r="do";return t.startsWith("macro_condition_")&&(r="if"),'<span class="plomino_edit_macro"><i>'+r+"</i>&nbsp;"+e.title+'<i class="icon-pencil"></i></span>'},edit_macro:function(t,i,n,o,a){var s=this.widget,l=null;for(var d in s.form_urls)s.form_urls[d].map(function(e){e.id==i&&(l=e.url)});c=o._macro_id_;if("#"!=l[0]||!s.ids[c])if(null!=l){for(var c=o._macro_id_,u=1;void 0==c||s.ids[c];)c=i+"_"+u,u++;if(o._macro_id_=c,s.ids[c]=!0,l.startsWith("#")){var f=t.select2("data");return o.title=n,o.Form=i,f.push({id:JSON.stringify(o),text:n}),t.select2("data",f),void s.cleanup_inputs.bind({widget:s})()}s.backdrop.show(),s.loading.show(!0),jQuery.ajax({url:l,type:"POST",traditional:!0,data:o}).done(function(o){s.loading.hide(),s.backdrop.hide();new r(s.$el,{html:o,position:"middle top",actions:{"input.plominoSave":{onSuccess:function(r,o,l,d,c){if(e(o).find("#validation_errors").length>0)return!1;if(o.errors)return!1;r.hide();var u=t.select2("data"),f={};return e.map(o,function(e,t){f[t]=e.raw}),f.Form=i,void 0==f.title&&(f.title=n),u[a]={id:JSON.stringify(f),text:""},t.select2("data",u),s.cleanup_inputs.bind({widget:s})(),!1},onError:function(){return window.alert(response.responseJSON.errors.join("\n")),!1}}}}).show()})}else new r(e(t),{title:"Macro not found",html:"<div>Macro not found</div>"}).show()}})}),require(["jquery","pat-base","mockup-patterns-modal"],function(e,t,r){"use strict";return t.extend({name:"plominomacropopup",parser:"mockup",trigger:".plomino-macro",defaults:{},init:function(){var t=this;e(".plominoClose",t.$modal).each(function(){this.removeAttribute("onclick")}),e("#validation_errors a").each(function(){e(this).replaceWith(function(){return e("<span>"+e(this).html()+"</span>")})}),t.render()},render:function(){e(".plominoClose",this.$modal).off("click").on("click",function(t){t.stopPropagation(),t.preventDefault(),e(t.target).trigger("destroy.plone-modal.patterns")})}})}),define("/Users/quang.nguyen/PlominoWorkflow/src/Products/CMFPlomino/browser/static/js/macros.js",function(){}),require(["jquery","pat-base"],function(e,t,r){"use strict";return t.extend({name:"plominorefresh",parser:"mockup",trigger:"body.template-edit.portaltype-plominofield",defaults:{},init:function(){var t=this;e("#form-widgets-field_type").change(function(e){t.refresh(e)})},refresh:function(t){var r=e("<input>").attr("type","hidden").attr("name","update.field.type").val("1");e("form#form").append(e(r)),e("form#form").submit()}})}),define("/Users/quang.nguyen/PlominoWorkflow/src/Products/CMFPlomino/browser/static/js/refresh.js",function(){});
//# sourceMappingURL=plomino-compiled.js.map