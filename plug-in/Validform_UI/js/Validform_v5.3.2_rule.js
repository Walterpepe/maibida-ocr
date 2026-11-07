$.extend($.Datatype, {
    "pwd": /^[a-zA-Z][A-Za-z0-9_]{5,19}$/,
    "t": /0\d{2,3}-\d{5,9}|0\d{2,3}-\d{5,9}/,
    "userName": /^[a-zA-Z0-9_]+$/,
    "phone": function (gets, obj, curform, regxp) {
        /*参数gets是获取到的表单元素值，
          obj为当前表单元素，
          curform为当前验证的表单，
          regxp为内置的一些正则表达式的引用。*/
        var reg1 = regxp["m"], reg2 = /[\d]{7}/, mobile = curform.find("input[name='Mobile']");
        if (reg1.test(mobile.val())) { return true; }
        if (reg2.test(gets)) { return true; }
        return false;
    },
    "realName": function (gets, obj) {
        var patrn = /^\s*[\u4e00-\u9fa5]{1,}[\u4e00-\u9fa5.·]{0,15}[\u4e00-\u9fa5]{1,}\s*$/;
        return patrn.test(gets);
    },
    "tel": function (gets, obj) {
        var patrn = /[\d]{7}/;
        return patrn.test(gets);
    },
    "price": function (gets, obj) {
        if (parseInt(gets) >= 0 && parseInt(gets) <= 9999999) { return true; }
    },
    "cjh": function (gets, obj) {
        var patrn = /^[A-Za-z0-9]{17}$/;
        return (patrn.test(gets));
    },
    "idcard": function (gets, obj, curform, datatype) {
        //该方法由佚名网友提供;

        var Wi = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2, 1];// 加权因子;
        var ValideCode = [1, 0, 10, 9, 8, 7, 6, 5, 4, 3, 2];// 身份证验证位值，10代表X;

        if (gets.length == 15) {
            return isValidityBrithBy15IdCard(gets);
        } else if (gets.length == 18) {
            var a_idCard = gets.split("");// 得到身份证数组   
            if (isValidityBrithBy18IdCard(gets) && isTrueValidateCodeBy18IdCard(a_idCard)) {
                return true;
            }
            return false;
        }
        return false;
        function isTrueValidateCodeBy18IdCard(a_idCard) {
            var sum = 0; // 声明加权求和变量   
            if (a_idCard[17].toLowerCase() == 'x') {
                a_idCard[17] = 10;// 将最后位为x的验证码替换为10方便后续操作   
            }
            for (var i = 0; i < 17; i++) {
                sum += Wi[i] * a_idCard[i];// 加权求和   
            }
            valCodePosition = sum % 11;// 得到验证码所位置   
            if (a_idCard[17] == ValideCode[valCodePosition]) {
                return true;
            }
            return false;
        }
        function isValidityBrithBy18IdCard(idCard18) {
            var year = idCard18.substring(6, 10);
            var month = idCard18.substring(10, 12);
            var day = idCard18.substring(12, 14);
            var temp_date = new Date(year, parseFloat(month) - 1, parseFloat(day));
            // 这里用getFullYear()获取年份，避免千年虫问题   
            if (temp_date.getFullYear() != parseFloat(year) || temp_date.getMonth() != parseFloat(month) - 1 || temp_date.getDate() != parseFloat(day)) {
                return false;
            }
            return true;
        }
        function isValidityBrithBy15IdCard(idCard15) {
            var year = idCard15.substring(6, 8);
            var month = idCard15.substring(8, 10);
            var day = idCard15.substring(10, 12);
            var temp_date = new Date(year, parseFloat(month) - 1, parseFloat(day));
            // 对于老身份证中的你年龄则不需考虑千年虫问题而使用getYear()方法   
            if (temp_date.getYear() != parseFloat(year) || temp_date.getMonth() != parseFloat(month) - 1 || temp_date.getDate() != parseFloat(day)) {
                return false;
            }
            return true;
        }
    },
    "checkTime": function (gets, obj, curform, regxp) {
        var beginTime = curform.find("input[name='BeginTime']").val(), endTime = curform.find("input[name='EndTime']").val();
        var beginTime = new Date(beginTime.replace(/\-/g, "\/"));
        var endTime = new Date(endTime.replace(/\-/g, "\/"));
        if (beginTime > endTime) { return false; }
        return true;
    },
    "lt1num": function (gets, obj) {
        if (parseInt(gets) < 1) { return true; }
    },
    "need1": function (gets, obj, curform, regxp) {
        var need = 1,
            numselected = curform.find("input[name='" + obj.attr("name") + "']:checked").length;
        return numselected >= need ? true : "请至少选择" + need + "项！";
    }
});