import sqlparse
import pytest

class QueryComplexityAnalyzer:
    def __init__(self, query):
        self.query = query
        self.parsed = sqlparse.parse(query)[0]
        self.metrics = {}

    def count_unique_tables(self):
        table_keywords = ["FROM", "INTO", "UPDATE", "JOIN", "TABLE"]
        tables = set()
        for token in self.parsed.tokens:
            if token.value.upper() in table_keywords:
                next_token = self.parsed.token_next(self.parsed.token_index(token))[1]
                table_name = next_token.value.split()[0]
                tables.add(table_name)
        self.metrics["unique_tables"] = len(tables)

    def analyze(self):
        self.count_unique_tables()

test_cases = [
    ("""
    SELECT p.product_id, p.product_name
    FROM products p
    WHERE p.product_expiry BETWEEN '2018-01-01' AND '2020-12-31';
    """, 1),
    ("""
    SELECT p.product_id, p.product_name, SUM(ol.quantity) AS total_quantity
    FROM products p
    JOIN order_lines ol ON p.product_id = ol.product_id
    JOIN orders o ON ol.order_id = o.order_id
    WHERE o.order_date BETWEEN '2020-04-01' AND '2020-06-30'
    GROUP BY p.product_id, p.product_name
    HAVING SUM(ol.quantity) > 100
    ORDER BY total_quantity DESC;
    """, 3),
    ("""
    WITH sales_regions AS 
      (SELECT region_id, SUM(sales_amount) AS total_sales
       FROM sales
       GROUP BY region_id)
    SELECT r.region_name, sr.total_sales
    FROM sales_regions sr
    JOIN regions r ON sr.region_id = r.region_id
    WHERE sr.total_sales > (SELECT AVG(total_sales) FROM sales_regions)
    ORDER BY total_sales DESC;
    """, 2),
    ("""
    INSERT INTO products (product_id, product_name)
    VALUES (1, 'Product 1');
    """, 1),
    ("""
    UPDATE products
    SET product_name = 'New Product Name'
    WHERE product_id = 1;
    """, 1),
    ("""
    DELETE FROM products
    WHERE product_id = 1;
    """, 1),
    ("""
    CREATE TABLE new_table (
        column1 INT,
        column2 VARCHAR(255)
    );
    """, 1)
]

@pytest.mark.parametrize("query, expected_unique_tables", test_cases)
def test_query_complexity_analyzer(query, expected_unique_tables):
    analyzer = QueryComplexityAnalyzer(query)
    analyzer.analyze()
    assert analyzer.metrics["unique_tables"] == expected_unique_tables

if __name__ == "__main__":
    test_query_complexity_analyzer()