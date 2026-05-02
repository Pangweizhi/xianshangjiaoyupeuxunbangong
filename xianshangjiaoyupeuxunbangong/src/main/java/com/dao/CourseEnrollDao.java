package com.dao;

import com.baomidou.mybatisplus.mapper.BaseMapper;
import com.baomidou.mybatisplus.plugins.pagination.Pagination;
import com.entity.CourseEnrollEntity;
import com.entity.view.CourseEnrollView;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

public interface CourseEnrollDao extends BaseMapper<CourseEnrollEntity> {
    List<CourseEnrollView> selectListView(Pagination page, @Param("params") Map<String, Object> params);
}

