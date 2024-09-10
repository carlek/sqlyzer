Lets use sqlparse to develop a query complexity analyzer.
One aspect of query complexity is number of unique tables involved.
There will be more metrics added, so make it flexible to grow the metrics.
Use SQLPARSE to a count that metric. Write the analyzer and a test driver test it on these queries
Have ASSERTIONS verify that the first query has 1 unique table, and the second query has 3
```sql
SELECT p.product_id, p.product_name
FROM products p
WHERE p.product_expiry BETWEEN '2018-01-01' AND '2020-12-31';

SELECT p.product_id, p.product_name, SUM(ol.quantity) AS total_quantity
FROM products p
JOIN order_lines ol ON p.product_id = ol.product_id
JOIN orders o ON ol.order_id = o.order_id
WHERE o.order_date BETWEEN '2020-04-01' AND '2020-06-30'
GROUP BY p.product_id, p.product_name
HAVING SUM(ol.quantity) > 100
ORDER BY total_quantity DESC;
```
