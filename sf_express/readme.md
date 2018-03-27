# coding: utf-8

#####顺丰BSP V3.5 2018-1-23 Gavin GU
# 测试账号
#bsp_head:BSPdevelop
#checnpassword:j8DzkIFgmlomPt0aLuwU
#url:	http://bsp-ois.sit.sf-express.com:9080/bsp-ois/ws/sfexpressService?wsdl

#lodop云打印
#http://www.c-lodop.com/download.html

###########以下为快递请求信息报文
##收件信息
#### orderid客户订单号
#### d_company收件公司
#### d_contact联系人
#### d_tel联系电话
#### d_mobile手机号码
#### d_province省
#### d_city市
#### d_county区 / 县
#### d_address详细地址
##express_type 顺丰标快--1;顺丰特惠--2;顺丰次晨--5;顺丰即日--6;云仓专配次日--37;云仓转配隔日--38;
##pay_method付款方式：1:寄方付(寄付月结、寄付现结）2:收方付3:第三方付


## 货品信息
## orderid客户订单号
## Cargo##商品名称
## count商品数量
## unit单位
## weight单重
## amount单价
## currency结算货币（国际件用）
## source_area原产地（国际件用）

## 订单信息
## orderid订单号
## express_type业务类型
## pay_method支付方式
## parcel_quantity包裹数
## custid月结卡号
## cargo_total_weight快件总重量
## sendstarttime发货时间
## order_source订单来源
## remark备注信息

# 寄件信息
# j_company寄件公司
# j_contact联系人
# j_tel联系电话
# j_mobile联系手机
# j_province省
# j_city市
# j_county区
# j_address详细地址


