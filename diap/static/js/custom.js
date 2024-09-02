
  (function ($) {
  
  "use strict";

    // CUSTOM LINK
    $('.smoothscroll').click(function(){
      var el = $(this).attr('href');
      var elWrapped = $(el);
      var header_height = $('.navbar').height();
  
      scrollToDiv(elWrapped,header_height);
      return false;
  
      function scrollToDiv(element,navheight){
        var offset = element.offset();
        var offsetTop = offset.top;
        var totalScroll = offsetTop-0;
  
        $('body,html').animate({
        scrollTop: totalScroll
        }, 300);
      }
    });

    var numItems1 = $('.carousel1 .item').length; //.owl-carousel-image

    // Проверить, является ли количество элементов больше трех
    if (numItems1 > 3) {
      // Настроить первую карусель на центральный элемент и циклическую прокрутку
      $('.carousel1').owlCarousel({
        center: true,
        loop: true,
        margin: 30,
        autoplay: true,
        responsiveClass: true,
        dots: false,
        responsive:{
            1:{
                items: 3
            }
        }
      });
    } else {
      // Настроить первую карусель на центральный элемент и отключить циклическую прокрутку
      $('.carousel1').owlCarousel({
        center: false, //true or false
        loop: false,
        margin: 30,
        autoplay: false,
        responsiveClass: true,
        dots: false,
        responsive:{
            1:{
                items: 3
            }
        }
      });
    }

    // Получить количество элементов во второй карусели
    var numItems2 = $('.carousel2 .item').length; //.owl-carousel-image

    // Проверить, является ли количество элементов больше трех
    if (numItems2 > 3) {
      // Настроить вторую карусель на центральный элемент и циклическую прокрутку
      $('.carousel2').owlCarousel({
        center: true,
        loop: true,
        margin: 30,
        autoplay: true,
        responsiveClass: true,
        dots: false,
        responsive:{
            1:{
                items: 3
            }
        }
      });
    } else {
      // Настроить вторую карусель на центральный элемент и отключить циклическую прокрутку
      $('.carousel2').owlCarousel({
        center: false, //true or false
        loop: false,
        margin: 30,
        autoplay: false,
        responsiveClass: true,
        dots: false,
        responsive:{
            1:{
                items: 3
            }
        }
      });
    }
  
  })(window.jQuery);


