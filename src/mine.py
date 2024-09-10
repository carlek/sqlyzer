import sqlparse


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


def test_query_complexity_analyzer():
    query1 = """
    SELECT p.product_id, p.product_name
    FROM products p
    WHERE p.product_expiry BETWEEN '2018-01-01' AND '2020-12-31';
    """
    query2 = """
    SELECT p.product_id, p.product_name, SUM(ol.quantity) AS total_quantity
    FROM products p
    JOIN order_lines ol ON p.product_id = ol.product_id
    JOIN orders o ON ol.order_id = o.order_id
    WHERE o.order_date BETWEEN '2020-04-01' AND '2020-06-30'
    GROUP BY p.product_id, p.product_name
    HAVING SUM(ol.quantity) > 100
    ORDER BY total_quantity DESC;
    """

    analyzer1 = QueryComplexityAnalyzer(query1)
    analyzer1.analyze()
    assert analyzer1.metrics["unique_tables"] == 1

    analyzer2 = QueryComplexityAnalyzer(query2)
    analyzer2.analyze()
    assert analyzer2.metrics["unique_tables"] == 3


if __name__ == "__main__":
    test_query_complexity_analyzer()
