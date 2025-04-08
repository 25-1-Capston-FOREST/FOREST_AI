# database/item_queries.py

from .base import BaseDatabase

class ItemQueries(BaseDatabase):
    def get_items_data(self):
        """모든 아이템 정보를 가져오는 메서드"""
        query = """
        SELECT id, name, category, price, description
        FROM items
        """
        try:
            result = self.execute_query(query)
            return result if result else []
            
        except Exception as e:
            print(f"아이템 조회 중 오류 발생: {str(e)}")
            return []