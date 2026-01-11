from flashtext import KeywordProcessor
from sqlalchemy.orm import Session
from database.management import NotallowedWordManagement

class not_allowed_word:
    @staticmethod
    def check_message(content,db:Session):
        not_allowed_word_management = NotallowedWordManagement(db)
        keyword_processor = KeywordProcessor()
        db_words = not_allowed_word_management.get_not_allowed_words_all()
        keyword_processor.add_keywords_from_list(db_words)
        found_words = keyword_processor.extract_keywords(content)
    
        if found_words:
            return found_words[0] 
        return None

# 测试
if __name__ == "__main__":
    msg = "我想去赌博赚钱"
    result = not_allowed_word.check_message(msg)
    if result:
        raise ValueError("对不起，存在违禁词！打回！")
