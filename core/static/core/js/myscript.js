$('.featured-carousel').owlCarousel({

    loop:true,

    margin:20,

    nav:true,

    dots:false,

    navText: [
        '<img src="/static/core/images/back.png">',
        '<img src="/static/core/images/next.png">'
    ],

    autoplay:true,

    autoplayTimeout:3000,

    responsive:{

        0:{
            items:1
        },

        576:{
            items:2
        },

        992:{
            items:3
        },

        1200:{
            items:4
        }

    }

});

$('.featured-carousel .owl-nav').appendTo('.featured-right');



$('.featured-card').click(function(){

    let id = $(this).data('business');

    $.get('/business/' + id + '/modal/', function(response){

        $('#modalContent').html(response.html);

        $("#businessModal").modal("show");

    });

});

$(document).on("click", ".offer-card", function (e) {

    e.preventDefault();

    let id = $(this).data("business");

    $.get("/business/" + id + "/modal/", function (response) {

        $("#modalContent").html(response.html);

        $("#businessModal").modal("show");

    });

});