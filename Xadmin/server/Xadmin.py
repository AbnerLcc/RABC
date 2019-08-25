#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.urls import path,re_path,include
from django.shortcuts import HttpResponse,render,redirect
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.forms import ModelForm
from django.forms import widgets as wid
from Xadmin.paging.paging_py import Pagination
from django.db.models import Q
import copy
from RBAC.perssiom_data import  Perssion_views,Permission_login_data as Mean_lef
import json
from django.db.models.fields.related import ManyToManyField,ForeignKey
# noinspection PyCallingNonCallable
class Show_list(object):
    def __init__(self,config,request,data_list):
        self.config=config    # 调用该类对象本身,也就说在类中实例化第三方类
        self.request=request
        # 分页
        self.current_page = request.GET.get("page", 1)
        self.all_count = data_list.count()
        self.current_url = request.path
        self.pagination = Pagination(self.all_count, self.current_page, self.current_url, request.GET, per_page=10,
                                     max_show=7)
        # 实例化分页对象
        self.data_list = data_list[self.pagination.start:self.pagination.end]  # 提取分页后数据

        # 批量处理


    def get_greate_action(self,request):
        action = [{"name": i.__name__, "desc": i.shortdesc} for i in self.config.rebulid_action(request)]  # 目的是为了在HTML显示内容
        return action

    # 获取分类数据
    def get_filter_html(self,request):
        catage_list = self.config.filter_list
        url_data =copy.deepcopy(request.GET)            # 获取url路径中参数

        #  分类搜索,去掉页码数,去掉所有不合法字段
        #  字典在for循环中不能够删除数据
        # for k,v in url_data.items():
        #
        #     if k not in self.config.rebulid_display_list():
        #         print(type(k))
        #         del url_data[k]
        #
        # print(url_data)


        link_list={}                  # 因为有两个参数,是相互对应的,因此需要两个参数
        current_url=request.path
        for field in catage_list:  # 拿到分类字段,即组合依据     ["user","tags","category"]
            data_url=copy.deepcopy(url_data)# 之所以放在里面是因为,当下一次循环时,会携带上一个分类依据,因此每一次都应该是新的数据,

            # 如果是普通字段呢,就没有

            filed_obj = self.config.model._meta.get_field(field)
            verbose_name=filed_obj.verbose_name            # 获取字段中文名字

            if isinstance(filed_obj,ForeignKey) or isinstance(filed_obj,ManyToManyField):
                data_list=self.config.model._meta.get_field(field).remote_field.model.objects.all()
                    # 获取外键表所有实例化对象
            else:
               data_list=self.config.model.objects.all()
            label_list=[]
            try:
                current_title=data_url[field]
                data_url.pop(field)
                # data_url.pop("page"),如果上一个条件没有,就会不执行,如果放在这里就会多次循环执行这行代码,因此放在外面合适
            except:
                current_title=0
            s= "<a href='{0}?{1}' class='list-group-item'>全部</a>".format(current_url,data_url.urlencode())
            label_list.append(s)
            for obj in data_list:
                if isinstance(filed_obj,ForeignKey) or isinstance(filed_obj,ManyToManyField):
                    data_url[field]=obj.pk
                    a_text=obj
                else:
                    a_text=getattr(obj,field)    # 拿到当前字段的名字
                    data_url[field]=a_text

                if current_title==str(obj.pk) or current_title==a_text:
                    link="<a href='{0}?{1}' class='list-group-item a_active'>{2}</a>".format(current_url,data_url.urlencode(),a_text)
                else:
                    link="<a href='{0}?{1}' class='list-group-item'>{2}</a>".format(current_url,data_url.urlencode(),a_text)

                label_list.append(link)

            """
            else:       # 如果不是外键字段分类,就没有意义了,但可以通过时间分类,普通字段分类
                data_list=self.config.model.objects.all()
                label_list=[]
                try:
                    current_title=data_url[field]
                    data_url.pop(field)
                    # data_url.pop("page"),如果上一个条件没有,就会不执行,如果放在这里就会多次循环执行这行代码,因此放在外面合适
                except:
                    current_title =0
                s = "<a href='{0}?{1}' class='list-group-item'>全部</a>".format(current_url, data_url.urlencode())
                label_list.append(s)
                for obj in data_list:
                    name=getattr(obj,field)    # 拿到当前字段的名字
                    data_url[field]=name
                    if current_title==name:
                        s = "<a href='{0}?{1}' class='list-group-item a_active'>{2}</a>".format(current_url, data_url.urlencode(),name)
                    else:
                        link = "<a href='{0}?{1}' class='list-group-item'>{2}</a>".format(current_url,data_url.urlencode(),name)
                    label_list.append(s)  
          """


            link_list[verbose_name]=label_list
        return link_list

    # 批量处理函数
    def many_action(self,request,queryset):
        funcation_str = request.POST.get("action", "")
                  # 获取操作命令函数

        try:     # 防止没有选项
            funcation = getattr(self.config, funcation_str)
                  # 在views类中寻找函数名
            funcation(request,queryset)  # 批量处理时
        except:pass
    def get_TableHead(self,request):
        title_list = []
        search_contion=[]
        for field in self.config.rebulid_display_list(request):
            if isinstance(field, str):
                if field == "__str__":
                    title_list.append(self.config.model._meta.verbose_name)  # 如果传显示列表就返回表名

                else:
                    title_list.append(self.config.model._meta.get_field(field).verbose_name)  # 求字段中文名
            else:  # if callable(field)   判断是不是函数                                                                 # 函数怎么命名
                var = field(self.config, header=True)
                title_list.append(var)  # 求函数名

        return title_list
    def get_TableBody(self,request):
        items_list = []
        for obj in self.data_list:            # 表某一行对应的对象
            item=[]

            for field in self.config.rebulid_display_list(request):        #["title","desc",add_0]  ["__str__"]

                   if not callable(field):                           # 如果是字段
                        if field in self.config.list_display_link:      #   判断field是不是指定编辑字段
                            # 如何判断有没有编辑和删除权限
                            url = self.config.get_udate_url(obj)
                            item.append(mark_safe("<a href='%s'>%s</a>"%(url,getattr(obj,field))))
                        # 求字段名
                        else:

                            if field != "__str__":
                                filed_obj=self.config.model._meta.get_field(field)    # 必须拿到的是当前字段对象，否则以下永远不成立
                                if isinstance(filed_obj,ManyToManyField):
                                    manytomany_text=[]
                                    all_obj=getattr(obj, field).all()     # 拿到manytomany中所有对象值
                                    for i in all_obj:
                                        manytomany_text.append(str(i))      # 注意一定要把数据转换成字符串,否则join不起来
                                    item.append("、".join(manytomany_text))

                                #elif isinstance(filed_obj,ForeignKey):
                                #   外键字段to_field  出现bug, 跳不出这个循环,即
                                #    item.append(getattr(obj, field))
                                else:
                                    #   外键字段to_field  出现bug, 跳不出这个循环,

                                    # choices字段判断,在外键中不需要判断,因为其有__str__
                                    if filed_obj.choices:
                                        item.append(getattr(obj, "get_"+field+"_display"))   # getattr 是函数就会执行


                                    else:
                                        item.append(getattr(obj,field))        # 当是多对多的关系时,这个只能显示对象，一对一时也可以



                            else:                     # 如果是字符串__str__
                                item.append(getattr(obj,field))
                   else:
                       item.append(field(self.config,obj))
            items_list.append(item)


        return  items_list


class ModelXadmin(object):
    # list_display=["__str__"],当for循环时,默认取第一个值
    list_display=["__str__",]       # 默认展示模型中__str__方法返回的值
    list_display_link=[]
    Model_Form_class=[]
    search_list=[]
    action=[]
    filter_list=[]
    # 私人个别字段过滤
    private_filter=[]
    def __init__(self,model,site):
        self.model=model
        self.site=site
        self.app_name= self.model._meta.app_label
        self.table_name = self.model._meta.model_name

    # url分发
    @property
    def url(self):                     # self指调用他的对象,也就是site调用
        url = []
        url.append(re_path('^add/$',self.add_views,name="%s_%s_add"%(self.app_name,self.table_name)))
        url.append(re_path('^delete/(\d+)',self.delete_views,name="%s_%s_delete"%(self.app_name,self.table_name)))
        url.append(re_path('^update/(\d+)',self.update_views,name="%s_%s_update"%(self.app_name,self.table_name)))
        url.append(re_path('^check/(\d+)',self.check_views,name="%s_%s_check"%(self.app_name,self.table_name)))
        url.append(re_path('^$',self.list_views,name="%s_%s_home"%(self.app_name,self.table_name)))
        url.extend(self.extra_url())
        # [(re_path('^/ Xadmin / schoolapp / department /add....)],

        #  temp.extend(self.extra_url())
        return url,None,None        # [re_path('^delete/(\d+)',test),],None,None

    def cancle(self,request,customer_id, course_id):
        pass
    def extra_url(self):
        return []
    def get_udate_url(self,obj):
        _url = reverse("%s_%s_update" % (self.app_name, self.table_name), args=[obj.pk, ])  # 反向解析
        return _url

    def get_add_url(self,obj):
        _url = reverse("%s_%s_add" % (self.app_name, self.table_name))  # 反向解析
        return _url
    # 编辑页面,默认的查看字段的方法

    def get_delete_url(self,obj):
        _url = reverse("%s_%s_delete" % (self.app_name, self.table_name), args=[obj.pk, ])  # 反向解析
        return _url
    def get_check_url(self,obj):
        _url = reverse("%s_%s_check" % (self.app_name, self.table_name), args=[obj.pk, ])  # 反向解析
        return _url
    def get_home_url(self):
        _url = reverse("%s_%s_home" % (self.app_name, self.table_name))  # 反向解析
        return _url
    # 查看默认标签
    def search_boutton(self,obj=None,header=False):
        if header:
            return "操作"
        else:
            url = reverse("%s_%s_update"%(self.app_name,self.table_name),args=[obj.pk,])      # 反向解析
            return mark_safe("<a href='%s'>编辑</a>" % url)

    # 选项标签,
    def checkbox_button(self,obj=None,header=False):
        if header:   #    当是表头会传进header=Ture
            return  mark_safe("<label><input type='checkbox' name='check' checked class='control_all'></label>")
        return  mark_safe("<label><input type='checkbox' checked  class='item_choice' value=%s name='item'></label>"%obj.pk)

    # 反向解析添加路径
    def add_url(self, obj=None, header=False):  # 通过传参方法,决定返回那种函数
        if header:
            return "操作"
        else:
            url = reverse("%s_%s_add" % (self.app_name, self.table_name))
            return url

    # 删除标签
    def delete_button(self, obj=None, header=False):
        if header:
            return "操作"
        else:
            url = reverse("%s_%s_delete" % (self.app_name, self.table_name), args=[obj.pk])
            return mark_safe("<a href='%s' class='delete' onclick='return false;'><i class='fa-trash fa'>&ensp;删除</i></a>" % url)


    # 展示的字段和链接进行处理,类的应用值经典
    def rebulid_display_list(self,request):
        tem=[]

        tem.append(ModelXadmin.checkbox_button)         # 把选择框加到表头和表单前面,
               # 之所以用类,是因为在缺省形参中,如果调用一次,之后的参数都会发生改变,
        tem.extend(self.list_display)     # 把实例化对象自身的数据加到tem当中

        if not self.list_display_link:     # 是否传有link项,   权限不在这里加,通过权限判断添加
            tem.append(ModelXadmin.search_boutton)

        # tem.append(ModelXadmin.delete_button)         # 把选择框加到表头和表单前面,

        return tem

    # 批量删除函数
    def delete_table(self, request, queryset):  # 删除数据
        queryset.delete()
    delete_table.shortdesc = "批量删除"



    def rebulid_action(self,request):
        tem_list=[]
        try:
            action=request.action
        except:
            self.action=[]

        if  self.action:
            tem_list=self.action
        return tem_list
    def get_models_form(self):
        if not self.Model_Form_class:
            class Model_Form(ModelForm):
                class Meta:
                    model = self.model
                    fields = "__all__"
                    labels = {
                        ""
                    }
            return  Model_Form      # 查看列表,即主页,并对相应字段配上路径
        else:
            return self.Model_Form_class

    def get_new_form(self,form):

        for bfield in form:
           # from django.forms.boundfield import BoundField
            #print(bfield)
            # print(bfield.field) # 字段对象
            # print("name",bfield.name)  # 字段名（字符串）
            # print(type(bfield.field)) # 字段类型

            from django.forms.models import ModelChoiceField
            from django.forms.fields import FileField

            if isinstance(bfield.field, FileField):      # 添加file标志,方便ajax控制
                bfield.is_field=True


            if isinstance(bfield.field,ModelChoiceField):        # 如果是多对多字段
                bfield.is_pop=True

                # print("=======>",bfield.field.queryset.model) # 一对多或者多对多字段的关联模型表

                related_model_name=bfield.field.queryset.model._meta.model_name
                related_app_label=bfield.field.queryset.model._meta.app_label


                _url=reverse("%s_%s_add"%(related_app_label,related_model_name))
                        # 跳转路径
                bfield.url=_url+"?ForeignKeyLabel_id=id_%s"%bfield.name
                        # 带参数目的是为了在添加视图中判断是直接访问路径还是间接访问路径
        return form

    # 分页
    def paging(self, request, data_list):
        current_page = request.GET.get("page", 1)
        all_count = data_list.count()
        current_url = request.path
        pagination = Pagination(all_count, current_page, current_url, request.GET, per_page=10, max_show=7)
        data_list = data_list[pagination.start:pagination.end]
        return pagination,data_list

    def search_contition(self,request):
        key_word=request.GET.get("key_word","")
        self.key_word=key_word
        contion = Q()
        contion.connector = "or"  # 改变q条件之间的关系为   or  关系


        if not self.search_list:
            pass

        else:
            for field in self.search_list:
                contion.children.append((field+"__contains",key_word))




        # 分类查询，因为不判断会导致字段错误
        if self.filter_list:       # 没有数据,for循环会报错
            contion.connector = "and"
            param=copy.deepcopy(request.GET)           # 查询条件
             # 也可以用if语句

            # try:           这种方法写死了，如果有其他变量照样报错，如手动输入的参数
            #     param.pop("page")
            # except:
            #     pass
            for k,v in param.items():
                if k in self.filter_list:
                    contion.children.append((k,v))

        # 个别表过滤查询

        if self.private_filter:
            contion.connector = "and"
            for i in self.private_filter:

                private_contion=request.GET.get(i,None)

                if private_contion:

                    contion.children.append((i,private_contion))


        return contion
    def list_views(self, request, *args):

        # 条件合并
        con=self.search_contition(request)
        if con:

            data_list=self.model.objects.filter(con)
        else:
            data_list=self.model.objects.all()    # 如何判断是查询还是分页



        show_list=Show_list(self,request,data_list)
        add_url=self.add_url()
        verbose_name=self.model._meta.verbose_name

        # 批量处理
        mamy_action=show_list.get_greate_action(request)

        if request.method == "POST":
            condition = request.POST.getlist('item', "")
            queryset = self.model.objects.filter(pk__in=condition)
            show_list.many_action(request,queryset)

        link_list=show_list.get_filter_html(request)

        thead=show_list.get_TableHead(request)
        tbody=show_list.get_TableBody(request)


        return render(request, "XXadmin/XXadmin_check.html",
                      {
                       "add_url":add_url,
                       "show_list":show_list,
                          "link_list":link_list,
                          "verbose_name":verbose_name,
                          "thead":thead,
                          "tbody":tbody,
                          "mamy_action":mamy_action,
                      })

    def add_views(self,request):
        Model_Form = self.get_models_form()
        form=Model_Form()
        verbose_name = self.model._meta.verbose_name
        if request.method == "POST":
            form=Model_Form(request.POST,request.FILES)
            if form.is_valid():
                obj=form.save()                    # 插入数据后的实例话对象

                ForeignKeyLabel_id= request.GET.get("ForeignKeyLabel_id", None)
                if not ForeignKeyLabel_id:
                    return redirect(self.get_home_url())
                else:
                    data={"ForeignKeyLabel_id":ForeignKeyLabel_id,"text":str(obj),"pk":obj.pk}
                    return render(request,'XXadmin/pop.html',{"data":data})

            form = self.get_new_form(form)
            return render(request, "XXadmin/add.html", locals())

        form = self.get_new_form(form)
                  # 展现所有的字段
        return render(request,"XXadmin/add.html",{"form":form})
    def check_views(self,request,pk):

        return HttpResponse("05")
    def update_views(self,request,pk):
        verbose_name = self.model._meta.verbose_name
        obj=self.model.objects.filter(pk=pk).first()
        form = self.get_models_form()

        if request.method == "POST":
            form=form(request.POST,request.FILES,instance=obj,)
            if form.is_valid():
                form.save()
                return redirect(self.get_home_url())
            form = self.get_new_form(form)
            return render(request, "XXadmin/edict.html", {"form": form,"verbose_name":verbose_name})
        form=form(instance=obj)
        form = self.get_new_form(form)
        return render(request, "XXadmin/edict.html", {"form": form,"verbose_name":verbose_name})
    def delete_views(self,request,pk):
        self.model.objects.filter(pk=pk).delete()
        return redirect(self.get_home_url())



class XadminSite(object):
    def __init__(self):
        self._registry={}

    def all_table(self,request):
        tr_html=""
        url={}
        count=0
        for model, wait_class in self._registry.items():
            count+=1
            app_name = model._meta.app_label
            table_name = model._meta.model_name
            verbose_name=model._meta.verbose_name
            check_url=reverse("{0}_{1}_home".format(app_name,table_name))
            add_url=reverse("{0}_{1}_add".format(app_name,table_name))

            # url[verbose_name]=url1


            tr='<tr><td>{0}</td><td><a href="{1}">{2}</a></td>   <td><a href="{3}"> <i class ="fa fa-plus"></i>&emsp;添加</a></td></tr>'.format(count,check_url,verbose_name,add_url)
            tr_html=tr_html+tr
        url=reversed("all")
        return render(request,"XXadmin/home.html",{"tr_html":tr_html})

    def get_url(self):    # 对所有的表生成相应的路径    这是url调用的,因此此时的self就和url中self是一样的
        url = []
        for model, wait_class in self._registry.items():            # Xadmin.site.register(Blog)--->self._registry[model]=admin_class(model,self) ={blog:ModelXadmin(blog,site)}
            app_name = model._meta.app_label
            table_name = model._meta.model_name
            url_base = re_path('^{0}/{1}/'.format(app_name,table_name),wait_class.url)       # 假如是blog注册                 re_path('app01/blog',ModelXadmin(Blog,site))
            # 用配置类分发路径,这样我就可以拿到配置类内的所有方法,包括                                                              re_path('app01/article',ModelXadmin(Article,site))

            url.append(url_base)
            s = re_path('^{0}/$'.format(app_name), self.all_table, name="all")  # 添加所有表页面
            url.append(s)
        return url     #  [app01/article/,[re_path('^delete/(\d+)',test),],None,None]
    @property                                        #   相当于把结果封装成列表形式
    def urls(self):
        return self.get_url(), None, None        #  [app01/article/,[re_path('^delete/(\d+)',test),],None,None],None,None
                                                     # 这个self是site调用这个方法,因此这个self指的是site,谁调用方法,方法里面的self就是该对象

    def register(self,model,admin_class=None,**option):
        if not admin_class:
            admin_class=ModelXadmin
        self._registry[model]=admin_class(model,self)     # z注意这里需要传值,即把需要的值放在init里面,    model指的注册时传进来的表名
                                                            # (UserInfo,UserInfoConfig)    UserInfo = UserInfoConfig(model,site)
site=XadminSite()
#   Xadmin.site.urls

# app01/article/add/1
# 那个对象调用方法


# 路径在django启动的时候就生成的,但是匹配却是一层一层往上找的
# 加入
