--1.How much total revnue have we generated
select sum(order_amount) as total_revenue from fact_sales;

--2.How does revenue change month by month
select order_year,order_month,sum(order_amount) as monthly_revenue
from fact_sales
group by order_year , order_month
order by order_year , order_month;

--3.What are our most valuable customers
SELECT 
c.customer_name,
sum(f.order_amount) as total_spent
from fact_sales f
join dim_customers c
on f.customer_id = c.customer_id
GROUP BY c.customer_name
order by total_spent desc;

--4. which product generate the most revenue
SELECT
p.product_name,
sum(f.order_amount) as total_revenue
from fact_sales f
join dim_products p
on f.product_id = p.product_id
GROUP BY product_name
order by total_revenue desc;

--5.Which product in category performed best

select 
p.category,
sum(f.order_amount) as category_revenue
from fact_sales f
join dim_products p
on f.product_id = p.product_id
group by category
order by category_revenue desc;

--6. How much revenue does each customer generate over time
select
c.customer_name ,
count(f.order_id) as total_orders, sum(f.order_amount) as lifetime_value
from fact_sales as f
join dim_customers c
on f.customer_id = c.customer_id
group by c.customer_name
order by lifetime_value desc;

--7.Average value of an order
SELECT
avg(order_amount) as average_order_value
from fact_sales;