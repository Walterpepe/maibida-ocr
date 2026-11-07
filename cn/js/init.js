<!--DOC<!DOCTYPE html-->
<html lang="zh-cn">
 <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  
  <style>body{text-align:center;font-family:"Hiragino Sans GB","Microsoft Yahei",SimSun,Arial,"Helvetica Neue",Helvetica;font-size:14px;color:#333;margin:0;padding:0;height:100%}img{vertical-align:middle}a{text-decoration:none}.clearfix:after{display:block;clear:both;content:"";visibility:hidden;height:0}.explor-content{z-index:9999;position:absolute;top:25%;left:0;width:100%}.content-one{width:715px;height:152px;margin:0 auto;background:url(/error/1.png) no-repeat left center}.warning-text{display:inline-block;text-align:left;color:#666;padding:20px 0 0 215px}.font-size1{height:30px;line-height:30px;font-size:20px}.font-size1 strong{color:#3674bb}.font-size2{font-size:16px}.content-two{z-index:99999;position:absolute;bottom:15%;left:50%;width:792px;height:230px;margin:0 auto 0 -396px;border-radius:8px;background-color:#fff;border:solid 2px #e4f8ff}.brower-items-title{width:792px;height:44px;line-height:44px;background-color:#e4f8ff;font-size:16px;color:#086081;text-indent:20px;border-bottom:solid 2px #d2f2fd}.brower-items{padding:15px 0 15px 0}.b-item{float:left;width:25%;text-align:center;font-size:14px;color:#666;line-height:25px}.b-item .icon{width:100%;height:62px;background-repeat:no-repeat;background-position:center;margin-bottom:5px}.b-item a{display:block;margin:5px auto 0 auto;width:100px;height:30px;line-height:30px;border-radius:4px;background-color:#00beff;box-shadow:0 2px 0 0 #009bd0;border:1px solid #00beff;color:#fff;font-size:14px}</style>
 </head>
 <body>
  <div class="explor-content">
   <div class="content-one clearfix">
    <div class="warning-text">
     <p class="font-size1"><strong>啊噢，真不巧，网页走丢了！</strong></p>
     <p class="font-size2">抱歉，由于访问人数太多导致服务器压力山大，请您耐心等待。</p>
     <p class="">系统将在 <span id="second">8</span> 秒后带您返回首页</p>
    </div>
   </div>
  </div>
  
  <div style="position: absolute;bottom: 0;left: 0;width: 100%;height: 42px;background: url(/error/bg.png) no-repeat center top;border-bottom: 195px solid #3674BB;"></div>

  <script type="text/javascript">
      window.onload = function () {
          var timerSeconds = 8;
          var interval = setInterval(function () {
              if (timerSeconds <= 0) {
                  clearInterval(interval);
              }
              document.getElementById("second").innerHTML = timerSeconds;
              if (timerSeconds <= 0) {
                  setTimeout(function () {
                      window.location.href = '/';
                  }, 300);
              }
              timerSeconds--;
          }, 1000);
      }
    </script>
 </body>
</html>