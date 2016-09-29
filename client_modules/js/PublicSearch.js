function getFormData(formId) {
    //create requestObj from search form
    var searchForm = $(formId).find(':input').not($('button'));
    var formData = {};
    $.each(searchForm, function (formData) {
        return function (index, inputItem) {
            switch ($(inputItem).attr('type')) {
                case 'checkbox':
                    if ($(inputItem).is(':checked')) {
                        formData[$(inputItem).attr('name')] = $(inputItem).val();
                    }
                    break;

                case 'radio':
                    if ($(inputItem).is(':checked')) {
                        formData[$(inputItem).attr('name')] = $(inputItem).val();
                    }
                    break;

                default:
                    formData[$(inputItem).attr('name')] = $(inputItem).val();
            }
        }
    }(formData));

    return formData;
}

function chooseSlideDirection(targetId) {
    var Elem = $(targetId);
    if ($(Elem).css("display") == "none") { Elem.slideDown(); }
    else { Elem.slideUp(); }
}


function clearForm(oForm) {

    var elements = oForm.elements;

    oForm.reset();

    for (i = 0; i < elements.length; i++) {

        field_type = elements[i].type.toLowerCase();

        switch (field_type) {

            case "text":
                if (elements[i].name == "start"){
                    elements[i].value = 1;
                    break;
                }
                elements[i].value = "";
                break;

            case "password":
            case "textarea":
                elements[i].value = "";
                break;

            case "radio":
            case "checkbox":
                if (elements[i].checked) {
                    elements[i].checked = false;
                }
                break;

            case "select":
            case "select-one":
            case "select-multi":
                elements[i].selectedIndex = 0;
                break;

            default:
                break;
        }
    }
}

function checkPage(Page,increment) {
    if (!$.isNumeric(Page)) {
        return false;
    }
    var pageNumber = Number(Page);
    if (pageNumber + increment  >= 1 && pageNumber + increment <= Number($("#lastpage").val())) {
        return true;
    }
    else {
        return false;
    }
}

$(document).ready(function () {
    var display;
    // $('#searchfields').click(function() {
    //     chooseSlideDirection('#searchfieldsTarget');
    // });


    $('#next').click(function() {
        var $n = $("#start");
        if (checkPage($n.val(),1)) {
            $n.val(Number($n.val()) + 1);
            submitForm(display);
        }
    });

    $('#prev').click(function() {
        var $n = $("#start");
        if (checkPage($n.val(),-1)) {
            $n.val(Number($n.val()) - 1);
            submitForm(display);
        }
    });

    $('.expandInfo').click(function() {
      chooseSlideDirection("#" + $(this).attr('id') + "Target");
      $('.expandedInfo').not("#" + $(this).attr('id') + "Target").slideUp();
    });

    $("#acceptterms").click(function () {
        $(this).css({
            background: "",
            border: ""
        });
    });

    $('#search-reset').click(function () {
        clearForm($('#search')[0]);
        $('#resultsPanel').html('');
    });

    $('#search-list, #search-full, #search-grid').click(function () {
        submitForm($(this).attr('name'));

    });

    $('#search input[type=text]').keypress(function(event) {
        if (event.which == 13) {
            submitForm('search-list');
        }
    });


    $('[name]').map(function () {
        var elementID = $(this).attr('name');
        var source = $(this).attr('source');
        if (source) {
            // console.log(elementID);
            $(this).autocomplete({
                source: function (request, response) {
                    $.ajax({
                        url: "../../suggest/?",
                        dataType: "json",
                        data: {
                            q: request.term,
                            elementID: elementID,
                            source: source
                        },
                        success: function (data) {
                            response(data);
                        }
                    });
                },
                minLength: 2
            });
        }
    });

    $.tablesorter.addParser({
        id: 'sortkey',
        is: function(s, table, cell) {
            return false;
        },
       format: function(s, table, cell, cellIndex) {
           var $cell = $(cell);
           return $cell.attr('data-sort') || s;
           //return $(cell)[0].firstElementChild.getAttribute("data-sort");
        },
        type: 'text'
    });

    var submitForm = function(displaytype) {
        var formData = getFormData('#search');
        formData[displaytype] = '';

        if (!formData['acceptterms']) {
            $("#acceptterms")
                .css({
                    background: "yellow",
                    border: "3px red solid"
                });
        }
        else {
            $('#waitingImage').css({
                display: "block"
            });

            // chooseSlideDirection('#searchfieldsTarget');
            // chooseSlideDirection('#searchfields');

            $.post("../results/", formData).done(function (data) {
                $('#resultsPanel').html(data);

                $('#resultsListing').tablesorter({
                    theme: 'blue',
                    headers: {
                        1: { sorter:'sortkey' }
                    }
                });

                $('[id^=Facet]').map(function () {
                   $(this).tablesorter({theme: 'blue'});
                });

                $('#tabs').tabs({ active: 0 });

                $('#waitingImage').css({
                    display: "none"
                });
                xga('send', 'pageview', { 'page': 'search' }, trackingid);
            });
        }
    };

    $(document).on('click', '#select-items', function() {
        if ($('#select-items').is(':checked')) {
            $('#selectedItems input:checkbox').prop('checked', true);
        } else {
            $('#selectedItems input:checkbox').prop('checked', false);
        }
    });

    $(document).on('click', '.sel-item', function () {
        $('#select-items').prop('checked', false);
    });


    $(document).on('click', '#summarize', function () {
        var formData = getFormData('#selectedItems');
        formData[$(this).attr('name')] = '';

        if ($(this).attr('id') == 'summarize') {
            $('#waitingImage').css({
                display: "block"
            });

            $.post("../statistics/", formData).done(function (data) {
                $('#statsresults').html(data);

                $('#statsListing').tablesorter({theme: 'blue'});
                $('#waitingImage').css({
                    display: "none"
                });
                xga('send', 'pageview', { 'page': 'summarize' }, trackingid);
            });
//        } else if ($(this).attr('id') == 'downloadstats') {
//            $.post("../statistics/", formData).done(function (data) {
//                alert( "success" );
//            });
//            xga('send', 'pageview', { 'page': 'summarize/download' }, trackingid);
        }
//      xga('send', 'pageview', { 'page': 'statistics' }, trackingid);
    });

    $(document).on('click', '.map-item', function () {
        var Elem = $(this).siblings('.small-map');
        if ($(Elem).css("display") == "none") {
            var marker = ($(Elem).attr('data-marker'));
            console.log('img ' + marker);
            $(Elem).html('<iframe width="600" height="450" frameborder="0" style="border:0" src="https://www.google.com/maps/embed/v1/place?q='+marker+'&key=AIzaSyBeDzud2rQvl70-TFgsdlMa9vsUl_vidZk&maptype=satellite" allowfullscreen></iframe>');
            Elem.slideDown();
            xga('send', 'pageview', { 'page': 'map/inline' }, trackingid);
        }
        else {
            Elem.slideUp();
        }
    });

    $(document).on('click', '.facet-item', function () {
        var key = ($(this).attr('data-facetType'));
        var value = ($(this).text());

        // reset page number to 1 -- this is a new search!
        $("#start").val( 1 );

        if (key != '') {
            console.log(key + ': ' + value);
            var keyElement = $('#' + key);
            var keyElQual = $('#' + key + '_qualifier');
            if (keyElement != null) {
                keyElement.val(value);
                if (keyElQual != null) {
                    keyElQual.val('exact');
                }
            }
        }
        var formData = getFormData('#search');
        // TODO: CURRENTLY DEFAULT TO SEARCH-LIST BUT SHOULD HAVE A PERSISTENT DISPLAY TYPE? CURRENTLY DOESN'T ON DEV
        formData['search-list'] = '';

        $.post("../results/", formData).done(function (data) {
            $('#resultsPanel').html(data);

            $('#resultsListing').tablesorter({
                theme: 'blue',
                headers: {
                    1: { sorter:'sortkey' }
                }
            });

            $('[id^=Facet]').map(function () {
               $(this).tablesorter({theme: 'blue'});
            });

            $('#tabs').tabs({ active: 1 });
            xga('send', 'pageview', { 'page': 'search/refine' }, trackingid);
        });
    });

    $(document).on('click', '#map-bmapper, #map-google', function () {
        var formData = getFormData('#selectedItems');
        formData[$(this).attr('name')] = '';

        if ($(this).attr('id') == 'map-bmapper') {
            $.post("../bmapper/", formData).done(function (data) {
                window.open(data, '_blank');
            });
            xga('send', 'pageview', { 'page': 'map/bmapper' }, trackingid);
        } else if ($(this).attr('id') == 'map-google') {
            $.post("../gmapper/", formData).done(function (data) {
                $('#maps').html(data);
            });
            xga('send', 'pageview', { 'page': 'map/google' }, trackingid);
        }
    });
// we need to make sure this gets done in the event the page is created anew (e.g. via a pasted URL)
$('#tabs').tabs({ active: 0 });
// nb: this is a newish browser feature -- HTML5. what it does is to clear the GET parms from the URL in the addr bar.
//window.history.pushState({},'foo','.')
// on the first load (or a reload) of the page, clear the form...
//clearForm($('#search')[0]);
});
