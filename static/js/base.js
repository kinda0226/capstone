/**
 * Created by ZTH on 01.11.15.
 */

var init_funcs = [];

var addEvent = function(object, type, callback) {
    // if (object == null || typeof(object) == 'undefined') return;
    // var objs = [];
    // if (typeof(object) == 'string') {
    //     objs = document.getElementsByClassName(object);
    // } else {
    //     objs = [object];
    // }
    // for (var i = 0; i < objs.length; ++i) {
    //     var obj = objs[i];
    //     if (obj.addEventListener) {
    //         obj.addEventListener(type, callback, false);
    //     } else if (object.attachEvent) {
    //         obj.attachEvent("on" + type, callback);
    //     } else {
    //         obj["on" + type] = callback;
    //     }
    // }
    $(document).on(type, object, callback);
};

var addInit = function(func) {
    init_funcs.push(func);
};

function adjustArticles() {
	if (location.search.indexOf('type=tile') > 0) {
		var crow = parseInt(parseInt($('#content').css('width')) / 280);
		var ars = $('article');
		ars.css('clear', '');
		for (var i = crow; i < ars.length; i += crow) {
			$(ars[i]).css('clear', 'both');
		}
	}
}

addInit(adjustArticles);

function init() {

    if ($('#membership_ad').length > 0) {
        $.get('/static/buy.html', function(html) { $('#membership_ad').html(html); });
    }

    addEvent(".pointer", "click", function(e) {
        var rel = this.getAttribute("rel");
        if (typeof(rel) != 'undefined' && rel) {
            location = rel;
        }
    });

    addEvent("wx-icon", "mouseenter", function(e) {
        document.getElementsByClassName("wx-qrcode")[0].style.display = "block";
    });

    addEvent("wx-icon", "mouseleave", function(e) {
        document.getElementsByClassName("wx-qrcode")[0].style.display = "none";
    });

    $('a[rel!=""]').each(function (e) {
        var rel = this.getAttribute('rel');
		if (typeof(rel) == 'undefined' || rel == null)
			return;
        if (rel.indexOf('http://') == 0) {
            this.setAttribute('href', rel);
        } else if (rel.indexOf('/?p=') > 0) {
            this.setAttribute('href', '/post/' + rel.substr(rel.indexOf('?p=') + 3));
        }
    });
	
	$(window).bind('resize', adjustArticles);

    for (var i = 0; i < init_funcs.length; ++i)
        init_funcs[i]();

    // ads
    $('[id].pointer').each(function (i, x) {
        if (x.id.match(/^frx_\d+$/)) {
            $(x).css({
               'margin-top': '20px',
               'margin-bottom': '20px'
            });
            if ($(x).width() > $(x).height()) {
                var num = parseInt($('.articles.list').children().length / 2 + (Math.random() * 3 - 1));
                $(x.outerHTML).insertAfter($('.articles.list').children(':nth-child(' + num + ')'));
            }
        }
    });
    
    // like
    
    $('.icons span').css('cursor', 'pointer').bind('click', function() {
        var which = $(this);
        if (which.index() == 0) return;
        $.get('/like?action=' + (2-which.index()) + '&post=' + (which.parent().data('id')), function (data) {
            which.html(which.children('i')[0].outerHTML + data);
        });
    });
}

function searchSubmit() {
    location = '/search?q=' + ux_search.value;
    return false;
}

// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(init);