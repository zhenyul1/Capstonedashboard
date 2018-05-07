$().ready(function () {
    $sidebar = $('.sidebar');
    $sidebar_img_container = $sidebar.find('.sidebar-background');

    $full_page = $('.full-page');

    $sidebar_responsive = $('body > .navbar-collapse');

    window_width = $(window).width();

    fixed_plugin_open = $('.sidebar .sidebar-wrapper .nav li.active a p').html();

    if (window_width > 767 && fixed_plugin_open == 'Dashboard') {
        if ($('.fixed-plugin .dropdown').hasClass('show-dropdown')) {
            $('.fixed-plugin .dropdown').addClass('show');
        }

    }

    $('.fixed-plugin a').click(function (event) {
        // Alex if we click on switch, stop propagation of the event, so the dropdown will not be hide, otherwise we set the  section active
        if ($(this).hasClass('switch-trigger')) {
            if (event.stopPropagation) {
                event.stopPropagation();
            } else if (window.event) {
                window.event.cancelBubble = true;
            }
        }
    });

    $('.fixed-plugin .background-color span').click(function () {
        $(this).siblings().removeClass('active');
        $(this).addClass('active');

        var new_color = $(this).data('color');

        if ($sidebar.length != 0) {
            $sidebar.attr('data-color', new_color);
        }

        if ($full_page.length != 0) {
            $full_page.attr('filter-color', new_color);
        }

        if ($sidebar_responsive.length != 0) {
            $sidebar_responsive.attr('data-color', new_color);
        }
    });

    $('.fixed-plugin .img-holder').click(function () {
        $full_page_background = $('.full-page-background');

        $(this).parent('li').siblings().removeClass('active');
        $(this).parent('li').addClass('active');


        var new_image = $(this).find("img").attr('src');

        if ($sidebar_img_container.length != 0 && $('.switch-sidebar-image input:checked').length != 0) {
            $sidebar_img_container.fadeOut('fast', function () {
                $sidebar_img_container.css('background-image', 'url("' + new_image + '")');
                $sidebar_img_container.fadeIn('fast');
            });
        }

        if ($full_page_background.length != 0 && $('.switch-sidebar-image input:checked').length != 0) {
            var new_image_full_page = $('.fixed-plugin li.active .img-holder').find('img').data('src');

            $full_page_background.fadeOut('fast', function () {
                $full_page_background.css('background-image', 'url("' + new_image_full_page + '")');
                $full_page_background.fadeIn('fast');
            });
        }

        if ($('.switch-sidebar-image input:checked').length == 0) {
            var new_image = $('.fixed-plugin li.active .img-holder').find("img").attr('src');
            var new_image_full_page = $('.fixed-plugin li.active .img-holder').find('img').data('src');

            $sidebar_img_container.css('background-image', 'url("' + new_image + '")');
            $full_page_background.css('background-image', 'url("' + new_image_full_page + '")');
        }

        if ($sidebar_responsive.length != 0) {
            $sidebar_responsive.css('background-image', 'url("' + new_image + '")');
        }
    });

    $('.switch input').on("switchChange.bootstrapSwitch", function () {

        $full_page_background = $('.full-page-background');

        $input = $(this);

        if ($input.is(':checked')) {
            if ($sidebar_img_container.length != 0) {
                $sidebar_img_container.fadeIn('fast');
                $sidebar.attr('data-image', '#');
            }

            if ($full_page_background.length != 0) {
                $full_page_background.fadeIn('fast');
                $full_page.attr('data-image', '#');
            }

            background_image = true;
        } else {
            if ($sidebar_img_container.length != 0) {
                $sidebar.removeAttr('data-image');
                $sidebar_img_container.fadeOut('fast');
            }

            if ($full_page_background.length != 0) {
                $full_page.removeAttr('data-image', '#');
                $full_page_background.fadeOut('fast');
            }

            background_image = false;
        }
    });
});

type = ['primary', 'info', 'success', 'warning', 'danger'];

demo = {
    initPickColor: function () {
        $('.pick-class-label').click(function () {
            var new_class = $(this).attr('new-class');
            var old_class = $('#display-buttons').attr('data-class');
            var display_div = $('#display-buttons');
            if (display_div.length) {
                var display_buttons = display_div.find('.btn');
                display_buttons.removeClass(old_class);
                display_buttons.addClass(new_class);
                display_div.attr('data-class', new_class);
            }
        });
    },


    initDashboardPageCharts: function () {


        var dataSales = {
            labels: ['9:00AM', '12:00AM', '3:00PM', '6:00PM', '9:00PM', '12:00PM', '3:00AM', '6:00AM'],
            series: [
                [287, 385, 490, 492, 554, 586, 698, 695, 700, 580],
                [800, 800, 800, 800, 800, 800, 800, 800, 800, 800],
                // [23, 113, 67, 108, 190, 239, 307, 308, 439, 410, 410, 509]
            ]
        };

        var optionsSales = {
            lineSmooth: false,
            low: 0,
            high: 1000,
            showArea: false,
            height: "245px",
            axisX: {
                showGrid: false,
            },
            lineSmooth: Chartist.Interpolation.simple({
                divisor: 3
            }),
            showLine: true,
            showPoint: false,
            fullWidth: false
        };

        var responsiveSales = [
            ['screen and (max-width: 640px)', {
                axisX: {
                    labelInterpolationFnc: function (value) {
                        return value[0];
                    }
                }
            }]
        ];

        var chartVib = Chartist.Line('#chartVib', dataSales, optionsSales, responsiveSales);
        var chartTemp = Chartist.Line('#chartTemp', dataSales, optionsSales, responsiveSales);
        var chartNoise = Chartist.Line('#chartNoise', dataSales, optionsSales, responsiveSales);

    },


    showNotification: function (from, align) {
        color = Math.floor((Math.random() * 4) + 1);

        $.notify({
            icon: "nc-icon nc-app",
            message: "Welcome to <b>AI Shop Floor Dashboard</b>."

        }, {
            type: type[color],
            timer: 8000,
            placement: {
                from: from,
                align: align
            }
        });
    }


}