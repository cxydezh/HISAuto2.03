import re
# 行为组树相关方法
def parse_group_rank(rank: str) -> dict:
    """解析GroupRank字符串，返回分层级字典"""
    result = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
    if not rank:
        return result
    matches = re.findall(r'([ABCDE])(\d+)', rank)
    for k, v in matches:
        result[k] = int(v)
    return result

def iid_to_group_rank(iid: str) -> str:
    """根据树节点iid复原标准group_rank字符串"""
    result = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
    matches = re.findall(r'([ABCDE])(\d+)', iid)
    for k, v in matches:
        result[k] = int(v)
    return f"A{result['A']}B{result['B']}C{result['C']}D{result['D']}E{result['E']}"
