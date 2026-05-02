package com.service.impl;

import com.baomidou.mybatisplus.plugins.Page;
import com.baomidou.mybatisplus.service.impl.ServiceImpl;
import com.dao.CourseResourceDao;
import com.entity.CourseResourceEntity;
import com.entity.view.CourseResourceView;
import com.service.CourseResourceService;
import com.utils.PageUtils;
import com.utils.Query;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;

@Service("courseResourceService")
@Transactional
public class CourseResourceServiceImpl extends ServiceImpl<CourseResourceDao, CourseResourceEntity> implements CourseResourceService {
    @Override
    public PageUtils queryPage(Map<String, Object> params) {
        Page<CourseResourceView> page = new Query<CourseResourceView>(params).getPage();
        page.setRecords(baseMapper.selectListView(page, params));
        return new PageUtils(page);
    }
}

