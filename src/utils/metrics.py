import sqlparse
from sqlparse.sql import Parenthesis, Statement, Identifier
from sqlparse.tokens import DML, Keyword, Whitespace

def subquery_tables(query: str) -> tuple[int, list[str]]:
    """
    Count the number of subqueries and extract the table names from these subqueries.

    Parameters:
    query (str): The SQL query to analyze.

    Returns:
    tuple[int, list[str]]: The count of subqueries and a list of table names extracted from these subqueries.
    """
    subquery_count: int = 0
    subquery_table_list: list[str] = []

    def extract_table_name(tokens):
        table_name = None
        for i, token in enumerate(tokens):
            # syntax is 'FROM' [<Whitespace>]*  <Table Name>  
            if token.ttype is Keyword and token.value.upper() == 'FROM':
                j = i + 1
                while j < len(tokens) and tokens[j].ttype is Whitespace:
                    j += 1
                # ensure next token is Identifier
                if j < len(tokens) and isinstance(tokens[j], Identifier):
                    table_name = tokens[j].get_real_name()
                    break
        return table_name

    # recursively traverse tokens to find subqueries
    def extract_subqueries(tokens):
        nonlocal subquery_count 
        nonlocal subquery_table_list
        for token in tokens:
            # Parenthesis with a SELECT statement => subquery
            if isinstance(token, Parenthesis):
                if any(t.ttype is DML and t.value.upper() == 'SELECT' for t in token.tokens):
                    subquery_count += 1
                    subquery_table_list.append(extract_table_name(token.tokens))
                    extract_subqueries(token.tokens)
            # Recursively check within token if children
            elif hasattr(token, 'tokens'):
                extract_subqueries(token.tokens)

    parsed = sqlparse.parse(query)[0]
    extract_subqueries(parsed.tokens)
    return subquery_count, subquery_table_list

def unique_tables(query: str) -> tuple[int, list[str]]:
    """
    Extract unique table names from an SQL query.

    Parameters:
    query (str): The SQL query to analyze.

    Returns:
    tuple[int, list[str]]: A count of unique tables and a list of unique table names.
    """
    table_keywords = ["FROM", "INTO", "UPDATE", "JOIN", "TABLE"]
    tables = set()
    parsed = sqlparse.parse(query)[0]
    for token in parsed.tokens:
        if token.value.upper() in table_keywords:
            next_token = parsed.token_next(parsed.token_index(token))[1]
            table_name = next_token.value.split()[0]
            tables.add(table_name)
    return (len(tables), tables)


def redundant_joins(query: str) -> list[str]:
    """
    Extract redundant joins in an SQL query.

    A redundant JOIN is defined as joining the same table multiple times,
    where at least one of the joins doesn't contribute to the final result set
    (i.e., its columns are not selected or used in WHERE clauses).

    Args:
            query (str): The SQL query to analyze.

    Returns:
            list[str]: List of aliases and table names involved in redundant joins. [] if none.
    """
    parsed_query = sqlparse.parse(query)[0]  # Assuming single-query input
    joins = [statement for statement in parsed_query.tokens if statement.value == "JOIN"]
    join_aliases = set()
    join_tables = {}
    for join in joins:
        table_name, table_alias = parsed_query.token_next(parsed_query.token_index(join))[1].value.split()
        join_aliases.add(table_alias)
        if table_name not in join_tables:
            join_tables[table_name] = [table_alias]
        else:
            join_tables[table_name].append(table_alias)

    # Check for tables with multiple joins
    used_aliases = set()
    for table_name, aliases in join_tables.items():
        if len(aliases) > 1:
            # Check if all joins contribute to the final output
            # Check SELECT clause
            select = [
                statement
                for statement in parsed_query.tokens
                if statement.value == "SELECT"
            ]
            columns = parsed_query.token_next(parsed_query.token_index(select[0]))[1].value.split()
            for c in [column.split(".")[0] for column in columns if "." in column]:
                used_aliases.add(c)

            # Check WHERE clause (if exists)
            where = [
                statement
                for statement in parsed_query.tokens
                if statement.value == "WHERE"
            ]
            if where:
                columns = parsed_query.token_next(parsed_query.token_index(where[0]))[1].value.split()
                for c in [column.split(".")[0] for column in columns if "." in column]:
                    used_aliases.add(c)

    # Find aliases that aren't used
    redundant_aliases = join_aliases - used_aliases
    # Return tables involved in redundant joins
    return [f"{alias}.{table}" for table, aliases in join_tables.items() for alias in aliases if alias in redundant_aliases]