package com.dao;

import com.baomidou.mybatisplus.mapper.BaseMapper;
import com.baomidou.mybatisplus.plugins.pagination.Pagination;
import com.entity.CourseChapterEntity;
import com.entity.view.CourseChapterView;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

public interface CourseChapterDao extends BaseMapper<CourseChapterEntity> {
    List<CourseChapterView> selectListView(Pagination page, @Param("params") Map<String, Object> params);
}

