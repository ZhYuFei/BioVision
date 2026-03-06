import cv2

def evaluate_clarity(image):
    """
    评估图像的清晰度，返回一个清晰度分数。
    分数越高表示图像越清晰。
    """
    # 将图像转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 使用拉普拉斯算子计算图像的二阶导数
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    
    # 计算拉普拉斯算子的方差作为清晰度分数
    clarity_score = laplacian.var()
    
    return clarity_score