#coding:utf-8
import hmac
import hashlib
import urllib2
import time
import datetime
from app.basehandler import BaseHandler
from app.utils.zlhttpclient import zlHttpClient
signKey = "sbnzye1t21c26bl12m85i6np5m3y9a0xgf805u0dvn3y2q4pk9"

class HandlerPayHaiWan(BaseHandler):
    def post(self):
        asyx_order_id = self.get_argument("asyx_order_id")
        subject = self.get_argument("subject")
        subject_desc = self.get_argument("subject_desc")
        trade_status = self.get_argument("trade_status")
        amount = self.get_argument("amount")
        channel = self.get_argument("channel")
        order_creatdt = self.get_argument("order_creatdt")
        order_paydt = self.get_argument("order_paydt")
        asyx_game_id = self.get_argument("asyx_game_id")
        pay_order_id = self.get_argument("pay_order_id")
        Memo = self.get_argument("Memo")
        sign = self.get_argument("sign")
        todoSign = asyx_order_id + subject + subject_desc + trade_status + amount + channel + order_creatdt + order_paydt + asyx_game_id + pay_order_id
        print todoSign
        toSign = hmac.new(signKey, todoSign.encode("utf-8"), hashlib.md5).hexdigest()
        print toSign,"==",sign
        result = "failed"
        if sign == toSign and int(trade_status) == 1:
            url = "http://127.0.0.1:8080/HaiWan?Memo=%s&subject=%s&amount=%s&asyx_order_id=%s&order_paydt=%s" %(Memo, subject, amount, asyx_order_id, int(time.mktime(datetime.datetime.strptime(order_paydt, "%Y-%m-%d %H:%M:%S").timetuple())))
            print url
            request = urllib2.Request(url)
            result = urllib2.urlopen(request).read()
        self.write(result)
        self.flush()
        self.finish()
        