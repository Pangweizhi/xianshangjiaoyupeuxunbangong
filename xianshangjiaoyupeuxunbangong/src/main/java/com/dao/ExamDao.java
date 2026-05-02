package com.dao;

import com.baomidou.mybatisplus.mapper.BaseMapper;
import com.baomidou.mybatisplus.plugins.pagination.Pagination;
import com.entity.ExamEntity;
import com.entity.view.ExamView;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

public interface ExamDao extends BaseMapper<ExamEntity> {
    List<ExamView> selectListView(Pagination page, @Param("params") Map<String, Object> params);
}
