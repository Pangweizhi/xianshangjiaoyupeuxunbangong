package com.dao;

import com.baomidou.mybatisplus.mapper.BaseMapper;
import com.baomidou.mybatisplus.plugins.pagination.Pagination;
import com.entity.CourseCreditRecordEntity;
import com.entity.view.CourseCreditRecordView;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

public interface CourseCreditRecordDao extends BaseMapper<CourseCreditRecordEntity> {
    List<CourseCreditRecordView> selectListView(Pagination page, @Param("params") Map<String, Object> params);
}

