#!/usr/bin/env python
# -*- coding:utf-8 -*-

import copy

class Pagination(object):

    def __init__(self, data_num, current_page, current_url,request_get, per_page=10, max_show=3):
        """
        进行初始化.
        :data_num: 数据总数
        current_page: 当前页
        :url_prefix: 当前页码url
        :per_page: 每页显示多少条数据
        : max_show: 页面最多显示多少个页码
        :request_get:    request.GET
        """
        self.data_num = data_num
        self.per_page = per_page
        self.max_show = max_show
        self.current_url = current_url

        # 把页码数算出来
        self.total_page, more = divmod(data_num, per_page)
        if more:
            self.total_page += 1

        # 算出当前页码
        try:
            self.current_page = int(current_page)
        except Exception as e:
            self.current_page = 1
            # 如果URL传过来的页码数是负数
        if self.current_page <= 0:
            self.current_page = 1
            # 如果URL传过来的页码数超过了最大页码数
        elif self.current_page > self.total_page and self.total_page:
            self.current_page = self.total_page  # 默认展示最后一页



        # 页码数的一半 算出来
        self.half_show = max_show // 2


        # 页码最左边显示多少,确定最大页码数是否大于展示最大页码数
        if self.max_show>self.total_page:                       # 最大页码数 max_show>self.total_page:说明剩下的if语句 max<total,非常经典条件处理
            self.page_start = 1
            self.page_end = self.total_page                   #  如果  total < show

        elif self.current_page - self.half_show <= 1:         #current_page有效,说明total>half
            self.page_start = 1
            self.page_end = self.max_show                   #  如果  total < show
        elif self.current_page + self.half_show >= self.total_page:  # 如果右边越界,total>half_show
            self.page_end = self.total_page
            self.page_start = self.total_page - self.max_show      #   总
        else:
            self.page_start = self.current_page - self.half_show
            # 页码最右边显示
            self.page_end = self.current_page + self.half_show
        self.request_params=copy.deepcopy(request_get)            # 复制一份原有传进的的参数,不影响原有数据,当在函数下执行时

    @property
    def start(self):
        # 数据从哪儿开始切
        return (self.current_page - 1) * self.per_page

    @property
    def end(self):
        # 数据切片切到哪儿
        return self.current_page * self.per_page

    def get_page_html(self):

        l=[]

        for i in range(self.page_start, self.page_end + 1):
            self.request_params["page"] = i
            if i == self.current_page:
                tmp = '<li class="active"><a href="{0}?page={1}">{2}</a></li>'.format(self.current_url,self.request_params.urlencode(), i)
            else:
                tmp = '<li><a href="{0}?{1}">{2}</a></li>'.format(self.current_url,self.request_params.urlencode(),i)                   # 把字典转换成等式,i)
            l.append(tmp)
         # request.Get拿到的是字典形式参数   <QueryDict: {'page': ['7'], 'gt': ['10']}>
         # request_params.urlencode()  把chuanjinlai的参数转化成page=7&gt=10

            # 加一个下一页上一页,首页,末页
        if self.total_page:
            if self.current_page == 1 and self.total_page==1:
                l.insert(0,'<li class="disabled" ><a href="#">«</a></li>')
                l.append('<li class="disabled"><a href="#">»</a></li>')
            elif self.current_page==1:
                l.insert(0, '<li class="disabled" ><a href="#">«</a></li>')
                self.request_params["page"] =  self.current_page + 1
                l.append('<li><a href="{}?{}">»</a></li>'.format(self.current_url,self.request_params.urlencode()))
            elif self.total_page==self.current_page:
                self.request_params["page"] = self.current_page - 1
                l.insert(0, '<li ><a href="{}?{}">«</a></li>'.format(self.current_url,self.request_params.urlencode()))
                self.request_params["page"] = self.total_page
                l.append('<li class="disabled"><a href="{0}?{1}">»</a></li>'.format(self.current_url,self.request_params.urlencode() ))
            else:
                self.request_params["page"] = self.current_page - 1
                l.insert(0, '<li ><a href="{0}?{1}">«</a></li>'.format(self.current_url,self.request_params.urlencode()))

                self.request_params["page"] = self.current_page + 1
                l.append('<li><a href="{0}?{1}">»</a></li>'.format(self.current_url, self.request_params.urlencode()))

            self.request_params["page"] =1
            l.insert(0, '<li ><a href="{}?{}">首页</a></li>'.format(self.current_url,self.request_params.urlencode()))
            self.request_params["page"] =self.total_page
            l.append('<li ><a href="{}?{}">尾页</a></li>'.format(self.current_url,self.request_params.urlencode()))
        return l                                  # 有什么用