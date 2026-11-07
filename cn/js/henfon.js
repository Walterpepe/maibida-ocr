
$(function(){
	var $heights = $(window).height();
	    $widths  = $(window).width();
	if($(window).width()<=1200){
	$(".T-nav > li > a").click(function(){
	  if($(this).siblings(".secon").length>0){
		  $(this).siblings(".secon").stop(false,true).slideToggle();
		  $(this).parent().siblings().find(".secon").slideUp();
		  return false;
		  }
	})
	};
	$(window).scroll(function(){
	  if($(window).scrollTop()>30){
		 $(".top").addClass("on"); 
		 }else{
			 $(".top").removeClass("on"); 
			 }
	});
	$(window).scroll(function(){
	  if($(window).scrollTop()>30){
		 $(".top2").addClass("on"); 
		 }else{
			 $(".top2").removeClass("on"); 
			 }
	});
	$(".mob-nav").click(function(){
		$(this).toggleClass("on");
		$(".T-nav").stop(false,true).fadeToggle();
		});
	 
    $(".ny-nav span").text($(".ny-nav p a.cur").text());
	$(".ny-nav span,.liack span").click(function(){
		$(this).siblings().stop(false,true).slideToggle();
		})
	$(".baenc li .con a.cur").parent().show().siblings(".tit").addClass("on");
	$(".baenc li .tit").click(function(){
	  $(this).toggleClass("on").siblings(".con").stop(false,true).slideToggle();
	  $(this).parent().siblings().children(".tit").removeClass("on").siblings(".con").stop(false,true).slideUp();
	});
	if($(".ny-lboa .baenc a.cur").length>0){
		$(".ny-lboa span").text($(".ny-lboa .baenc a.cur").text());
	}
	$(".ny-lboa span").click(function(){
	  $(this).siblings(".baenc").slideToggle()	
	});
	$(".aloeal").on('click','dt',function(){
	  $(this).addClass("on").siblings("dt").removeClass("on");
	  $(this).next("dd").stop(false,true).slideDown().siblings("dd").stop(false,true).slideUp();	
	})
	$(".dolsca").click(function(){
	  if($(this).siblings(".lourew").length>0){
		  $(this).toggleClass("on").siblings().stop(false,true).slideToggle().parent().siblings().children(".dolsca").removeClass("on").siblings().stop(false,true).slideUp();
		  }
	  })
	
})


















