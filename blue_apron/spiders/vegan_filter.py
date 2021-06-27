import scrapy

class VeganFilterSpider(scrapy.Spider):
    name = 'vegan_filter'
    allowed_domains = ['www.blueapron.com']
    veg_url = 'https://www.blueapron.com/cookbook/vegetarian?page='

    #pagination we will loop thru
    start_pg = 1

    #recipes url
    recipes  = 'https://www.blueapron.com'

    #set of non vegan but vegatarian foods
    not_vegan = {'cheese', 'egg', 'honey', 'milk', 'yogurt', 'dairy'}

    def start_requests(self):
        yield scrapy.Request(
            url = self.veg_url + str(self.start_pg),
            callback=self.parse
        )
    
    #gets all recipes in vegatarian cookbook
    def parse(self, response):

        #gets the 12 recipes from the page
        items = response.xpath("//div[@class='recipe-thumb col-md-4']")
        for item in items:
            recipe_url = item.xpath(".//@href").extract()
            recipe_name = item.xpath(".//h3/text()").extract() + item.xpath(".//h4/text()").extract()

            
            yield scrapy.Request(
                url = self.recipes + recipe_url[0],
                callback = self.parse_recipe,
                meta = {
                'name' : recipe_name[0],
                'url' : self.recipes + recipe_url[0]
            }
            )

        
        #pagination
        if self.start_pg < 100:
            self.start_pg += 1
            yield scrapy.Request(
            url = self.veg_url + str(self.start_pg),
            callback=self.parse,
        )
        
    
    #checks if ingreidents are vegan-friendly
    def parse_recipe(self, response):

        #get all ingridents
        ingridents = response.xpath("//li[@class='ba-info-list__item']")

        #boolean set True will be false if any ingrident is not Vegan
        vegan = True

        #loop thru ingridents
        for ingrident in ingridents:

            #extract ingrident name
            ingri_name = ingrident.xpath(".//div[@class='non-story']//text()").extract()
            if len(ingri_name) > 0:
                ingri_name = ingri_name[-1]
                ingri_name = ingri_name.replace("/n", "")
                ingri_name = ingri_name.replace(" ", "")
                ingri_name = ingri_name.lower()

                #loop thru set not_vegan
                for item in self.not_vegan:
                    if item in ingri_name:
                        vegan = False 
                        
        if vegan:
            yield{
                'recipe' : response.request.meta['name'],
                'url' : response.request.meta['url']
            }











