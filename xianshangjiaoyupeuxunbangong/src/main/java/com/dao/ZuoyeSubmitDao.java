package com.dao;

import com.baomidou.mybatisplus.mapper.BaseMapper;
import com.baomidou.mybatisplus.plugins.pagination.Pagination;
import com.entity.ZuoyeSubmitEntity;
import com.entity.view.ZuoyeSubmitView;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

/**
 * 作业提交 Dao 接口
 */
public interface ZuoyeSubmitDao extends BaseMapper<ZuoyeSubmitEntity> {

    List<ZuoyeSubmitView> selectListView(Pagination page, @Param("params") Map<String, Object> params);
}
