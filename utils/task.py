
class Task:
    def __init__(self, task_list):
        self.task_list = task_list
        self.tasks = self.initialize()
        
    def initialize(self):
        tasks = []
        for i, task in enumerate(self.task_list):
            tasks.append({
                "index": i+1,
                "task": task,
                "status": "open"
            })
        return tasks
    def update_task(self, index, status):
        for item in self.tasks:
            if item["index"] == index:
                item["status"] = status

    def get_tasks(self):
        return self.tasks
    
    def get_task_template(self):
        str_out = ""
        for task in self.tasks:
            str_out += str(task['index']) + ". "
            str_out += task['task'] + ".  " + "(" + "Status: " + task['status'] + ")\n\n"
        return str_out
    
    def get_task_template_with_number(self):
        str_out = ""
        for task in self.tasks:
            str_out += "Task Number(" + str(task['index']) + ") : "
            str_out += task['task'] + "  " + "(" + "Status: " + task['status'] + ")\n"
        return str_out
    
    def get_latest_successful_task(self):
        successful_last_idx = None
        for task in self.tasks:
            if task['status'] == "open":
                successful_last_idx = task['index']
                break
        return successful_last_idx
    
    def get_current_task(self):
        current_task = None
        for task in self.tasks:
            if task['status'] == "open":
                current_task = task['task']
                break
        return current_task
    
    def get_current_task_with_id(self):
        current_task = {"task": None, "index": None, "status": None}
        for task in self.tasks:
            if task['status'] == "open":
                current_task['task'] = task['task']
                current_task['index'] = task['index']
                current_task['status'] = task['status']
                break
        return f"Task Number ({current_task['index']}): {current_task['task']}  (Status: {current_task['status']})"
    
    def get_current_task_id(self):
        for task in self.tasks:
            if task['status'] == "open":
                return task['index']
                break  
    
    def check_termination(self):
        terminate = True
        for task in self.tasks:
            if task['status'] == "open":
                return False
        
        return terminate

# sales_query = '''WITH product_sales AS ( SELECT \"item_productId\", SUM(CAST(\"item_quantity\" AS INTEGER)) AS total_units_sold FROM sales_history GROUP BY \"item_productId\" HAVING total_units_sold > 200) SELECT p.\"title\", p.\"sku\", ps.total_units_sold FROM product p JOIN product_sales ps ON p.\"productId\" = ps.\"item_productId\" LIMIT 10''' 
# products_over_200_sales = fetch_postgres_data(sales_query) 
# products_over_200_sales_count = len(products_over_200_sales) 
# if products_over_200_sales_count <= 10 else products_over_200_sales.to_csv('products_over_200_sales.csv', index=False) products_over_200_sales if products_over_200_sales_count <= 10 else 'More than 10 items'",


query = '''\nSELECT DATE_TRUNC('month', \"creationDate\") AS sales_month, \n \"item_productId\", \n SUM(\"item_price\" * CAST(\"item_quantity\" AS INTEGER)) AS total_revenue \nFROM sales_history \nGROUP BY sales_month, \"item_productId\" \nORDER BY sales_month, \"item_productId\" \n'''
# sales_aggregation = fetch_postgres_data(query)
# join_query = '''\nSELECT sa.sales_month, \n sa.\"item_productId\", \n sa.total_revenue, \n p.title, \n p.visionCategoryName \nFROM sales_aggregation sa \nJOIN product p ON sa.\"item_productId\" = p.\"productId\" \n'''\
# sales_report_with_catalog = fetch_postgres_data(join_query)
# if len(sales_report_with_catalog) <= 10:
#  print(sales_report_with_catalog)
# else:
#     print(sales_report_with_catalog.head(10))
# sales_report_with_catalog.to_csv('monthly_sales_with_catalog_report.csv', index=False)"