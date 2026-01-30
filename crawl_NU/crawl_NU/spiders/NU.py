import scrapy
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor

class NuSpider(scrapy.Spider):
    name = "NU"
    allowed_domains = ["www.mccormick.northwestern.edu"]
    start_urls = ["https://www.mccormick.northwestern.edu/research-faculty/directory/faculty-search-list.xml"]
    # rules = (
    #     Rule(
    #         LinkExtractor(
    #             allow=(r'profiles/'),
    #             deny=(r'/login', r'/signup'), # 暂时去掉参数过滤，防止误杀
    #         ),
    #         callback='parse_page',
    #         follow=False,
    #     ),
    #   
    #     Rule(
    #         LinkExtractor(
    #             allow=(r'/research-faculty/directory/'),
    #            
    #             deny=(r'/profiles/', r'/login', r'/signup'),
    #         ),
    #         follow=True,
    #     )
    # )
    def parse(self, response):
        faculties = response.xpath("//faculty") 
        
        for faculty in faculties:
            relative_link = faculty.xpath("./pageLink/text()").get()
            if relative_link:
                yield response.follow(relative_link, callback=self.parse_page)
    

    def parse_page(self, response):
        main = response.css("#main-content")
        if not main:
            return
        result = {}
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
            if isinstance(node.root, str): 
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
