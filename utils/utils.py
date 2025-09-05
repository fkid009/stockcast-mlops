import yaml

from utils.path import SQL_DIR

def load_sql(fname: str) -> str:
    """
    sql 디렉토리 안의 파일을 읽어 문자열로 반환
    """
    
    return (SQL_DIR / fname).read_text(encoding = "utf-8")


def load_yaml(path) -> dict:
    with open(path, "r", encoding = "utf-8") as f:
        return yaml.safe_load(f)