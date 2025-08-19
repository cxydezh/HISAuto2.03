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

def group_rank_to_dict(group_rank: str) -> dict:
    """将group_rank转换为字典"""
    result = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
    matches = re.findall(r'([ABCDE])(\d+)', group_rank)
    for k, v in matches:
        result[k] = int(v)
    return result

def parse_list_rank_to_iid(list_rank):
        """将list_rank转换为iid格式"""
        if not list_rank:
            return None
        rank_dict = parse_group_rank(list_rank)
        group_rank_str = ""
        for key, value in rank_dict.items():
            if value > 0:
                group_rank_str += key + str(value)
        return group_rank_str
    
def parse_group_rank_to_iid(group_rank):
        """将group_rank转换为iid格式"""
        if not group_rank:
            return None
        rank_dict = parse_group_rank(group_rank)
        group_rank_str = ""
        for key, value in rank_dict.items():
            if value > 0:
                group_rank_str += key + str(value)
        return group_rank_str
    
def get_parent_iid(iid):
        """根据当前iid获取父节点iid"""
        if not iid:
            return None
        
        rank_dict = parse_group_rank(iid)
        
        # 根据层级确定父节点
        if rank_dict['E'] > 0:
            return f"A{rank_dict['A']}B{rank_dict['B']}C{rank_dict['C']}D{rank_dict['D']}"
        elif rank_dict['D'] > 0:
            return f"A{rank_dict['A']}B{rank_dict['B']}C{rank_dict['C']}"
        elif rank_dict['C'] > 0:
            return f"A{rank_dict['A']}B{rank_dict['B']}"
        elif rank_dict['B'] > 0:
            return f"A{rank_dict['A']}"
        else:
            return None  # A级节点没有父节点
    

