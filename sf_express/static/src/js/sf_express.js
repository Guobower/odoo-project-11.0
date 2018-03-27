odoo.define('sf_express.ListRenderer', function (require) {
    'use strict';
    var Model = require('web.data');
    var lodop = require('sf_express.lodop');
    var ListController = require('web.ListController');

    function ReplaceNull(str) {
        if (str == null || str == "null") {
            str = "";
        }
        return str;
    }

    function BatchPrint(res_data) {
        //批量打印函数
        var strE = "";//隔日E标识"E"
        var strCOD = "";//代收货款标识
        var strCard = "";//代收货款卡号
        var strExpresstype = "";//顺丰业务类型
        var strMailID = "";//条码物流单号
        var strName = "";//收货人
        var strDestcode = "";//目的地址
        var strPhone = "";//收货电话
        var strAddress = "";//收货地址
        var strMonth = "";//月
        var strDay = "";//日
        var strPaytype = "";//代收货款
        var strPaymount = "";//代收金额
        var SFMonthlyAccount = "";//月结号
        var strSMJZ = "";//保价声明金额，规则在线支付大于等于1800元按销售金额，代收货款大于等于1000元按销售金额
        var strBJFY = "";//保价费用
        var strProduct = "";//产品
        var strRemark = "货到联系务必本人签收！";//备注
        var strPayMethod = "";//顺丰付款方式
        var strSendMessage = "";//寄件人信息，默认值为志行合力
        var errMessage = "";
        var strSendaddres = "";
        var Account = "";
        var proprice = "";
        var dai_proprice = "";
        PrintInit();//打印初始化


        //后台字符串序列化为json对象
        if (res_data.length < 0) {
            alert("错误：无打印信息！");
            return;
        }
        // var res_data = JSON.parse(res_data);
        for (var o in res_data) {
            strName = ReplaceNull(res_data[o].strName);
            var Expresstype = ReplaceNull(res_data[o].strExpresstype);
            switch (Expresstype) {
                case "1":
                    strExpresstype = "顺丰标快";
                    strE = "";
                    break;
                case "2":
                    strExpresstype = "顺丰特惠";
                    strE = "E";
                    break;
                case "5":
                    strExpresstype = "顺丰次晨";
                    strE = "";
                    break;
                case "6":
                    strExpresstype = "顺丰即日";
                    strE = "";
                    break;
                default:
                    strExpresstype = Expresstype;
                    strE = "";
                    break;
            }
            proprice = ReplaceNull(res_data[o].proprice)
            dai_proprice = ReplaceNull(res_data[o].dai_proprice)
            strSendMessage = ReplaceNull(res_data[o].strSendMessage)
            Account = ReplaceNull(res_data[o].SFMonthlyAccount)
            SFMonthlyAccount = "月结账号：" + ReplaceNull(res_data[o].SFMonthlyAccount)
            strDestcode = ReplaceNull(res_data[o].strDestcode);
            // strAddress = ReplaceNull(res_data[o].strAddress).replaceAll('"', ' ');
            strAddress = ReplaceNull(res_data[o].strAddress);
            strSendaddres = ReplaceNull(res_data[o].strSendaddres);
            var PayMethod = (res_data[o].strPayMethod);
            //顺丰付款方式是到付的时候，月结号不填
            if (PayMethod == "2") {
                SFMonthlyAccount = "";
                strPayMethod = "付款方式:到付";
            }
            if (PayMethod == "1") {
                strPayMethod = "付款方式:寄付月结";
            }
            if (PayMethod == "3") {
                strPayMethod = "付款方式:第三方付";
                //第三方付，月结账号下面需要加上“第三方地区：755A”，这里用不到没加
            }
            if (PayMethod == "4") {
                strPayMethod = "付款方式:寄付现结";
                strSendMessage = "广发银行贵金属产品供应商\n服务热线 400-830-8003 转 1-8-3";//目前项目寄付现结为广发项目使用
                SFMonthlyAccount = "";//寄付现结不打印月结号
            }
            strPhone = ReplaceNull(res_data[o].strPhone);
            //电话号码屏蔽
            if (strPhone.length > 7) {
                strPhone = strPhone.substring(0, 3) + "*****" + strPhone.substring(strPhone.length - 3, 3);
            }
            if (ReplaceNull(res_data[o].paytype) == "货到付款") {
                //代收信息打印
                strCOD = "COD";
                strPaytype = "代收货款";
                strPaymount = "¥" + ReplaceNull(res_data[o].strPaymount) + "元";
                strCard = "卡号:" + Account;
                //保价信息打印
                if (ReplaceNull(res_data[o].strPaymount) >= dai_proprice)//代收大于等于1000元保价
                {
                    strSMJZ = "声明价值:" + ReplaceNull(res_data[o].strPaymount) + "元";
                    strBJFY = "保价费用:" + ReplaceNull(res_data[o].strPaymount) * 5 / 1000 + "元";//千分之五
                }
                else//不保价则不打印信息
                {
                    strSMJZ = "";
                    strBJFY = "";
                }
            }
            else//非代收
            {
                strCOD = "";
                strPaytype = "";
                strPaymount = "";
                strCard = "";
                //保价信息打印
                if (ReplaceNull(res_data[o].strPaymount) >= proprice)//在线支付大于等于1800元保价
                {
                    strSMJZ = "声明价值:" + ReplaceNull(res_data[o].strPaymount) + "元";
                    strBJFY = "保价费用:" + ReplaceNull(res_data[o].strPaymount) * 5 / 1000 + "元";
                }
                else//不保价则不打印信息
                {
                    strSMJZ = "";
                    strBJFY = "";
                }
            }
            strProduct = ReplaceNull(res_data[o].strProduct);
            //
            var now = new Date();
            var strDate = "寄件日期:" + (now.getMonth() + 1) + "月" + now.getDate() + "日";

            strMailID = ReplaceNull(res_data[o].strMailID);

            var arrMailId = new Array();//定义数组
            arrMailId = strMailID.split(',');//分割运单号为数组
            var i = arrMailId.length;//得到数组长度
            if (i == 1) {
                LODOP.NewPage();
                CreatePrintPage(strExpresstype, strDestcode, strAddress, strSendMessage, strName, strPhone, strPayMethod,
                    strSMJZ, strBJFY, strPaytype, strPaymount, strE, strCOD, strCard, strProduct, strRemark, strDate,
                    "", "", "", "", arrMailId[0], SFMonthlyAccount, strSendaddres);
            }
            else if (i > 1) {
                var strPageCount = "";//包裹数量，格式“2/2”
                var strChild = "";//空字符串""或者“子单号”
                var strMother = "";//空字符串""或者“母单号”
                var strMotherid = "";//空字符串""或者母单物流号
                var strMailid = "";//条码物流号
                for (var j = 1; j <= i; j++) {
                    strPageCount = j + "/" + i;
                    if (j == 1)//多包裹母单单号打印设置
                    {
                        strChild = "母单号";
                        strMother = "";
                        strMotherid = "";
                        strMailid = arrMailId[0];
                    }
                    else//多包裹子单单号打印设置
                    {
                        strChild = "子单号";
                        strMother = "母单号";
                        strMotherid = arrMailId[0];
                        strMailid = arrMailId[j - 1];
                    }
                    //预览打印
                    LODOP.NewPage();
                    CreatePrintPage(strExpresstype, strDestcode, strAddress, strSendMessage, strName, strPhone, strPayMethod,
                        strSMJZ, strBJFY, strPaytype, strPaymount, strE, strCOD, strCard, strProduct, strRemark, strDate, strPageCount,
                        strChild, strMother, strMotherid, strMailid, SFMonthlyAccount, strSendaddres);
                    //直接打印不预览
                    //CreatePrintPage(strPageCount, strChild, strMother, strMotherid, strMailid); LODOP.PRINT();
                }
            }
        }
        LODOP.PREVIEW();
    }

    //打印初始化
    function PrintInit() {
        LODOP.PRINT_INITA(-138, -188, 585, 950, "顺丰电子面单套打");
        LODOP.SET_PRINT_PAGESIZE(1, 1000, 2100, "");
        LODOP.SET_PRINT_MODE("CATCH_PRINT_STATUS", true);
    }

    //带参数打印函数，创建打印页
    function CreatePrintPage(strExpresstype, strDestcode, strAddress, strSendMessage, strName, strPhone, strPayMethod,
                             strSMJZ, strBJFY, strPaytype, strPaymount, strE, strCOD, strCard, strProduct, strRemark, strDate,
                             strPageCount, strChild, strMother, strMotherid, strMailid, SFMonthlyAccount, strSendaddres) {
        LODOP.ADD_PRINT_SETUP_BKIMG('<img border="0" src="/sf_express/static/src/images/210.jpg"/>');
        LODOP.SET_SHOW_MODE("BKIMG_WIDTH", 756);
        LODOP.SET_SHOW_MODE("BKIMG_HEIGHT", 1070);
        LODOP.SET_SHOW_MODE("BKIMG_IN_PREVIEW", true);
        LODOP.SET_SHOW_MODE("BKIMG_PRINT", true);
        LODOP.ADD_PRINT_BARCODE(216, 234, 208, 45, "128C", strMailid);
        LODOP.SET_PRINT_STYLEA(0, "ShowBarText", 0);
        LODOP.ADD_PRINT_TEXT(261, 309, 110, 20, strMailid);//第一联子弹运单号文本
        LODOP.SET_PRINT_STYLEA(0, "FontName", "Arial");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 10);
        LODOP.SET_PRINT_STYLEA(0, "Bold", 1);
        LODOP.ADD_PRINT_TEXT(212, 469, 96, 20, strExpresstype);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 14);
        LODOP.SET_PRINT_STYLEA(0, "Bold", 1);
        LODOP.ADD_PRINT_TEXT(298, 215, 22, 41, "目的地");
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 7);
        LODOP.SET_PRINT_STYLEA(0, "AlignJustify", 1);
        LODOP.SET_PRINT_STYLEA(0, "LineSpacing", -4);
        LODOP.ADD_PRINT_TEXT(285, 234, 185, 45, strDestcode);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "Arial");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 36);
        LODOP.SET_PRINT_STYLEA(0, "Bold", 1);
        LODOP.ADD_PRINT_TEXT(345, 215, 16, 36, "收件人");
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 7);
        LODOP.SET_PRINT_STYLEA(0, "LineSpacing", -4);
        LODOP.ADD_PRINT_TEXT(353, 234, 340, 31, strAddress);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 10);
        LODOP.SET_PRINT_STYLEA(0, "Bold", 1);
        LODOP.SET_PRINT_STYLEA(0, "LineSpacing", -6);
        LODOP.ADD_PRINT_TEXT(384, 215, 15, 25, "寄件人");
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 7);
        LODOP.SET_PRINT_STYLEA(0, "LineSpacing", -4);
        LODOP.ADD_PRINT_TEXT(383, 236, 255, 27, strSendMessage);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 10);
        LODOP.SET_PRINT_STYLEA(0, "LineSpacing", -1);
        LODOP.ADD_PRINT_TEXT(395, 236, 340, 31, strSendaddres);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 8);
        LODOP.SET_PRINT_STYLEA(0, "LineSpacing", -4);
        LODOP.ADD_PRINT_TEXT(339, 235, 100, 20, strName);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 10);
        LODOP.SET_PRINT_STYLEA(0, "Bold", 1);
        LODOP.ADD_PRINT_TEXT(338, 334, 228, 20, strPhone);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "Arial");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 10);
        LODOP.SET_PRINT_STYLEA(0, "Bold", 1);
        LODOP.ADD_PRINT_TEXT(390, 485, 93, 25, "定时派送");
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 14);
        LODOP.SET_PRINT_STYLEA(0, "Bold", 1);
        LODOP.SET_PRINT_STYLEA(0, "LetterSpacing", -3);
        LODOP.ADD_PRINT_TEXT(415, 211, 101, 20, strPayMethod);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 7);
        // LODOP.ADD_PRINT_TEXT(424, 211, 120, 20, "月结账号:<%=SFMonthlyAccount%>");
        LODOP.ADD_PRINT_TEXT(424, 211, 120, 20, SFMonthlyAccount);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 7);
        LODOP.ADD_PRINT_TEXT(415, 312, 110, 20, strSMJZ);//声明价值
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 7);
        // LODOP.ADD_PRINT_TEXT(424, 312, 95, 20, strBJFY);//保价费用
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 7);
        LODOP.ADD_PRINT_TEXT(461, 217, 20, 35, "托寄物");
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 7);
        LODOP.SET_PRINT_STYLEA(0, "LineSpacing", -4);
        LODOP.ADD_PRINT_TEXT(458, 412, 81, 20, "收件员:282434");
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 7);
        LODOP.SET_PRINT_STYLEA(0, "LetterSpacing", -1);
        LODOP.ADD_PRINT_TEXT(469, 412, 81, 20, strDate);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 7);
        LODOP.SET_PRINT_STYLEA(0, "LetterSpacing", -1);
        LODOP.ADD_PRINT_TEXT(480, 413, 80, 20, "派件人:");
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 7);
        LODOP.SET_PRINT_STYLEA(0, "LetterSpacing", -1);
        LODOP.ADD_PRINT_TEXT(417, 482, 48, 20, "签名:");
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 7);
        LODOP.ADD_PRINT_TEXT(483, 529, 45, 20, "月   日");
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 7);
        LODOP.ADD_PRINT_TEXT(555, 217, 13, 20, "寄件人");
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 7);
        LODOP.SET_PRINT_STYLEA(0, "LineSpacing", -4);
        LODOP.ADD_PRINT_TEXT(567, 237, 340, 31, strSendaddres);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 8);
        LODOP.SET_PRINT_STYLEA(0, "LineSpacing", -4);
        LODOP.ADD_PRINT_BARCODE(496, 329, 211, 40, "128C", strMailid);
        LODOP.SET_PRINT_STYLEA(0, "ShowBarText", 0);
        LODOP.ADD_PRINT_TEXT(537, 396, 141, 20, strMailid);//第二联运单号文本
        LODOP.SET_PRINT_STYLEA(0, "FontName", "Arial");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 10);
        LODOP.SET_PRINT_STYLEA(0, "Bold", 1);
        LODOP.ADD_PRINT_TEXT(590, 217, 17, 25, "收件人");
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 7);
        LODOP.SET_PRINT_STYLEA(0, "LineSpacing", -4);
        LODOP.ADD_PRINT_TEXT(556, 235, 322, 34, strSendMessage);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 8);
        LODOP.SET_PRINT_STYLEA(0, "LineSpacing", -4);
        LODOP.ADD_PRINT_TEXT(589, 237, 100, 20, strName);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 8);
        LODOP.ADD_PRINT_TEXT(589, 334, 225, 20, strPhone);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 8);
        LODOP.ADD_PRINT_TEXT(600, 237, 324, 25, strAddress);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 8);
        LODOP.SET_PRINT_STYLEA(0, "LineSpacing", -4);
        LODOP.ADD_PRINT_BARCODE(729, 339, 222, 35, "128C", strMailid);
        LODOP.SET_PRINT_STYLEA(0, "ShowBarText", 0);
        LODOP.ADD_PRINT_TEXT(764, 396, 143, 20, strMailid);//第三联运单号文本
        LODOP.SET_PRINT_STYLEA(0, "FontName", "Arial");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 10);
        LODOP.SET_PRINT_STYLEA(0, "Bold", 1);
        LODOP.ADD_PRINT_TEXT(781, 218, 15, 20, "寄件人");
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 7);
        LODOP.SET_PRINT_STYLEA(0, "LineSpacing", -4);
        LODOP.ADD_PRINT_TEXT(793, 237, 340, 31, strSendaddres);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 8);
        LODOP.SET_PRINT_STYLEA(0, "LineSpacing", -4);
        LODOP.ADD_PRINT_TEXT(817, 218, 10, 20, "收件人");
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 7);
        LODOP.SET_PRINT_STYLEA(0, "LineSpacing", -4);
        LODOP.ADD_PRINT_TEXT(780, 235, 328, 37, strSendMessage);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 8);
        LODOP.SET_PRINT_STYLEA(0, "LineSpacing", -4);
        LODOP.ADD_PRINT_TEXT(814, 235, 100, 20, strName);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 8);
        LODOP.ADD_PRINT_TEXT(814, 329, 230, 20, strPhone);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 8);
        LODOP.ADD_PRINT_TEXT(826, 235, 333, 27, strAddress);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 8);
        LODOP.SET_PRINT_STYLEA(0, "LineSpacing", -4);
        LODOP.ADD_PRINT_IMAGE(731, 226, 59, 18, '<img border="0" src="/sf_express/static/src/images/LOGO.jpg"/>');
        LODOP.SET_PRINT_STYLEA(0, "Stretch", 1);
        LODOP.ADD_PRINT_IMAGE(752, 225, 63, 20, '<img border="0" src="/sf_express/static/src/images/95338.jpg"/>');
        LODOP.SET_PRINT_STYLEA(0, "Stretch", 1);
        LODOP.ADD_PRINT_IMAGE(509, 227, 59, 18, '<img border="0" src="/sf_express/static/src/images/LOGO.jpg"/>');
        LODOP.SET_PRINT_STYLEA(0, "Stretch", 1);
        LODOP.ADD_PRINT_IMAGE(529, 225, 63, 20, '<img border="0" src="/sf_express/static/src/images/95338.jpg"/>');
        LODOP.SET_PRINT_STYLEA(0, "Stretch", 1);
        LODOP.ADD_PRINT_TEXT(236, 463, 126, 35, strPaytype);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 19);
        LODOP.SET_PRINT_STYLEA(0, "Bold", 1);
        LODOP.SET_PRINT_STYLEA(0, "LetterSpacing", -3);
        LODOP.ADD_PRINT_TEXT(273, 466, 105, 20, strPaymount);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 11);
        LODOP.SET_PRINT_STYLEA(0, "Bold", 1);
        LODOP.ADD_PRINT_TEXT(260, 212, 36, 20, strPageCount);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "Arial");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 10);
        LODOP.SET_PRINT_STYLEA(0, "Bold", 1);
        LODOP.ADD_PRINT_TEXT(262, 250, 56, 20, strChild);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 10);
        LODOP.SET_PRINT_STYLEA(0, "Bold", 1);
        LODOP.ADD_PRINT_TEXT(275, 250, 61, 20, strMother);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 10);
        LODOP.SET_PRINT_STYLEA(0, "Bold", 1);
        LODOP.ADD_PRINT_TEXT(274, 309, 113, 20, strMotherid);//第一联母单运单号文本
        LODOP.SET_PRINT_STYLEA(0, "FontName", "Arial");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 10);
        LODOP.SET_PRINT_STYLEA(0, "Bold", 1);
        LODOP.ADD_PRINT_TEXT(764, 346, 57, 20, strChild);//第三联“子单号”文本
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 10);
        LODOP.SET_PRINT_STYLEA(0, "Bold", 1);
        LODOP.ADD_PRINT_TEXT(538, 341, 62, 20, strChild);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 10);
        LODOP.SET_PRINT_STYLEA(0, "Bold", 1);
        LODOP.ADD_PRINT_TEXT(160, 433, 42, 51, strE);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 36);
        LODOP.SET_PRINT_STYLEA(0, "Bold", 1);
        LODOP.ADD_PRINT_TEXT(161, 331, 101, 46, strCOD);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 36);
        LODOP.ADD_PRINT_TEXT(262, 465, 100, 15, strCard);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 8);
        LODOP.ADD_PRINT_TEXT(462, 235, 175, 30, strProduct);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 8);
        LODOP.SET_PRINT_STYLEA(0, "Alignment", 2);
        LODOP.ADD_PRINT_TEXT(626, 212, 348, 28, strProduct);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 8);
        LODOP.SET_PRINT_STYLEA(0, "Alignment", 2);
        LODOP.ADD_PRINT_TEXT(653, 211, 349, 58, strRemark);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 10);
        LODOP.SET_PRINT_STYLEA(0, "Alignment", 2);
        LODOP.ADD_PRINT_TEXT(852, 209, 351, 29, strProduct);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 8);
        LODOP.SET_PRINT_STYLEA(0, "Alignment", 2);
        LODOP.ADD_PRINT_TEXT(880, 208, 352, 47, strRemark);
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 10);
        LODOP.SET_PRINT_STYLEA(0, "Alignment", 2);
        LODOP.ADD_PRINT_TEXT(415, 397, 97, 20, "计费重量:    KG");
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 7);
        LODOP.ADD_PRINT_TEXT(424, 397, 85, 20, "运费:        元");
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 7);
        LODOP.ADD_PRINT_TEXT(433, 397, 85, 20, "费用合计:    元");
        LODOP.SET_PRINT_STYLEA(0, "FontName", "黑体");
        LODOP.SET_PRINT_STYLEA(0, "FontSize", 7);
    }

    ListController.include({
        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            var self = this;
            // 批量发货操作
            if (self.modelName === 'stock.picking') {
                this.$buttons.on('click', 'button.sf_express_send', function () {
                    var list_ids = self.getSelectedIds()
                    self.do_action({
                        'title': '批量发货',
                        'type': 'ir.actions.act_window',
                        'res_model': 'send.express.order',
                        'views': [[false, 'form']],
                        'view_mode': 'form',
                        'target': 'new',
                        'context': {'default_picking_id': list_ids}
                    });
                });
            }

            //批量打印操作
            if (self.modelName === 'print.order') {
                this.$buttons.on('click', 'button.sf_express_print', function () {
                    return lodop.loadRequiredJS().always(function () {
                        // 如果loadjs成功，初始化LODOP
                        // 失败，getLodop将会提供下载链接
                        window.LODOP = lodop.getLodop();
                    }).then(function () {
                        var list_ids = self.getSelectedIds()
                        if (!list_ids.length) return;
                        if (window.LODOP) {
                            self.model.call("get_json_data", [list_ids]).then(function (res_data) {
                                BatchPrint(res_data);
                                model.call("print_done", [list_ids]);
                            });
                        }
                    });
                });
            }
        }
    })
    ;

});