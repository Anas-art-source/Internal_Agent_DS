




def get_update_dataset_prompt(prompt_data):
    return f"""
    ## Tables available are:
    1. `product` - table for catalog data. Columns are:
       * `productId`: varchar -  Numeric value stored as string. It is the id of a products with all of its variations(sizes, colors, etc). Always access a prodcutId with a DISTINCT operator.
       * `sku`: varchar - Numeric value stored as string. The id of a unique variation of a productId (example: id of specific size of a prodcut)
       * `title`: varchar - The name of the item.
       * `visionCategoryName` - varchar: The fashion category of an item. Available categories are: {prompt_data['visionCategoriesAvailable']}
       * `category`: varchar - The structure of the e-comm navigation. Available categories are: {prompt_data['categories']}
       * `price`: numeric -  The price of the item.
       * `salePrice`: `numeric` - The discounted price of the item. Only to be used if explicitly asked by user.
       * `stock`: bool - An attribute of a sku. Indicates if a given sku is available in inventory. Be aware the a product id has several skus. ALWAYS search for products that are in inventory, unless user asks for historical items or sales data analysis.
       * `size`: varchar - Unique available values for this column are: {prompt_data['sizes']}
       * `collections`: varchar - Name of the collection for a given season. Unique available values for this column are: {prompt_data['collections']}
       * `brands`: varchar - Name of the brand that is sold in the catalog. Unique available values for this column are: {prompt_data['brands']}

    2. `sales_history` - table for sales data. Columns are: 
       * `orderId`: varchar - The id of an order/ purchase. The same order may have as many rows as there are items on it;
       * `total_Items_value`, `totaldiscountvalue` , `totalfreightvalue`: float8 - The total value, discount and freight value of an order;
       * `creationDate`: timestamp -  Date of an order.
       * `item_sku`: varchar (foreign key) - sku id. Same as `sku` column in `product` table
       * `item_productId`: varchar  (foreign key) - product id. Same as `productId` column in `product` table.
       * `item_quantity` (varchar): item quantity
       * `item_price`: float8 - Price of the item in an order.
       * `userProfileId`: varchar -  id of customer that made teh purchase
       * `city`, `state`, `country`, `neighborhood`: varchar - Columns containing information on city, state, country, neighborhood of the address of an order.
       * `geoCoordinates`: POINT - geo coordinates of the address of an order. Example: (-43.93443298339844,-19.928903579711914);
       * `utmiCampaign`, `utmSource`, `utmMedium`, `utmPartner`: varchar - Identifier of the online source of an order.

## Guidelines for using Catalog data (table name: `product`):
- For category, sizes, and collection you must match the user query to available values for each one.
- When checking if a product has available inventory, you must check the inventory of skus under it. A product might be avaiable in one size but not in other.
- The color or pattern name may be in the title, so use the LIKE clause with LOWER to ensure case sensitivity does not affect the query.
- Users may call a item by its name. When looking for product names, try to also filter category if available.
- Always use double quotes for column names and single quotes for text values and put the entire query between triple quotes.
- Consider numeric, boolean, and textual values appropriately for their data type.
- Ensure that queries are optimized for performance, especially when involving multiple filters.
- Return the query directly without the word SQL in front.
- Do not add a semicolon at the end of the query.
- You may select columns that are relevant to formulate an answer.
- When grouping columns to calculate a result ONLY group by the columns that answers the user question.

* Catalog DB is on Postgres which is case sensitive. Below a few SQL Query examples:
- '''SELECT "productId",  FROM product WHERE "price" > 100 AND "stock" = true''' (returns all products with a price greater than 100)
- '''SELECT "productId",  FROM product WHERE "visionCategoryName" = 'dresses' AND "stock" = true''' (returns all dresses in inventory)


## Guidelines for using Sales data (table name: `sales_history`):
- Do NOT assume sales_history has the same columns available on catalog. On sales_history Use item_sku,item_productId to match with sku and productId on Catalog;
- When generating a sales report of a period or a item, focus on focus on revenue values. Only count the number of items sold if users explicitly asks for this analysis;

* sales_history DB is on Postgres which is case sensitive. Below a few SQL Query examples:
- '''SELECT "item_productId", SUM(item_quantity::INTEGER) AS total_quantity_sold FROM sales_history GROUP BY "item_productId" ORDER BY total_quantity_sold DESC LIMIT 1''' (returns the productId of the item that was most sold)
- '''WITH top_selling_products AS (
    SELECT 
        "item_productId",
        SUM(CAST("item_price" AS FLOAT) * CAST("item_quantity" AS INTEGER)) AS total_sales_value
    FROM 
        sales_history
    GROUP BY 
        "item_productId"
    ORDER BY 
        total_sales_value DESC
    LIMIT 5
)
SELECT 
    p."productId", 
    tsp.total_sales_value
FROM 
    product p''' (returns the report on top 5 best selling products)
    
    
## When combining catalog and sales history data:
- Do not filter inventory availability for products that are listed on sales history;
- Prioritize productId over sku. 


When necessary, combine multiple conditions to further refine the results.
Ensure that queries return accurate and relevant results based on the provided instructions.

"""