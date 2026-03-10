import time
import configparser
from typing import Optional, Tuple, List
import numpy as np

class PeakFinder:
    def __init__(self, config: configparser.ConfigParser):
        """
        峰值查找器
        
        Args:
            config: 配置解析器
        """
        self.x_start = int(config.get('focus_controller', 'x_start', fallback=1))
        self.x_end = int(config.get('focus_controller', 'x_end', fallback=161))
        self.prior_range = tuple(map(int, config.get('focus_controller', 'prior_range', fallback='10, 70').split(',')))
        
        # 算法内部状态
        self.queried_points = {}  # 已查询的点 {x: y}
        self.query_count = 0
        self.start_time = None
        
        # 搜索状态
        self.search_complete = False
        self.peak_x = -1
        self.peak_y = float('-inf')
        
        # 算法参数
        self.phi = (np.sqrt(5) - 1) / 2  # 黄金分割比例 ≈ 0.618
        
    def request_next_x(self) -> int:
        """
        请求下一个需要查询的x值
        返回: 要查询的x坐标，如果搜索完成返回-1
        """
        if self.search_complete:
            return -1
        
        if self.start_time is None:
            self.start_time = time.time()
        
        # 如果没有先验知识，使用标准黄金分割
        if self.prior_range is None or self.query_count >= 5:
            return self._standard_golden_search()
        else:
            return self._prior_guided_search()
    
    def receive_y(self, x: int, y: float) -> None:
        """
        接收查询结果
        
        Args:
            x: 查询的x坐标
            y: 对应的y值
        """
        if x == -1 or self.search_complete:
            return
        
        # 记录查询结果
        self.queried_points[x] = y
        self.query_count += 1
        
        # 更新当前最大值
        if y > self.peak_y:
            self.peak_x = x
            self.peak_y = y
        
        # 检查搜索是否应该结束
        self._check_search_completion()
    
    def get_peak(self) -> Tuple[int, float]:
        """
        获取当前找到的峰值点
        
        Returns:
            (x, y): 峰值点的坐标和值，如果未找到返回(-1, -inf)
        """
        if self.peak_x == -1:
            return -1, float('-inf')
        return self.peak_x, self.peak_y
    
    def get_statistics(self) -> dict:
        """
        获取搜索统计信息
        
        Returns:
            dict: 包含查询次数、耗时、搜索状态等信息
        """
        elapsed = 0
        if self.start_time:
            elapsed = time.time() - self.start_time
        
        return {
            'query_count': self.query_count,
            'elapsed_time': elapsed,
            'searched_points': list(self.queried_points.keys()),
            'search_complete': self.search_complete,
            'current_peak': (self.peak_x, self.peak_y)
        }
    
    def _standard_golden_search(self) -> int:
        """标准黄金分割搜索"""
        if self.query_count == 0:
            # 第一次查询：第一个黄金分割点
            return int(self.x_start + (1 - self.phi) * (self.x_end - self.x_start))
        
        if self.query_count == 1:
            # 第二次查询：第二个黄金分割点
            return int(self.x_start + self.phi * (self.x_end - self.x_start))
        
        # 获取当前搜索边界
        left, right = self._get_current_search_interval()
        
        if right - left <= 3:
            # 区间足够小，进行线性搜索
            for x in range(left, right + 1):
                if x not in self.queried_points:
                    return x
            self.search_complete = True
            return -1
        
        # 黄金分割法选择下一个点
        known_points = [(x, y) for x, y in self.queried_points.items() 
                       if left <= x <= right]
        known_points.sort(key=lambda p: p[0])
        
        if len(known_points) < 2:
            # 如果区间内已知点少于2个，在中间查询
            return (left + right) // 2
        
        # 找到区间内最靠近黄金分割点的未查询点
        x1 = int(left + (1 - self.phi) * (right - left))
        x2 = int(left + self.phi * (right - left))
        
        # 优先查询未查询过的黄金分割点
        for x in [x1, x2]:
            if x not in self.queried_points and left <= x <= right:
                return x
        
        # 如果都查询过了，查询中间点
        mid = (left + right) // 2
        candidates = [mid, mid-1, mid+1, left, right]
        for x in candidates:
            if x not in self.queried_points and left <= x <= right:
                return x
        
        # 所有点都查询过了
        self.search_complete = True
        return -1
    
    def _prior_guided_search(self) -> int:
        """先验知识指导的搜索"""
        p_left, p_right = self.prior_range
        prior_width = p_right - p_left
        
        if self.query_count == 0:
            # 第一次查询：优先区域的中心
            return (p_left + p_right) // 2
        
        if self.query_count == 1:
            # 第二次查询：优先区域的左边界
            return p_left
        
        if self.query_count == 2:
            # 第三次查询：优先区域的右边界
            return p_right
        
        if self.query_count == 3:
            # 根据前三次结果决定搜索方向
            best_x = self.peak_x
            
            if best_x < p_left:  # 峰值可能在左边
                return max(self.x_start, p_left - prior_width // 2)
            elif best_x > p_right:  # 峰值可能在右边
                return min(self.x_end, p_right + prior_width // 2)
            else:  # 峰值在优先区域内
                # 在峰值附近对称采样
                offset = prior_width // 4
                x_candidates = [
                    best_x - offset,
                    best_x + offset,
                    best_x
                ]
                for x in x_candidates:
                    if (x not in self.queried_points and 
                        self.x_start <= x <= self.x_end):
                        return int(x)
        
        # 4次查询后，使用基于当前信息的搜索
        return self._adaptive_search()
    
    def _adaptive_search(self) -> int:
        """自适应搜索，基于已有信息选择下一个点"""
        if len(self.queried_points) < 3:
            # 信息不足，在未查询区域的中点查询
            unsearched = [x for x in range(self.x_start, self.x_end + 1) 
                         if x not in self.queried_points]
            if unsearched:
                return unsearched[len(unsearched) // 2]
            return -1
        
        # 找到当前搜索区间
        left, right = self._get_current_search_interval()
        
        if right - left <= 3:
            # 小区间线性搜索
            for x in range(left, right + 1):
                if x not in self.queried_points:
                    return x
            return -1
        
        # 计算梯度方向
        sorted_points = sorted([(x, y) for x, y in self.queried_points.items() 
                               if left <= x <= right])
        
        if len(sorted_points) >= 2:
            # 计算平均梯度
            gradients = []
            for i in range(len(sorted_points) - 1):
                x1, y1 = sorted_points[i]
                x2, y2 = sorted_points[i + 1]
                if x2 > x1:
                    gradients.append((y2 - y1) / (x2 - x1))
            
            if gradients:
                avg_gradient = np.mean(gradients)
                
                if avg_gradient > 0:
                    # 整体上升，向右搜索
                    search_x = min(right, self.peak_x + (right - left) // 4)
                else:
                    # 整体下降，向左搜索
                    search_x = max(left, self.peak_x - (right - left) // 4)
                
                # 找到最近的未查询点
                if search_x not in self.queried_points:
                    return search_x
                
                # 向两侧扩展搜索
                for offset in range(1, (right - left) // 2 + 1):
                    for dx in [offset, -offset]:
                        x = search_x + dx
                        if (x not in self.queried_points and 
                            left <= x <= right):
                            return x
        
        # 回退到黄金分割
        x1 = int(left + (1 - self.phi) * (right - left))
        x2 = int(left + self.phi * (right - left))
        
        for x in [x1, x2, (left + right) // 2]:
            if x not in self.queried_points and left <= x <= right:
                return x
        
        # 搜索任何未查询点
        for x in range(left, right + 1):
            if x not in self.queried_points:
                return x
        
        return -1
    
    def _get_current_search_interval(self) -> Tuple[int, int]:
        """根据已查询点确定当前搜索区间"""
        if len(self.queried_points) < 2:
            return self.x_start, self.x_end
        
        # 找到包含所有已查询点的最小区间
        queried_x = list(self.queried_points.keys())
        min_x, max_x = min(queried_x), max(queried_x)
        
        # 扩展区间边界
        left = max(self.x_start, min_x - 5)
        right = min(self.x_end, max_x + 5)
        
        return left, right
    
    def _check_search_completion(self) -> None:
        """检查搜索是否完成"""
        # 检查是否所有点都已查询
        all_searched = all(x in self.queried_points 
                          for x in range(self.x_start, self.x_end + 1))
        
        if all_searched:
            self.search_complete = True
            return
        
        # 检查是否满足停止条件
        if self.query_count >= 20:  # 最大查询次数限制
            self.search_complete = True
            return
        
        # 检查最近几次查询是否没有改进
        if len(self.queried_points) >= 5:
            recent_points = sorted(self.queried_points.items(), 
                                  key=lambda x: x[1], reverse=True)[:3]
            if all(abs(x - self.peak_x) <= 2 for x, _ in recent_points):
                # 最近几次查询都在峰值附近，认为已收敛
                self.search_complete = True


# 使用示例
if __name__ == "__main__":  
    import csv

    print("\n\n=== 示例: 完整使用流程 ===")

    config = configparser.ConfigParser()
    config.read('config/default.ini')


    
    # 创建峰值查找器，指定x范围和先验范围
    finder = PeakFinder(config=config)
    
    with open('./data/clarity_scores1.csv', mode='r', encoding='utf-8') as file:
        # 交互式查询
        while True:
            x = finder.request_next_x()
            if x == -1:
                print("搜索完成！")
                break
            
            print(f"请求查询点: x={x}")
            
            # 从CSV文件中获取对应的y值
            file.seek(0)  # 重置文件指针
            reader = csv.DictReader(file)
            for row in reader:
                if int(float(row['Zoom Level'])) == x:
                    y = float(row['Clarity Score'])
                    break

            finder.receive_y(x, y)
            print(f"接收结果: y={y:.2f}")
            
            stats = finder.get_statistics()
            print(f"当前进度: {stats['query_count']}次查询, 当前峰值: {stats['current_peak']}")
            print("-" * 40)
    
    final_peak = finder.get_peak()
    print(f"\n最终结果: 峰值在 x={final_peak[0]}, y={final_peak[1]:.2f}")