package com.dao;

import com.baomidou.mybatisplus.mapper.BaseMapper;
import com.baomidou.mybatisplus.plugins.pagination.Pagination;
import com.entity.ExamRecordEntity;
import com.entity.view.ExamRecordView;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

public interface ExamRecordDao extends BaseMapper<ExamRecordEntity> {
    List<ExamRecordView> selectListView(Pagination page, @Param("params") Map<String, Object> params);
}
