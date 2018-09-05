import copy


class MyPage(object):
    def __init__(self, page_num, all_data_amount, request,per_page_data=5, page_show_tags=11):
        '''
        :param page_num: 当前页码
        :param all_data_amount:  总的数据量
        :param url_prefix:  页码a标签的url前缀
        :param per_page_data:  每页显示多少条数据
        :param page_show_tags:  页面上显示多少个页码
        '''
        self.page_num = page_num
        self.all_data_amount = all_data_amount
        self.per_page_data = per_page_data
        self.page_show_tags = page_show_tags

        new_request_GET = copy.deepcopy(request.GET)
        self.new_request_GET = new_request_GET

        try:
            page_num = int(page_num)
        except Exception:
            page_num = 1
        # 如果当前页码小于等于0，返回第一页
        if page_num <= 0:
            page_num = 1

        # 通过总数据的条数来计算有多少页,a为商，b为余数，如果余数！=0，总页数=a+1，否则=a
        total_page_num, more = divmod(self.all_data_amount, self.per_page_data)
        if more:
            total_page_num += 1

        # 如果当前页码大于总的页码数，返回最后一页
        if page_num > total_page_num:
            page_num = total_page_num

        if total_page_num == 0:
            page_num = 1

        page_start_num = (page_num - 1) * self.per_page_data
        page_end_num = page_num * self.per_page_data
        self.page_num = page_num
        self.page_start_num = page_start_num
        self.page_end_num = page_end_num
        self.total_page_num = total_page_num

    @property
    def start(self):
        return self.page_start_num

    @property
    def end(self):
        return self.page_end_num

    def ret_html(self):

        show_tags_left = self.page_num - self.page_show_tags // 2
        show_tags_right = self.page_num + self.page_show_tags // 2

        # 控制两端不超出显示
        if show_tags_left <= 0:
            show_tags_left = 1
            show_tags_right = self.page_show_tags
        if show_tags_right >= self.total_page_num:
            show_tags_right = self.total_page_num
            show_tags_left = self.total_page_num - self.page_show_tags + 1

        # 当总页码不够最多显示的页码数，只需要三页，肯定不够9页，没我们就显示3页
        if self.total_page_num < self.page_show_tags:
            show_tags_left = 1
            show_tags_right = self.total_page_num
        start = '<nav aria-label="Page navigation"> <ul class="pagination">'
        end = '</ul></nav>'
        self.new_request_GET["page"] = 1
        first_page_tag = '<li><a href="?{}">首页</a></li>'.format(self.new_request_GET.urlencode())
        self.new_request_GET["page"] = self.total_page_num
        last_page_tag = '<li><a href="?{}">尾页</a></li>'.format(self.new_request_GET.urlencode())
        if self.page_num - 1 == 0:
            self.new_request_GET["page"] = 1
        else:
            self.new_request_GET["page"] = self.page_num - 1
        front_page_tag = '<li><a href="?{}">&laquo;</a></li>'.format(self.new_request_GET.urlencode())

        if self.page_num + 1 > self.total_page_num:
            self.new_request_GET["page"] = self.total_page_num
        else:
            self.new_request_GET["page"] = self.page_num + 1
        next_page_tag = '<li><a href="?{}">&raquo;</a></li>'.format(self.new_request_GET.urlencode())

        page_tag_html = ''
        for i in range(show_tags_left, show_tags_right + 1):
            self.new_request_GET["page"] = i
            if i == self.page_num:
                page_tag_html += '<li class="active"><a href="?{0}">{1}</a></li>'.format(
                    self.new_request_GET.urlencode(),i )
            else:
                page_tag_html += '<li><a href="?{0}">{1}</a></li>'.format(self.new_request_GET.urlencode(),i)
        page_tag_html = start + front_page_tag + first_page_tag + page_tag_html + last_page_tag + next_page_tag + end

        return page_tag_html
