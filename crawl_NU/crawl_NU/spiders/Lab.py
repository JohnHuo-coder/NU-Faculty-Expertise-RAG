import scrapy
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from crawl_NU.items import LabItem

class LabSpider(scrapy.Spider):
    name = "Lab"
    allowed_domains = ["www.mccormick.northwestern.edu"]
    start_urls = ["https://www.mccormick.northwestern.edu/computer-science/research/groups-labs.html"]
    # rules = (
    #     Rule(
    #         LinkExtractor(
    #             allow=(r'profiles/'),
    #             deny=(r'/login', r'/signup'), 
    #         ),
    #         callback='parse_page',
    #         follow=False,
    #     )
    # )
    

    def parse(self, response):
        main = response.css("#main-content")
        if not main:
            return
        main = response.css("#main-content")
        for node in main.css("h2"):
            labItem = LabItem()
            lab_name = self.extract_pure_link(node)
            lab_desc, lab_leader = self.get_description(node)
            labItem["name"] = lab_name
            labItem["description"] = lab_desc
            if lab_leader:
                labItem["leader"] = lab_leader
            yield labItem

    def get_description(self, h2_node):
        lines = []
        leader_name = ""
        for node in h2_node.xpath("following-sibling::node()"):
            if isinstance(node.root, str): 
                text = node.get().strip()
                if text:
                    lines.append(text)
                continue
            if node.root.tag == "p" and node.root.get("class") != "back_to_top":
                text, name = self.extract_p_with_leader_name(node)
                leader_name = name
                lines.append(text)
            else:
                break
        description = "\n".join(lines)
        return description, leader_name
    
    def extract_pure_link(self, a):
        text = a.css("::text").get()
        href = a.css("::attr(href)").get()
        formatted_text = f'{text} ({href})'
        return formatted_text
    
    def extract_p_with_leader_name(self, p):
        parts = []
        name = ""
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
                name = text
            else:
                text = node.xpath("string()").get()
                if text:
                    parts.append(text)
        content = "".join(parts).strip()
        return content, name
