/**
 * Created by zhangyw on 2016/6/2.
 */


var ccpmViewModel = function() {

    var self = this;
    var today = new Date() ;
    var year = today.getFullYear() +"";
    var month = (today.getMonth() +1) + "";
    var day = today.getDate() +"";
    var valpre="期货";
  if(!sjConfig._isSupports_canvas()){
    //    alert("您的浏览器太旧，无法获得最佳用户体验，请使用Chrome或IE11进行浏览。");
    $(".no_data").html("当前浏览器不支持本功能展示，请使用IE9以上版本或者Chrome、Safari最新版浏览器。");
     //   self.isOldBrower(true);
    }

    // Non-editable catalog data - would come from the server
    //  self.tabledata = ko.observable({"IC": [{"instrumentid":"IC1601"}]});
    self.tabledata = ko.observableArray();
    self.isShowAmt = ko.observable(false);
    self.buyflag = ko.observable(true);
    self.sellflag = ko.observable(true);
    self.tradingdayShow = ko.observable();
    self.showtitle = ko.observable();
    self.showAlone = ko.observable(false);
    var urlParametre = "productid=";
    var urlproductIdx= window.location.href.indexOf(urlParametre);
    if(urlproductIdx>0){
        var urlproduct = window.location.href.substr( urlproductIdx+urlParametre.length ,2);
        self.selectProduct =ko.observable( urlproduct );
        if( urlproduct.substr(1,1)=="O"){
          valpre="期权";
          $('input[name="radio"]:eq(1)').attr("checked","checked");
          changeProduct();
         }
    }else{
        self.selectProduct =ko.observable( "IF");
    }

    self.productid = sjConfig.productids;


    self.inputdate = ko.observable(year + "-" + (month[1]?month:"0"+month) + "-" +(day[1]?day:"0"+day));

    self.isShow =  ko.observable(false);
    self.isHavResult= ko.observable(false);
    self.download ={"url" : ko.observable(),
        "details" : ko.observable()};
    self.getDatas = function () {
        self.inputdate($.trim($("#actualDate").val()));
        $("#selectProduct").val(self.selectProduct() );

         var val=$('input[name="radio"]:checked').val();
        var val2=$.trim( $('#selectSec').val());  
        var selectedProduct; 
        if(val != valpre  ){
           if(val2 =="IO")
              {selectedProduct = "IO";
                self.selectProduct =ko.observable( "IO");
              }else if(val2=="IF")
             {selectedProduct = "IF";
              self.selectProduct =ko.observable( "IF");}else{
             selectedProduct = val2;
              self.selectProduct =ko.observable( val2);
             }
         valpre=val;  
          }else{
        // selectedProduct = $.trim($('#selectSec').val());
selectedProduct =$.trim(self.selectProduct());
          }
        //self.selectProduct =ko.observable( selectedProduct );
        var isShowAmt = sjConfig._formatPrice(selectedProduct, "isPositionAmt");
        var date_cur = new Date($.trim($("#actualDate").val()));
        var date_lit = new Date('2020-09-14');
          if(date_cur< date_lit){
                var isShowAmt=false
          }
        self.isShowAmt(false);
        self.isShow(false);
        self.isHavResult(false);
        var judge=null;
        self.tradingdayShow();
        self.showtitle();
        var title=null;
    //    var selectedProduct=$.trim(self.selectProduct());
        $.ajax({
            async:true,
            dataType:"text",
          //  url: "http://www.cffex.com.cn/fzjy/ccpm/" + sjConfig._parseDate( self.inputdate(),0) + "/" + $.trim(self.selectProduct()) + ".xml" ,
 url: "/sj/ccpm/" + sjConfig._parseDate( self.inputdate(),0) + "/" + selectedProduct + ".xml?id="+Math.floor(Math.random()*100) ,
            method: 'GET',
            success: function(response) {
                var instrData = {};
                var amtData = {};
                var instrumentidArray = [];

                $(response).find("data").each(function () {

                    var tempdata = {};

                    var node = $(this);

                    var instment = $.trim( node.find("instrumentid").text() );
                    judge=instment;
                    if( instrumentidArray.indexOf(instment) == -1){
                        instrumentidArray.push(instment);
                    }
                    if (instrData[instment] == null) {
                        instrData[instment] = {
                            "volumn": [],
                            "buyposition": [],
                            "sellposition": []
                        };
                    }
                    tempdata = {
                        "dataTypeId" : $.trim( node.find("dataTypeId").text() ),
                        "rank" : $.trim( node.find("rank").text() ),
                        "shortname" : $.trim( node.find("shortname").text() ),
                        "volume" : $.trim( node.find("volume").text() ),
                        "varvolume" : $.trim( node.find("varVolume").text() ),
                        "partyid" : $.trim( node.find("partyid").text() ),
                        "dataTypeId" : $.trim( node.find("dataTypeId").text() ),
                    };

                    var datatype = $.trim( node.find("datatypeid").text() );
                    if( datatype == "0"){
                        instrData[instment]["volumn"].push(tempdata);
                    }else if ( datatype == "1") {
                                instrData[instment]["buyposition"].push(tempdata);
                    } else if (datatype == "2") {
                        instrData[instment]["sellposition"].push(tempdata);
                    }

                });
               if( isShowAmt== true){
                    isShowAmt = false;
                   $(response).find("positionamt").each(function () {
                       var node = $(this);

                       var instment = $.trim( node.find("instrumentid").text() );
                       isShowAmt = true;
                       judge=instment;
                       title=instment;
                       if(instment=="")
                       {
                                 isShowAmt =false;
                       }
                       var buy = $.trim( node.find("buyvolumeamt").text() );
                       var sell = $.trim( node.find("sellvolumeamt").text() );
                       if(buy == '' || buy == undefined || buy == null){
                           self.buyflag(false)
                       } else {
                           self.buyflag(true)
                       }
                       if(sell == '' || sell == undefined || sell == null){
                           self.sellflag(false)
                       } else {
                           self.sellflag(true)
                       }
                       var tempdata = {
                           "futurecompany" : $.trim( node.find("futurecompany").text() ),
                           "volumeamt" : $.trim( node.find("volumeamt").text() ),
                           "varvolumeamt" : $.trim( node.find("varvolumeamt").text() ),
                           "buyvolumeamt" : $.trim( node.find("buyvolumeamt").text() ),
                           "buyvarvolumeamt" : $.trim( node.find("buyvarvolumeamt").text() ),
                           "sellvolumeamt" : $.trim( node.find("sellvolumeamt").text() ),
                           "sellvarvolumeamt" : $.trim( node.find("sellvarvolumeamt").text() ),
                       };
                       if (amtData[instment] == null) {
                           amtData[instment] = {};
                       }

                       if (tempdata["futurecompany"] == "0") {
                           amtData[instment]["0"] = $.extend(true, {}, tempdata);
                       } else if (tempdata["futurecompany"] == "1") {

                           amtData[instment]["1"] = $.extend(true, {}, tempdata);
                       }

                   });
               }



                var instrTemp = {};
                var totalTemp = {};
                for (var key in instrData) {
                    instrData[key]["volumn"].sort(sjConfig._positionRankSort);
                    instrData[key]["buyposition"].sort(sjConfig._positionRankSort);
                    instrData[key]["sellposition"].sort(sjConfig._positionRankSort);
                    instrTemp[key] = [];
                    totalTemp[key] = {
                        totalvolumn: 0,
                        totalvarvolumn: 0,
                        totalbuyp: 0,
                        totalvarbuyp: 0,
                        totalsellp: 0,
                        totalvarsellp: 0,
                    }
                    for (var i = 0; i < instrData[key]["volumn"].length; i++) {
                        instrTemp[key].push({
                            "rank1": instrData[key]["volumn"][i]["rank"],
                            "vshortname": instrData[key]["volumn"][i]["shortname"],
                            "volumn": instrData[key]["volumn"][i]["volume"],
                            "varvolumn": instrData[key]["volumn"][i]["varvolume"],
                            "rank2": instrData[key]["buyposition"][i]["rank"],
                            "bshortname": instrData[key]["buyposition"][i]["shortname"],
                            "buyposition": instrData[key]["buyposition"][i]["volume"],
                            "varbuypositon": instrData[key]["buyposition"][i]["varvolume"],
                            "rank3": instrData[key]["sellposition"][i]["rank"],
                            "sshortname": instrData[key]["sellposition"][i]["shortname"],
                            "sellposition": instrData[key]["sellposition"][i]["volume"],
                            "varsellposition": instrData[key]["sellposition"][i]["varvolume"]
                        })

                        totalTemp[key].totalvolumn += Number(instrData[key]["volumn"][i]["volume"]);
                        totalTemp[key].totalvarvolumn += Number(instrData[key]["volumn"][i]["varvolume"]);
                        totalTemp[key].totalbuyp += Number(instrData[key]["buyposition"][i]["volume"]);
                        totalTemp[key].totalvarbuyp += Number(instrData[key]["buyposition"][i]["varvolume"]);
                        totalTemp[key].totalsellp += Number(instrData[key]["sellposition"][i]["volume"]);
                        totalTemp[key].totalvarsellp += Number(instrData[key]["sellposition"][i]["varvolume"]);

                    }
                }

                for(var key in instrTemp){
                    //合计
                    instrTemp[key].push({
                        "rank1":"合计",
                        "vshortname":"",
                        "volumn":  totalTemp[key].totalvolumn,
                        "varvolumn":  totalTemp[key].totalvarvolumn,
                        "rank2": "",
                        "bshortname": "",
                        "buyposition":  totalTemp[key].totalbuyp,
                        "varbuypositon":   totalTemp[key].totalvarbuyp,
                        "rank3": "",
                        "sshortname": "",
                        "sellposition": totalTemp[key].totalsellp,
                        "varsellposition": totalTemp[key].totalvarsellp
                    })
                }



                instrumentidArray.sort(function(a,b){
                    return a>b;
                })


                var showArrays =[];
                for(var i=0 ;i<instrumentidArray.length; i++){
                    var instru = instrumentidArray[i];
                    if(judge.length>3 && judge.indexOf("O") >0){
                    showArrays.push({
                        insShow : "合约系列:" + instrumentidArray[i],
                        posData : instrTemp[instru],
                        amtData :  isShowAmt ? amtData[instru]:[],
                        judge:1
                    })
                   }else{
                     showArrays.push({
                        insShow :"合约:" + instrumentidArray[i],
                        posData : instrTemp[instru],
                        amtData :  (isShowAmt && i<1) ? amtData[judge]:[],
                        judge:  (isShowAmt && i<1) ? 0:1                        
                    })
                    }
                }
                self.tabledata(showArrays);
                self.showtitle("产品:"+title);

                self.tradingdayShow("交易日:" + sjConfig._parseDate(self.inputdate(), 2));

                self.isShowAmt(isShowAmt);

                if(self.tabledata().length >0)
                {
                    self.isShow(true) ;
                }



            },
            complete : function(response){

                $("#selectSec").find(" option[value='"+urlproduct+"']").attr("selected",true);
                if(!self.isShow()){
                    self.isHavResult(true);
                }else{
                    var date =sjConfig._parseDate( self.inputdate(), 0);
                    self.download.url("/sj/ccpm/" + date + "/" + selectedProduct  + "_1.csv");
                    self.download.details(selectedProduct+"当日成交持仓排名");

                }
            }
        });
    }
}



var main = new ccpmViewModel()
ko.applyBindings(main);
main.getDatas();
changeProduct();