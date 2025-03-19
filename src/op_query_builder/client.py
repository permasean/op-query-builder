from query import Query
import overpy

class QueryClient:
    def __init__(self) -> None:
        self.api = overpy.Overpass()

    # method to get admin level
    
    def execute_query(self, query: Query) -> str:
        return ''
    
    def validate_query(self, query) -> bool:
        try:
            self.api.query(query)
            print("Query is syntactically valid.")
            return True
        except overpy.exception.OverpassSyntaxError as e:
            print(f"Syntax error: {e}")
            return False
        except Exception as e:
            print(f"Other error: {e}")
            return False