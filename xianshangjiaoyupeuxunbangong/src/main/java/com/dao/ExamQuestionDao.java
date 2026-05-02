package com.dao;

import com.baomidou.mybatisplus.mapper.BaseMapper;
import com.baomidou.mybatisplus.plugins.pagination.Pagination;
import com.entity.ExamQuestionEntity;
import com.entity.view.ExamQuestionView;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

public interface ExamQuestionDao extends BaseMapper<ExamQuestionEntity> {
    List<ExamQuestionView> selectListView(Pagination page, @Param("params") Map<String, Object> params);
}
