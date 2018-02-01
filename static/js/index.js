(function () {
    function $c(cname) {
        return document.getElementsByClassName(cname)[0];
    }

    function pos() {
        var base_x = window.innerWidth / 2 - 100, base_y = 0;

        function set_pos(cname, x_offset, y_offset) {
            var ele = $c(cname);
            if (Math.abs(x_offset) < 1) x_offset *= window.innerWidth;
            if (Math.abs(y_offset) < 1) y_offset *= window.innerHeight;
            //if (cname == 'rjsx' || cname == 'xtzt')
            //    ele.style.right = (base_x + x_offset) + 'px';
            //else
            ele.style.left = (base_x + x_offset) + 'px';
            ele.style.top = (base_y + y_offset) + 'px';
        }
        if (window.innerWidth >= 900) {
            set_pos('rjsx', -200, .05);
            set_pos('xtzt', -140, .05 * window.innerHeight + 150);
            set_pos('yjsnzlt', 120, 80);
            set_pos('yzxdsx', 200, 0);
            set_pos('zlk', 50 * 6, 200);
        } else {
            set_pos('rjsx',0,0);
            set_pos('xtzt',0,0);
            set_pos('yjsnzlt',0,0);
            set_pos('yzxdsx',0,0);
            set_pos('zlk',0,0);
        }
    }

    addEvent(window, "resize", pos);
    addInit(pos);

})();