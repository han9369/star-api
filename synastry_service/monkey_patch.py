# 修补flatlib库以正确处理swisseph返回的嵌套元组
def monkey_patch_flatlib():
    """
    动态修补flatlib库以处理swisseph返回的嵌套元组问题
    """
    try:
        # 尝试导入flatlib的swe模块
        from flatlib.ephem import swe as flatlib_swe
        
        # 保存原始calc_ut函数
        original_calc_ut = flatlib_swe.swisseph.calc_ut
        
        # 创建包装函数来处理嵌套元组
        def safe_calc_ut(*args, **kwargs):
            result = original_calc_ut(*args, **kwargs)
            
            # 检查结果是否为元组
            if isinstance(result, tuple) and len(result) > 0:
                if isinstance(result[0], tuple):
                    # 仅返回第一个元组的第一个元素
                    return result[0][0]
                return result[0]
            return result
        
        # 用安全版本替换原始函数
        flatlib_swe.swisseph.calc_ut = safe_calc_ut
        
        # 检查结构并适当修补
        # 注意：flatlib的结构可能与预期不同，get函数可能不直接在swe模块中
        # 查看模块是否有getSweObj和sweObject函数
        if hasattr(flatlib_swe, 'getSweObj') and callable(flatlib_swe.getSweObj):
            original_getSweObj = flatlib_swe.getSweObj
            
            def safe_getSweObj(obj):
                # 安全包装getSweObj
                return original_getSweObj(obj)
            
            flatlib_swe.getSweObj = safe_getSweObj
        
        if hasattr(flatlib_swe, 'sweObject') and callable(flatlib_swe.sweObject):
            original_sweObject = flatlib_swe.sweObject
            
            def safe_sweObject(jd, obj):
                result = original_sweObject(jd, obj)
                # 处理嵌套元组
                if isinstance(result, tuple) and len(result) > 0:
                    if isinstance(result[0], tuple):
                        return result[0][0]
                    return result[0]
                return result
            
            flatlib_swe.sweObject = safe_sweObject
        
        if hasattr(flatlib_swe, 'sweObjectLon') and callable(flatlib_swe.sweObjectLon):
            original_sweObjectLon = flatlib_swe.sweObjectLon
            
            def safe_sweObjectLon(jd, obj):
                result = original_sweObjectLon(jd, obj)
                # 处理嵌套元组
                if isinstance(result, tuple) and len(result) > 0:
                    if isinstance(result[0], tuple):
                        return result[0][0]
                    return result[0]
                return result
            
            flatlib_swe.sweObjectLon = safe_sweObjectLon
        
        return True
    except Exception as e:
        print(f"修补flatlib库失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False 