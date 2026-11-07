$(function(){
	    $(".video-li-a").on("click touch", function () {
	        var self = $(this), videoPath = self.attr("video-path");
	        if (videoPath) {
	            videoPath = (videoPath + "?n=" + Math.random());
				var videoWarp = $(".big-video-main");
				videoWarp.html(" <video src=\"" + videoPath + "\" width=\"100%\" height=\"auto\" controls preload></video>").children("video").trigger("play");
	            $(".shade,.big-video").show();
	        } else {
	            var options = {
	                type: 2,
	                msg: "视频不存在或已删除",
	                overlayShow: false
	            };
	            msgBox.tips(options);
	        }
		});
		
	    $(".big-video-clo").on("click touch", function () {
	        $(".shade, .big-video").hide();
			$(".big-video-main video").trigger('pause').remove();
	    });
	
})

