from imgAnalysis.imgClarityEvaluation import evaluate_clarity
from imgAnalysis.imgClarityEvaluation import roi_clarity_evaluation
import numpy as np

def test_evaluate_clarity():
    """测试图像清晰度评估函数"""
    # 创建一个简单的测试图像
    clarity_score = evaluate_clarity(np.full((300, 300, 3), (255,255,255), dtype=np.uint8))
    assert clarity_score == 0.0

def test_roi_clarity_evaluation():
    """测试ROI图像清晰度评估函数"""
    # 创建一个简单的测试图像
    clarity_score = roi_clarity_evaluation(np.full((300, 300, 3), (255,255,255), dtype=np.uint8),(10,10,100,100))
    assert clarity_score == 0.0