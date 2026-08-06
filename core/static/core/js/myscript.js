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