/**
 * Created by Administrator
 */

$(function(){
//加载
var s=window.location.search;
if(s)
{
 var ss=s.slice(3,s.length);
 var sss=ss.split("-");
 $("#daohang-b>ul").hide();
 $("#daohang-b div").removeClass("action2");
 $("#daohang-b [data-k="+sss[0]+"]").addClass("action2");
 $("#daohang-b [data-k="+sss[0]+"]").next().show();
 $("#daohang-b [data-k="+ss+"]").css("fontWeight","bolder");
 $("#daohang-b [data-k="+ss+"]").addClass("action");
 if(sss[0]=="1")
 {
   $("#content div").hide(0);
   $("#table-1").show();
 }
 else if(sss[0]=="2")
 {
   $("#content div").hide();
   $("#table-2").show();
 }
 else if(sss[0]=="3"&&sss[1]=="1")
 {
   $("#content div").hide();
   $("#table-3").show();
 }
 else if(sss[0]=="3"&&sss[1]=="2")
 {
   $("#content div").hide();
   $("#table-4").show();
 }
 else if(sss[0]=="3"&&sss[1]=="3")
 {
   $("#content div").hide();
   $("#table-5").show();
 }
 else if(sss[0]=="3"&&sss[1]=="4")
 {
   $("#content div").hide();
   $("#table-6").show();
 }
 else if(sss[0]=="4")
 {
   $("#content div").hide();
   $("#table-7").show();
 }
 else if(sss[0]=="5"&&sss[1]=="1")
 {
   $("#content div").hide();
   $("#table-8").show();
 }
}
else
{
  $("#daohang-b>ul").hide();
  $("#content div").hide();
}
  
//一级目录选中
$("#daohang-b").on("click","div",function(event){
    $("#daohang-b>ul").hide();
    $("#daohang-b div").removeClass("action2");
    $(this).addClass("action2");
    $(this).next().show(300);
})

//二级目录选中
$("#daohang-b").on("click","li",function(){
  $("#daohang-b li").removeClass("action");
  $("#daohang-b li").css("fontWeight","normal");
  $(this).css("fontWeight","bolder");
  $(this).addClass("action");
  var k=$(this).parent().data("k");
  var kk= k.slice(0,1);
  $("#daohang-b [data-k="+kk+"]").addClass("action2");
  //获取当前项目data-k
  var k1=$(this).data("k");
  if(k1!="5-2")
  {
  var str="monitor.html?A="+k1;
  window.location.href=str;
  }
})
$("#nav-nav a").attr("href","../logout");
})
