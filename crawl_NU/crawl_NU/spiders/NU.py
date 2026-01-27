import scrapy
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor

class NuSpider(scrapy.Spider):
    name = "NU"
    allowed_domains = ["www.mccormick.northwestern.edu"]
    start_urls = ["https://www.mccormick.northwestern.edu/research-faculty/directory/faculty-search-list.xml"]
    # rules = (
    #     # profile 页面
    #     # 1. 匹配个人 profile 页面 - 只要包含 profiles/ 路径就进入 parse_page
    #     Rule(
    #         LinkExtractor(
    #             allow=(r'profiles/'),
    #             deny=(r'/login', r'/signup'), # 暂时去掉参数过滤，防止误杀
    #         ),
    #         callback='parse_page',
    #         follow=False,
    #     ),
    #     # 2. 匹配目录页及其分页 - 保证爬虫能在目录里跑起来，寻找更多 profile 链接
    #     Rule(
    #         LinkExtractor(
    #             allow=(r'/research-faculty/directory/'),
    #             # 排除已经匹配过的 profiles 路径，避免逻辑混淆
    #             deny=(r'/profiles/', r'/login', r'/signup'),
    #         ),
    #         follow=True,
    #     )
    # )
    def parse(self, response):
        # XML 里的每个 <person> 节点就是一个教授
        # 注意：需要根据实际 XML 标签名微调，通常是 person 或 item
        faculties = response.xpath("//faculty") 
        
        for faculty in faculties:
            # 2. 提取相对路径，例如: /research-faculty/directory/profiles/abdeljawad-fadi.html
            relative_link = faculty.xpath("./pageLink/text()").get()
            if relative_link:
                # 3. 拼接完整 URL 并发送请求，回调你原来的 parse_page 函数
                yield response.follow(relative_link, callback=self.parse_page)
    # def parse_page(self, response):
    #     main = response.css("#main-content")
    #     name = main.css("h1#page-title::text").getall()
    #     name = " ".join(t.strip() for t in name if t.strip())
    #     position = main.css("h2::text, h2 span::text").getall()
    #     position = "".join(
    #         t.strip()
    #         for t in main.css("h2 *::text, h2::text").getall()
    #         if t.strip())

    #     blocks = main.css("p, ul")

    #     merged_paragraphs = []
    #     current_para = ""

    #     for block in blocks:
    #         tag = block.root.tag

    #         if tag == "p":
    #             # 如果之前有内容，先存
    #             if current_para.strip():
    #                 merged_paragraphs.append(current_para.strip())
    #             # 开启新段落
    #             current_para = " ".join(
    #                 t.strip()
    #                 for t in block.css("::text").getall()
    #                 if t.strip()
    #             )

    #         elif tag == "ul":
    #             # 把 ul 的 li 合并到当前 p
    #             items = [
    #                 t.strip()
    #                 for t in block.css("li ::text").getall()
    #                 if t.strip()
    #             ]
    #             if items:
    #                 current_para += "\n" + "\n".join(f"- {i}" for i in items)

    #     # 最后一个段落别忘了加
    #     if current_para.strip():
    #         merged_paragraphs.append(current_para.strip())

    #     yield {
    #         "url": response.url,
    #         "name": name,
    #         "position": position,
    #         "text": "\n".join(merged_paragraphs)
    #     }

    def parse_page(self, response):
        main = response.css("#main-content")
        if not main:
            return
        result = {}
        main = response.css("#main-content")
        name = main.css("h1#page-title::text").getall()
        name = " ".join(t.strip() for t in name if t.strip())
        result["name"] = name

        info_left = main.css("#faculty-profile-left")[0]

        position = info_left.css("p.title::text").getall()
        position = "\n".join(p.strip() for p in position)
        result["position"] = position

        for node in info_left.css("h2"):
            field_name, field_text = self.get_content(node)
            result[field_name] = field_text


        info_right = main.css("#faculty-profile-right")[0]
        for node in info_right.css("h2"):
            field_name, field_text = self.get_content(node)
            result[field_name] = field_text

        yield result

    def get_content(self, h2_node):
        field_name = " ".join(
            t.strip()
            for t in h2_node.css("::text").getall()
            if t.strip()
        )
        lines = []
        for node in h2_node.xpath("following-sibling::node()"):
            # text node
            if isinstance(node.root, str): 
                # 这是一个文本节点
                text = node.get().strip()
                if text:
                    lines.append(text)
                continue
            if node.root.tag == "p":
                text = self.extract_p_with_links(node)
                lines.append(text)
            elif node.root.tag == "a":
                formatted_text = self.extract_pure_link(node)
                lines.append(formatted_text)
            elif node.root.tag == 'ul':
                list_items = self.extract_ul_content(node)
                lines.append(list_items)
            elif node.root.tag == "br":
                continue
            else:
                break
        field_text = "\n".join(lines)
        return field_name, field_text
    
    def extract_pure_link(self, a):
        text = a.css("::text").get()
        href = a.css("::attr(href)").get()
        formatted_text = f'{text}: {href}'
        return formatted_text
    
    def extract_p_with_links(self, p):
        parts = []
        for node in p.xpath("node()"):
            if isinstance(node.root, str): 
                text = node.get()
                if text:
                    parts.append(text)
                continue
            if node.root.tag == "a":
                text = node.xpath("string()").get().strip()
                href = node.attrib.get("href")

                if href:
                    parts.append(f"{text} ({href})")
                else:
                    parts.append(text)
            else:
                text = node.xpath("string()").get()
                if text:
                    parts.append(text)

        return "".join(parts).strip()
    
    def extract_ul_content(self, ul):
        items = [
            t.strip()
            for t in ul.css("li ::text").getall()
            if t.strip()
        ]
        if not items:
            return ""
        return "\n".join(f"- {i}" for i in items)
