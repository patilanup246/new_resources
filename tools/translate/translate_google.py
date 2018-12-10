# coding:utf-8
import json

import requests
import logging

import sys


def sendRequest(text):
    url = "http://www.1talking.net:8000/api/v1.0/common/translate"
    formData = {
        "key": "d#*fsd32iofdg0&*fsfjan21374fdshf",  # 固定值key
        "q": text,  # 需要翻译的文本，接受一个数组或者字符串,
        "source": "auto",  # 源语言，不传则自动检测
        "target": "zh-cn"  # 目标语言
    }
    textChinses = ""
    for i in range(3):
        try:
            if sys.version_info[0] == 2:
                import urllib2
                import urllib
                proxy_handler = urllib2.ProxyHandler({})
                opener = urllib2.build_opener(proxy_handler)
                request = urllib2.Request(url=url, data=urllib.urlencode(formData))
                resp = opener.open(request)
                if resp.code == 200:
                    responseBody = json.loads(resp.read())
                    if responseBody["success"]:
                        textChinses = responseBody["data"]["translations"][0]["translatedText"]
                        break
            else:
                response = requests.post(url=url, data=formData)
                response.encoding = "utf-8"
                if response.status_code == 200:
                    responseBody = json.loads(response.text)
                    if responseBody["success"]:
                        textChinses = responseBody["data"]["translations"][0]["translatedText"]
                        break
        except Exception as e:
            print(e)
            logging.error(e)
            logging.warn("****************翻译失败****************")

    return textChinses


def mainTranslate(text):
    return sendRequest(text)


if __name__ == '__main__':
    text = """.bbb_link {display: block;position: relative;overflow: hidden; width: 100px; height: 38px; margin: 0px; padding: 0px;}	.bbb_link_img {padding: 0px; border: none;},Customer Service,new Date().getFullYear()>2010&&document.write(""+new Date().getFullYear());,Contact Us,Careers,Privacy & Security,function jumpToPartner() {						if (document.getElementById('partners-dropdown-choice').value == 'dummy') {							return false;							} else {								document.forms['gotoPartner'].action = document.getElementById('partners-dropdown-choice').value;							}						},Social Responsibility,About Qurate Retail Group,Our Company,About Garnet Hill,Go,var br_data = {};	function  bloomReachTrack(categoryId, categoryName, searchPhrase) {		br_data = {};		/* --- Begin parameters section: fill in below --- */		br_data.acct_id = "5287";				/*br_data.ptype = "<search, category, product, thematic, other>";*/		var areaName = '';		var viewName = '';		var areaNameElm = gwtDynamic.area_name;   /*document.getElementById("gwt_area_name");*/				if (areaNameElm) areaName = areaNameElm; /*areaNameElm.value;*/				var viewNameElm =  gwtDynamic.view_name; /*document.getElementById("gwt_view_name");*/				if (viewNameElm) viewName =  viewNameElm;   /*viewNameElm.value;*/				if(areaName || viewName) {			if("ProductSearch" == areaName) {				br_data.ptype = "search";				if(searchPhrase) {					br_data.search_term = searchPhrase; }				else {					var searchTerm = '';					searchTerm = jQuery(location).attr('hash'); 					if (searchTerm ) searchTerm = searchTerm.replace(/^#w=/, "");										if (searchTerm ) br_data.search_term = searchTerm;				}			}else if("CategoryView" == areaName) {				br_data.ptype = "category";			}else if("ProductDetailView" == viewName) {				br_data.ptype = "product";			}else if("BRThematicView" == viewName) {				br_data.ptype = "thematic";			}else if("HomeView" == viewName) {				br_data.ptype = "homepage";			}else {				br_data.ptype = "other";			}		}		if((typeof analyticsData != 'undefined') && analyticsData.cmCategoryId ) {			br_data.cat_id = analyticsData.cmCategoryId;		}		/*		br_data.cat = "<category(ies) related to page, separated by a '|'";		*/				if((typeof analyticsData != 'undefined') && analyticsData.cmPageId ) {			br_data.page_id = analyticsData.cmPageId;		}		if((typeof analyticsData != 'undefined') && analyticsData.breadCrumbsArray) {								br_data.cat = '';				if (analyticsData.breadCrumbsArray.length ==0) br_data.cat = '';				else {					br_data.cat = analyticsData.breadCrumbsArray[0];					for (var i=1; i <  analyticsData.breadCrumbsArray.length  ; i++) {						br_data.cat =  analyticsData.breadCrumbsArray[i] + '|' + br_data.cat;					}									}							}				if((typeof productsJson != 'undefined') && productsJson) {			if(productsJson.bundleId) {										/*br_data.prod_id = productsJson.partNumber; changed to mfPartNumber for gh based on bloomreach feedback */	                        br_data.prod_id = productJSONArray[0].pageProduct.mfPartNumber;                                br_data.prod_name = productJSONArray[0].pageProduct.prodName;                                br_data.sku = ''; /* br_data.prod_id;    changed to null for gh based on bloomreach feedback  */                                if (productJSONArray[0].pageProduct.minListPrice > 0)                                          br_data.price = productJSONArray[0].pageProduct.minListPrice;                                else                                          br_data.price = productJSONArray[0].pageProduct.minimumPrice;		                br_data.sale_price = productJSONArray[0].pageProduct.minimumPrice;			}else if((typeof productJSONArray != 'undefined') && productJSONArray && productJSONArray[0] && productJSONArray[0].pageProduct){									/*br_data.prod_id =  productJSONArray[0].pageProduct.partNumber; changed to mfPartNumber for gh based on bloomreach feedback */				br_data.prod_id =  productJSONArray[0].pageProduct.mfPartNumber;				br_data.prod_name =  productJSONArray[0].pageProduct.prodName;				br_data.sku = ''; /* br_data.prod_id; changed to null for gh based on bloomreach feedback  */								if(productJSONArray[0].pageProduct.minListPrice >0) 					br_data.price = productJSONArray[0].pageProduct.minListPrice;				else 					br_data.price = productJSONArray[0].pageProduct.minimumPrice;									br_data.sale_price = productJSONArray[0].pageProduct.minimumPrice;			}		}		/*br_data.pstatus= <"product status:  ok, outofstock, discontinued, other">;*/		if((typeof trkpix_json != 'undefined') && trkpix_json && trkpix_json.trkpix_pageName == 'orderConfirmation')  {			br_data.is_conversion = 1;			br_data.basket_value = trkpix_json.trkpix_order_value;			br_data.order_id = trkpix_json.trkpix_merchant_order_id;			/* Extended basket tracking. To be filled in only on pages with is_conversion = 1 */			if(trkpix_json) {												var itemsArray = [];				for (var pagepr in trkpix_json.trkpix_oItems) {						var oitem = trkpix_json.trkpix_oItems[pagepr].oitem;																								if(oitem) {						   var modval = '';						   if( (  ((oitem.price * oitem.qty) ) != Number(oitem.totalDiscountPrice.replace('\$','')))) 							   	modval = "sale";						   else 						   	modval = "";						 					   						    itemsArray.push( {							    "prod_id": oitem.itemsProductmfpartNo,							    "sku": oitem.partNumber ,							    "name": oitem.name,							    "quantity": oitem.qty,							    "price": oitem.price,							    "mod": modval						    });						}				}								br_data.basket={					"items": itemsArray				};							}						}else {			br_data.is_conversion = 0;		}		/* --- End parameter section --- */		(function() {		var brtrk = document.createElement('script');		brtrk.type = 'text/javascript';		brtrk.async = true;		brtrk.src = 'https:' == document.location.protocol ? "https://cdns.brsrvr.com/v1/br-trk-5287.js" : "http://cdn.brcdn.com/v1/br-trk-5287.js";		var s = document.getElementsByTagName('script')[0];		s.parentNode.insertBefore(brtrk, s);		})();	}		var brviewNameElm = gwtDynamic.view_name;        var brviewName = '';	if (brviewNameElm) brviewName = brviewNameElm; /*brviewNameElm.value;*/	function grabTPXData() {	/*This different for TS because TS categoryPageAnalyticsCallback doesnot seem to be called by SLI */		if ("SLIBodyView"!=brviewName) {			bloomReachTrack(null,null,null);		}	}		if( !( "ShoppingCartArea" == gwtDynamic.area_name  && checkoutVersion == "2"  ) ) 	grabTPXData();	            function showQuickViewAnalyticsCallBack(mfPartnumber, name, sku) {	   BrTrk.getTracker().logEvent(	       'product',	       'quickview',	      { 		    'prod_id': mfPartnumber,		    'prod_name': name,		    'sku': sku		  });      },Join our email list.,Conditions of Use,If you are not completely delighted with an item, we’ll take it back for exchange or refund.,Affiliate Sites,Ballard Designs,Garnet Hill Cares,Privacy & Security,Visit our blog,,800.870.3513,Gift Cards,var touchObj;
		var touchStartTime;
		function sourceCodeDblClicked() {
			triggerReportToServer();
		}
		function sourceCodeTouched(event) {
			event.preventDefault();
			if (touchObj == null) {
				touchObj = event.touches[0];
				touchStartTime = new Date();
			}
		}
		function sourceCodeReleased(event) {
			var found = false;
			for (var i = 0; i< event.touches.length; i++) {
				if (event.touches[i] == touchObj) {
					found = true;
					break;
				}
			};
			if ( ! found ) {
				var touchEndTime = new Date();
				var duration = touchEndTime - touchStartTime;
				if (duration > 1000) {
					triggerReportToServer();
				}
				touchObj = null;
			}
		}
		function triggerReportToServer() {
			if (typeof reportToServer == 'undefined') {
				head.js("/wcsstore/CornerStoneBrands/javascript/diagnosticTools.js", function() {reportToServer();});
			} else {
				reportToServer();
			}
		},Select an affiliate:,International Customers,:,Sale of the Day,Click to submit email,Returns & Exchanges,var divlist = findElementsWithPrefix("div", "gwt_recommendations_");
		// Determine if any of the divs in divlist are enabled. If so, set callCertonaRunInFooter to false.
		divlist.each( function (divelem) {
			if (callCertonaRunInFooter == true) {
				var jsvarname = divelem.id + "_JSON";
				eval("var jsonObj = " + jsvarname + ";");
				if (jsonObj.enabled == "true") {
					callCertonaRunInFooter = false;
				}
			}
		});

	    var cookieValue = Get_Cookie('RES_TRACKINGID');
	    if (! cookieValue || callCertonaRunInFooter ) {
			certonaResx.run();
		},Request a Catalog,©2018 Garnet Hill,jQuery(document).on('categoryPageAnalyticsCallBack',function(e,data) { 				if( typeof attachDragHandlerJQuery != 'undefined')  attachDragHandlerJQuery();				if( typeof bloomReachTrack != 'undefined') bloomReachTrack(data.categoryId,data.categoryName,null);	});	jQuery(document).on('productSearchAnalyticsCallBack',function(e,data) { 				if( typeof attachDragHandlerJQuery != 'undefined')  attachDragHandlerJQuery();				if( typeof bloomReachTrack != 'undefined') bloomReachTrack(null,null,data.searchTerm);	});	jQuery(document).on('addToCartAnalyticsCallBack',function(e,data) { 		 /*      	BrTrk.getTracker().logEvent('Cart', 'add', {'prod_id':data.mfPartnumber,'sku' :'','prod_color':'','prod_name': data.name}, {'price' : data.price, 'sale_price' : data.price}); */				 BrTrk.getTracker().logEvent('cart', 'click-add', {'prod_id':data.mfPartnumber,'sku' :''});      		});,Source Code: R8WBRS1,Garnet Hill,Our Outlet Store,Site Map,Frontgate,Current Specials,Wish List,The Garnet Hill Guarantee,Popular Searches,div#gwt_country_changer {						    margin-top: 10px;						    border-top: 2px solid #999999;						    padding-top: 10px;						    width: 60%;						},Shipping To:,To the Trade,Improvements,QVC,Threads,©,span.gh-italics {		font-style: italic;	}	@font-face{font-family:'FontAwesome';src:url('/wcsstore/images/GarnetHill/_media/css/fonts/fontawesome-webfont.eot?v=4.7.0');src:url('/wcsstore/images/GarnetHill/_media/css/fonts/fontawesome-webfont.eot?#iefix&v=4.7.0') format('embedded-opentype'),url('/wcsstore/images/GarnetHill/_media/css/fonts/fontawesome-webfont.woff2?v=4.7.0') format('woff2'),url('/wcsstore/images/GarnetHill/_media/css/fonts/fontawesome-webfont.woff?v=4.7.0') format('woff'),url('/wcsstore/images/GarnetHill/_media/css/fonts/fontawesome-webfont.ttf?v=4.7.0') format('truetype'),url('/wcsstore/images/GarnetHill/_media/css/fonts/fontawesome-webfont.svg?v=4.7.0#fontawesomeregular') format('svg');font-weight:normal;font-style:normal}.fa{display:inline-block;font:normal normal normal 14px/1 FontAwesome;font-size:inherit;text-rendering:auto;-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}.fa-lg{font-size:1.33333333em;line-height:.75em;vertical-align:-15%}.fa-2x{font-size:2em}.fa-3x{font-size:3em}.fa-4x{font-size:4em}.fa-5x{font-size:5em}.fa-fw{width:1.28571429em;text-align:center}.fa-ul{padding-left:0;margin-left:2.14285714em;list-style-type:none}.fa-ul>li{position:relative}.fa-li{position:absolute;left:-2.14285714em;width:2.14285714em;top:.14285714em;text-align:center}.fa-li.fa-lg{left:-1.85714286em}.fa-border{padding:.2em .25em .15em;border:solid .08em #eee;border-radius:.1em}.fa-pull-left{float:left}.fa-pull-right{float:right}.fa.fa-pull-left{margin-right:.3em}.fa.fa-pull-right{margin-left:.3em}.pull-right{float:right}.pull-left{float:left}.fa.pull-left{margin-right:.3em}.fa.pull-right{margin-left:.3em}.fa-spin{-webkit-animation:fa-spin 2s infinite linear;animation:fa-spin 2s infinite linear}.fa-pulse{-webkit-animation:fa-spin 1s infinite steps(8);animation:fa-spin 1s infinite steps(8)}@-webkit-keyframes fa-spin{0%{-webkit-transform:rotate(0deg);transform:rotate(0deg)}100%{-webkit-transform:rotate(359deg);transform:rotate(359deg)}}@keyframes fa-spin{0%{-webkit-transform:rotate(0deg);transform:rotate(0deg)}100%{-webkit-transform:rotate(359deg);transform:rotate(359deg)}}.fa-rotate-90{-ms-filter:"progid:DXImageTransform.Microsoft.BasicImage(rotation=1)";-webkit-transform:rotate(90deg);-ms-transform:rotate(90deg);transform:rotate(90deg)}.fa-rotate-180{-ms-filter:"progid:DXImageTransform.Microsoft.BasicImage(rotation=2)";-webkit-transform:rotate(180deg);-ms-transform:rotate(180deg);transform:rotate(180deg)}.fa-rotate-270{-ms-filter:"progid:DXImageTransform.Microsoft.BasicImage(rotation=3)";-webkit-transform:rotate(270deg);-ms-transform:rotate(270deg);transform:rotate(270deg)}.fa-flip-horizontal{-ms-filter:"progid:DXImageTransform.Microsoft.BasicImage(rotation=0, mirror=1)";-webkit-transform:scale(-1, 1);-ms-transform:scale(-1, 1);transform:scale(-1, 1)}.fa-flip-vertical{-ms-filter:"progid:DXImageTransform.Microsoft.BasicImage(rotation=2, mirror=1)";-webkit-transform:scale(1, -1);-ms-transform:scale(1, -1);transform:scale(1, -1)}:root .fa-rotate-90,:root .fa-rotate-180,:root .fa-rotate-270,:root .fa-flip-horizontal,:root .fa-flip-vertical{filter:none}.fa-stack{position:relative;display:inline-block;width:2em;height:2em;line-height:2em;vertical-align:middle}.fa-stack-1x,.fa-stack-2x{position:absolute;left:0;width:100%;text-align:center}.fa-stack-1x{line-height:inherit}.fa-stack-2x{font-size:2em}.fa-inverse{color:#fff}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0, 0, 0, 0);border:0}.sr-only-focusable:active,.sr-only-focusable:focus{position:static;width:auto;height:auto;margin:0;overflow:visible;clip:auto}			.fa-facebook-square:before{content:"\f082"}			.fa-twitter:before{content:"\f081"}			.fa-pinterest:before{content:"\f0d2"}			.fa-instagram:before{content:"\f16d"}/* TOP FOOTER FULL WIDTH */	div.gh-wrapper {		border-top: 4px solid #E6E6E6;	}	div.GH-footerTopFull,	div.GH-footerTopHalf,	div.GH-footerTopThird {		font-family:'Avenir LT Std', 'Avenir', Arial, Helvetica, sans-serif;		margin-bottom: 18px;			}	div.newsletter-box {		border-top: 1px solid #000;		border-bottom: 1px solid #000;		height: 62px;		padding: 12px 40px;	}	div.GH-footerTopFull {		background: #efefef;		padding: 25px 75px;		text-align: center;	}	div.newsletter-left,	div.newsletter-right {		width: 375px;		float: left;        margin-top: -8px;	}	div.newsletter-left p.eTitle {    	font-size: 2.6em;	    font-family: 'Times New Roman',Serif;	    font-weight: 300;	    padding-top: 0;	    margin: 0;	    line-height: 1em;	}	div.newsletter-left span.eMessage {		font-size: 14px;		font-family:'Avenir LT Std', 'Avenir', Arial, Helvetica, sans-serif;		padding-top: 16px;	    margin: 0;	}	div.newsletter-left p {		font-size: 1em;	}/* TOP FOOTER HALF SECTION */	div.GH-footerTopHalf {	}	div.section-box {		min-height: 144px;        margin-top: 24px;	}	div.section-left,	div.section-right {		float: left;		height: 144px;	}	div.section-left {		padding-right: 20px;	}	div.section-right {		background: #efefef;		margin-top: -24px;	}	div.section-right p.eTitle {		font-size: 2.5em;		font-family: 'Times New Roman',Serif;		text-align: center;		font-weight: 300;		padding-top: 28px;		margin: 0;	}	div.section-right p.eMessage {		font-size: 1.25em;		font-family:'Avenir LT Std', 'Avenir', Arial, Helvetica, sans-serif;		text-align: center;		padding: 15px 0;	    margin: 0;	}	div.section-right form {		text-align: center;	}/* TOP FOOTER THIRD SECTION */	div.bi-section-left,	div.bi-section-center {		width: 230px;		float: left;		padding-right: 20px;	}/* FOOTER CONTAINER */	div.footer-container {		min-height: 160px;		background: #efefef;		padding: 20px;		font-size: 13px;		font-family: 'Avenir LT Std', 'Avenir', Arial, Helvetica, sans-serif;                height: auto;                overflow: hidden;	}	div.footer-container a {		text-decoration: none;		color: #393939;	}	div.footer-container a:hover {		color: #000;		text-decoration: none;	}	div.box {		padding: 18px 20px;		border: 1px solid #aaa;		background: #fff;	}	div.box p {		margin-top: 0;		font-family:'Avenir LT Std', 'Avenir', Arial, Helvetica, sans-serif;	}	p.box-title {		font-weight: bold !important;		font-size: 18px !important;		margin-bottom: 0;		line-height: 1.2em;		text-align: center;	}	p.box-message {		text-align: center;		font-size: 1em;		line-height: 1.45em;		padding-top: 10px;	}	div.col-box {		width: 22%;		float: left;	}	div.col-links {		width: 19.5%;		float: left;	}	div.col-links ul {	    padding-left: 40px;	}	div.col-links li.heading {		font-family:'Avenir LT Std', 'Avenir', Arial, Helvetica, sans-serif;		font-size: 1.1em !important;		font-weight: bold;		margin-bottom: 8px;		color: #333 !important;	}	ul.col-links2 {	    padding-left: 20px !important;	}	ul.col-links3 {	    padding-left: 34px !important;	}	div.col-links ul li {		list-style: none;		color: #333;		line-height: 1.45em;		font-size: .95em;	}	li span.sale-color {		color: #cb2625;	}	li span.sale-color:hover {		color: #000;	}	ul.social-icons {		margin: 4px 0 10px -40px;	}	ul.social-icons li {		display: inline-block;		line-height: 1.45em;	}	ul.social-icons li span.fa {		font-size: 20px;		padding: 0 3px;		color: #999999;	}	ul.social-icons li span.fa:hover {		color: #000;	}	li.threads {		font-weight: bold;		font-family: 'Avenir LT Std', 'Avenir', Arial, Helvetica, sans-serif;	}	li.telephone {		padding: 10px 0 0 0;		font-size: 1.2em !important;		font-weight: bold;		font-family: 'Avenir LT Std', 'Avenir', Arial, Helvetica, sans-serif;		color: #000;	}	div.footer-links {		min-height: 40px;		font-size: 12px;		font-family: 'Avenir LT Std', 'Avenir', Arial, Helvetica, sans-serif;		color: #666;	}	div.footer-links ul {		margin: 10px 0 0 0px;	}	div.footer-links ul li {		display: inline-block;		border-right: 1px solid #808080;		padding: 0 8px;		line-height: 12px;		font-size: .9em;	}	div.footer-links ul li:last-child {		border-right: none;	}	div.footer-links a {		text-decoration: none;		color: #666;	}	div.footer-links a:hover {		color: #000;		text-decoration: underline;	}	li.threads a,	li.threads a span {	    font-weight: bold;	}	div.col-links li.heading a {	color: #333;	font-weight: bold;}/* Go to partners list Box */	li.partners {	    margin-bottom: -5px;	}	.partnersdropdown {	    width: 100%;		text-align: center;		padding-top: 15px;		border-top: 1px solid #E6E6E6;	}	div.dropdown span {		padding: 5px 5px 0 0px;		font-family: 'Avenir LT Std', 'Avenir', Arial, Helvetica, sans-serif;	}	form#gotoPartner {	    margin-bottom: 0;		display: inline-block;	}	select#partners-dropdown-choice {	    margin-bottom: 0px;		color: #808080;        width: 125px;	}	#gotoPartner input {    	padding: 0px 2px 1px;    }	#gotoPartner label {    	padding-right: 5px;    }	#gotoPartner label a {    	color: #333;    }	#footer #copyright {		padding-top: 0;		border: none;	}#footer .footer-links #partners-dropdown-choice {    width: 150px !important;    padding: 0 !important;}/* Email Box Full Width */#footer #emailUpdates {    float: right;    line-height: 21px;    width: 430px !important;    margin: 0;    padding: 0 130px 13px 0px;    background-color: transparent;    clear: none;    position: relative;    top: 50px;}#footer #emailUpdates input#emailSignUp {    width: 248px;    padding: 3px 7px 0;    height: 26px;    vertical-align: top;    margin-right: 4px;    color: #808080;    font-family: 'Avenir LT Std', 'Avenir', Arial, Helvetica, sans-serif;    border: 1px solid #C5C5C5;}#footer #emailUpdates button {    border: medium none;    display: block;    float: left;    margin: 0 !important;    opacity: 1;    padding-left: 5px;	background: transparent;}.button img {    height: 30px;    width: 30px;}#footer #emailUpdates .errortxt {    line-height: 10px;    width: 200px;    margin-top: -6px;}/* Page Overwrite CSS */#footer .footerLinks {	display: none;}#footer li a {color: #333 !important;    font-family:'Avenir LT Std', 'Avenir', Arial, Helvetica, sans-serif;}#footer li a:hover {    color: #000;    text-decoration: none !important;}select {	font-family: 'Avenir LT Std', 'Avenir', Arial, Helvetica, sans-serif;	color: #808080;}li.list-title a {color: #000;}/* Inline style fixes */		.threads {text-decoration:none;}		.threads:hover {text-decoration: none;}				.threads_div_span_rule {border-top: 2px solid #03739e;border-bottom: 2px solid #03739e; padding: 8px 2px 6px; text-align: center}				.threads_div_span {font-weight:bold; font-size: 17px;color:#03739e; font-style: italic;}		.threads_div_blog {font-family: 'Avenir LT Std', 'Avenir', Arial, Helvetica, sans-serif;color:#333; font-weight: bold;font-size: 16px;}		.threads_div_title {color:#98bb66;font-family: 'Times New Roman', Georgia, Times, serif;font-size: 16px;}		.spacer_div {height:50px;}		.threads_div {margin: 10px 0 18px 0;},Size Chart,Stay Connected,Get the inside scoop on exclusive sales and new arrivals!,function  emailSignupButtonClick() {
		window.location.href="/EmailSubscribeView?storeId=10054&catalogId=10054&langId=-1&sectionName=&subscribeSource=3";
	},Digital Wallpaper,HSN,verify sign,Gift Registry,Our History,More Ways to Shop,var is_instructions_emailSignUp = true;
		function clear_instructions_emailSignUp()
		{
			if(is_instructions_emailSignUp)
			{
				is_instructions_emailSignUp = false;
				jQuery('[name=\'emailSignUp\']').val('');
			}
		}
		function emailSignUpSubmit(form)
		{
			validator_reset();
			
			//clear_instructions_emailSignUp();
		
			if (emailSignUp_frmvalidator.validator_submit(false, "EmailSignUpForm", true) == true){	
				/**
				* @author hsawalhi
				* Per WCSBD-807
				*/
				document.getElementById("emailSignUp_label").removeAttribute("style");
				return true;		      
			}
			return false;
		}
		
		var emailSignUp_frmvalidator = new Validator("EmailSignUpForm");
		emailSignUp_frmvalidator.addValidation("emailSignUp",true,"req","error-div-emailSignUp","Please enter your email address.");
		emailSignUp_frmvalidator.addValidation("emailSignUp",false,"email","error-div-emailSignUp","Please enter a valid email address.");,Shipping Information,Order Status,Accessibility Statement,Grandin Road,Sign up for Email Updates,Zulily"""
    print(mainTranslate(text[:4000]))