if (!String.prototype.format) {
    String.prototype.format = function(dict) {
        return this.replace(/\{(\w+)\}/g, function(_m) { var m = _m.substr(1, _m.length - 2); if (dict[m]) return dict[m]; return m })
    };
}

function pop_window(url) {
    location = url;
}

var posts_list_page = 0;

function update_posts_list() {
    $.get('/admin/posts?search=' + ux_modal_search.value + '&page=' + posts_list_page, function (data) {
        $('#postlist').html('');
        if (posts_list_page < 0) posts_list_page = 0;
        for (var i = 0; i < data.length; ++i) {
            $('#postlist').append('<input name="postid" type="checkbox" value="{id}" data-title="{title}" data-display="{postType} {lang}" />[{postType} {lang}] {title}<br />'.format(data[i]));
        }
    });
}

function append_file(e) {
	$('#ux_archive_upload').append(window.archive_file);
}

function delete_file(e) {
	$(e).parent().children('div').children('input').val('!!delete!!');
	$(e).parent().hide();
}

function video_change() {
    ux_content.value = ux_china.value + "\n" + ux_nochina.value;
}

function adjust_editor() {
    var frm = mainForm;
    var ptype = $('#ux_type').val() || 'textareas';
    switch (ptype) {
        case "product":
        case "textareas":
            $('#ux_content').show();

            $.get('/admin/uploadlist', function (data) {
                tinymce.init({
                    plugins: "paste,link,image,table",
                    image_list: data,
                    selector: ptype == "textareas" ? "#mainForm textarea" : "textarea#ux_content",
				    file_browser_callback: function(field_name, url, type, win) {
				        if (type == 'image' || type == 'file') $('#file_form input').click();
				    },
                    content_css: "/static/css/base.css",
                    paste_use_dialog : false,
                    paste_auto_cleanup_on_paste : true,
                    paste_convert_headers_to_strong : false,
                    paste_strip_class_attributes : "all",
                    paste_remove_spans : true,
                    paste_remove_styles : true,
                    paste_retain_style_properties : "",
				});
            });
            break;
        default:
            if (tinymce.activeEditor != null) tinymce.activeEditor.destroy();
            $('#ux_content').hide();
            break;
    }

}

function fixdate(e) {
	var t = $(e).val();
	t = t.replace(/[年月日\/\.]/g, '-');
	var a = t.split('-');
	if (a.length < 3) a[2] = '01';
	if (a.length < 2) a[1] = '01';
	if (a[1].length != 2) a[1] = '0' + a[1].substr(0, 1);
	if (a[2].length != 2) a[2] = '0' + a[2].substr(0, 1);
	t = a.join('-').substr(0, 10);
	$(e).val(t);
}

function meta_change(x) {
    $(x).parent().parent().children("div.value").children('input').attr('name', 'meta_' + x.value);
}

function do_submit(form) {
    if (ux_content && ux_content.tagName == 'TEXTAREA' && ux_abstract.value.trim() == '') {
        ux_abstract.value = ux_content.value.replace(/<.*?>|&.*?;/ig, '').substr(0, 100);
    }
    if (ux_type.value == 'archive-gallery') {
        var gac = [];
        $('.photo').each(function () { gac.push({
            'filename': $(this).data('filename'),
            'title': $(this).children('.inputs').children('input').val(),
            'description': $(this).children('.inputs').children('textarea').val()
        }); });
        ux_content.value = JSON.stringify(gac);
    }
    var relates = $('#ux_relates .form-group');
    ux_relates_all.value = '';
    for (var i = 0; i < relates.length; ++i) {
        var r = relates[i];
        var r_id = $(r).children('div').children('input').val();
        var r_rel = $(r).children('div').children('select').val();
        ux_relates_all.value += r_id + ',' + r_rel + ';'
    }
    form.submit();
}

function do_delete() {
	// get selected
	var ids = get_ids();
	if (!ids || !confirm('Sure to delete these items?' + ids))
		return;
	$.post('/admin/delete', {'ref': location.href, 'ids': ids}, function(data) {
	    if (data.error) alert(data.error);
		location.reload();
	});
}

function get_ids() {
	var cs = $('.itemSelect:checked');
    var ids = '';
	for (var i = 0; i < cs.length; ++i)
		ids += $(cs[i]).attr('value') + ',';
	ids = ids.substring(0, ids.length - 1);
	return ids;
}

function redirect(param, value) {
	var s = location.search;
	var pv = param + '=' + encodeURI(value);
	// if (s == '') location = '?' + pv;
	s = s.substr(1);
	var pvs = s.split('&');
	for (var i = 0; i < pvs.length; ++i) {
	    var k = pvs[i].split('=')[0];
	    if (k == 'page') pvs[i] = '';
	    else if (k == param) { pvs[i] = pv; pv = ''; }
	    else if (param == 'by' && k == 'order') pvs[i] = '';
    }

    s = (pvs.join('&') + '&' + pv).replace(/&&/g, '&');
	s = s.replace(/^\&|\&$/, '').replace(/\&+/g, '&');
	if (param == 'by' && s.indexOf('order=') < 0) s += '&order=asc';

	location = '?' + s;
}

function replace_img(name) {
    var img = $('[name="' + name + '"]');
    if (img.length > 0) {
        var p = img.parent();
        var v = img.val();
        img[0].outerHTML = '<input type="text" name="' + name + '" class="form-control" /><img style="max-height: 240px; margin-top: 10px; margin-bottom: 10px" id="preview_' + name + '" class="preview" src="" /><br /><input action="/admin/uploadfile" type="file" class="upload" rel="' + name + '" />';
        $('input[name="' + name + '"]').val(v);
        $('img#preview_' + name).attr('src', v);
        img.remove();
    }
}

$(function () {

    $(document).on('change', 'input.upload', function () {
        var myname = $(this).attr('rel');

        if (this.files.length == 0) return;
        var qc = this.files[0].name.toLowerCase();
        if (!qc.endsWith('.jpg') && !qc.endsWith('.png') && !qc.endsWith('.gif')) {
            alert('Only JPG/PNG/GIF please!');
            $(this).val('');
            return;
        }
        // ready to upload
        var action = $(this).attr('action');
        var formData = new FormData();
        formData.append('file', this.files[0]);
        $.ajax({
            url: action,
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,
            context: myname,
            success: function (data) {
                $('input[rel="' + this + '"]').hide();
                $('input[name="' + this + '"]').val(data['url']);
                //$('input[name="' + this + '"]').attr('type', 'text');
                $('img#preview_' + this).attr('src', data['url']);
				if (typeof(img_upload_callback) != 'undefined') img_upload_callback(data.url);
            }
        });
    });


	$(document).on('change', 'input[rel]', function () {
		switch ($(this).attr('rel')) {
			case 'color':
				if (!this.value.match(/^\#[0-9a-f]{6}$/i)) {
					alert('Color code.');
					this.value = '#0080fa';
				}
				this.value = this.value.toLowerCase();
				var c = this.value, r = parseInt(c.substr(1,2),16), g=parseInt(c.substr(3,2),16), b=parseInt(c.substr(5,2),16);
				var brightness = (0.299*r+0.587*g+0.114*b);
				var text_color = (brightness > 127) ? '#000' : '#fff';
				$(this).css({
					'color': text_color,
					'background-color': this.value
				});
				break;
			case 'numeric':
				var x = +this.value;
				if (isNaN(x)) this.value = '0';
				break;
			case 'array':
				var r = [], f = $(this).parent().children('input[type="hidden"]');
				var siblings = $(this).parent().children('input[rel="array"]');
				for (var i = 0; i < siblings.length; ++i)
					r.push(siblings[i].value);
				f.val('json:' + JSON.stringify(r));
				break;
		}
	});
	$('input[rel="color"]').trigger('change');

	if (typeof(mainForm) != 'undefined') {
		$(document).on('change', 'input.tinymce_upload', function () {

	        if (this.files.length == 0) return;
	        var qc = this.files[0].name.toLowerCase();
			/*
	        if (!qc.endsWith('.jpg') && !qc.endsWith('.png') && !qc.endsWith('.gif')) {
	            alert('请选择 JPG/PNG/GIF 文件！');
	            $(this).val('');
	            return;
	        }
			*/
	        // ready to upload
	        var formData = new FormData();
	        formData.append('file', this.files[0]);
	        $.ajax({
	            url: '/admin/uploadfile',
	            type: "POST",
	            data: formData,
	            processData: false,
	            contentType: false,
	            context: this,
	            success: function (data) {
					top.$('.mce-btn.mce-open').parent().find('.mce-textbox').val(data['url']);//.closest('.mce-window').find('.mce-primary').click();
	            }
	        });
		});
	
		$(document).on('change', '#ux_archive_upload input[type="file"]', function () {

	        if (this.files.length == 0) return;
	        var qc = this.files[0].name.toLowerCase();
	        // ready to upload
	        var formData = new FormData();
	        formData.append('file', this.files[0]);
	        $.ajax({
	            url: '/admin/uploadfile',
	            type: "POST",
	            data: formData,
	            processData: false,
	            contentType: false,
	            context: this,
	            success: function (data) {
					$(this).attr('type', 'input').attr('readonly', 'readonly')
						.attr('name', 'meta_archive_file_' + $(this).parent().parent().children('div').children('select').val())
						.val(data['url']);
	            }
	        });
		});
	
		$(document).on('change', 'select#ux_type', adjust_editor);

	    replace_img('image');
	    replace_img('img_res');
	    if (location.hash != '' && location.hash.substr(0, 6) == "#type=") {
	        var ptype = location.hash.substr(6);
	        ux_type.value = ptype;
	    }

	    adjust_editor();
	
	} else if (typeof(admin_list) != 'undefined') {

	    $(document).on('click', '.selectAll', function () {
	        $('.itemSelect').click();
	    });
	    $(document).on('click', '.itemId', function () {
            var editor = false;
            if (location.href.indexOf('/column') > 0 || location.href.indexOf('/proposed') > 0) editor = 'post';
            else if (location.href.indexOf('/users') > 0) editor = 'account';
            if (!editor) return;
	        if ($(this).text() == '' || $(this).text() == 'None' || $(this).text() == 'ID') return;
	        pop_window('/admin/' + editor + '/' + $(this).text());
	    });
		$(document).on('dblclick', 'tbody.editable .field', function() {
			var $this = $(this);
            if ($this.hasClass('itemId')) return;
			if ($this.children('input').length != 0 || $this.children('div').length != 0) return;
			var text = $this.html();
			$('tbody.editable .field input').each(function(){
			    if ($(this).data('orig') != undefined) {
	                $(this).parent().html($(this).data('orig'));
	            }
			});
			$this.html('<input class="form-control" value="#" data-orig="#" />'.replace(/#/g, text));
		});
		$(document).on('click', '.header', function() {
			var order = location.search.match(/order=(.*?)(&|$)/);
			var by = location.search.match(/by=(.*?)(&|$)/);
			if (!order) order = 'desc'; else order = order[1];
			var newby = $(this).attr('data-field');
			if (!by || by[1] != newby) {
				redirect('by', newby)
			} else {
				redirect('order', order == 'desc' ? 'asc' : 'desc')
			}
		});
		$(document).on('click', '.image img, .banner img', function () {
			$('#img_upload_tmp').remove();
			var t = $(this);
			img_upload_callback = function (url) {
				$('#img_upload_tmp').remove();
				t.attr('src', url);
				var data = { id: +t.parent().siblings('.itemId').text(), source: location.href };
				data[t.parent().data('field')] = url;
				$.post('/admin/edit', data, function () {
					location.reload();
				});
			};
			$('#admin_list').append('<div style="position:absolute;display:block;width:1px;height: 1px;top:-1000px;" id="img_upload_tmp"><textarea name="img_upload_tmp_image"></textarea></div>');
			replace_img('img_upload_tmp_image');
			$('#img_upload_tmp input').click();			
		});
		var apply_modify = function(t, v) {
			t = $(t);
			v = (typeof(v) != 'undefined') ? v : t.val();
			var id = t.parent().siblings('.itemId').text();
			var data = { 'id' : id, 'source': location.href };
			data[t.parent().data('field')] = v;
			$.ajax({
	            method: 'POST',
				url: '/admin/edit',
				data: data,
				context: t
			}).done(function() {
			    if (this[0].tagName == 'INPUT' && (this.attr('type') || 'text') == 'text')
				    this.parent().html(v);
			});
		};
		$(document).on('keyup', 'tbody.editable .field input', function (){
	        if ((event.keyCode || event.which) != 13) return;
	        apply_modify(this);
	    });
		$(document).on('change', 'tbody.editable .field input, tbody.editable .field select', function() {
		    if (this.type == 'checkbox') val = this.checked ? 1 : 0; else val = $(this).val();
		    apply_modify(this, val);
	    });
	

		function replace_list_img() {
		    $('tbody .image, tbody .banner').each(function (){
		        var s = $(this).html();
		        if (s) $(this).html('<img src="' + s + '" />')
		    });
		}

	    var by = (location.search.match(/by=(.*?)(\&|$)/) || ['', 'id'])[1];
	    var order = (location.search.match(/order=(.*?)(\&|$)/) || ['', 'asc'])[1];
	    $('td.field').each(function (i, x) {
	        var f = $(x).data('field');
	        if (f == by) $(x).addClass(order);
	    });

	    var filter_type = (location.search.match(/filter_type=(.*?)(\&|$)/) || ['', ''])[1];
	    $('#ux_filter').val(filter_type);


	    $('#start-order').click(function() {
	        $('#admin_list').tableDnD({
	                onDragStart: function(table, row) {
	                    $('#save-order').show();
	                }
	        });
	    });

	    $('#save-order').click(function() {
	        var data = { 'q': '{{q}}' };
	        $('tr.item').each(function(){
	            var item = $(this).children().first().children('input');
	            var id = item.val();
	            var order = item.attr('data-order');
	            if (order != $(this).index())
	                data[id] = $(this).index();
	        });
	        $.post('/admin/change_order', data, function() { location.reload(); });
	    });

	    $('#ux_filter').change(function(){
	        redirect('filter_type', ux_filter.value);
	    });

	    $('#ux_batch').change(function(){
	        var ids = get_ids();
	        if (!ids || !ux_batch.value || !confirm('确认要转移栏目吗？')) {
	            return;
	        }
	        $.post('/admin/transfer_col', {'col_id': +$('#ux_batch').val().substr(3), 'ids': ids }, function(data) {
	            if (data.error) alert(data.error); location.reload();
	        });
	    });

	    replace_list_img();
	}
        
    var loc = location.href;
    if (location.search) loc = loc.substr(0, loc.indexOf('?'));
    $('a.nav-link').each(function (i, x) {
        if (loc.endsWith(x.href) || loc.match($(x).data('alt-href') || '^$')) $(x).addClass('active').parent().addClass('active');
    });
});