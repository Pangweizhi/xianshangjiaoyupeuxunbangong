package com.dao;

import com.baomidou.mybatisplus.mapper.BaseMapper;
import com.baomidou.mybatisplus.plugins.pagination.Pagination;
import com.entity.StudyProgressEntity;
import com.entity.view.StudyProgressView;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

public interface StudyProgressDao extends BaseMapper<StudyProgressEntity> {
    List<StudyProgressView> selectListView(Pagination page, @Param("params") Map<String, Object> params);
}

