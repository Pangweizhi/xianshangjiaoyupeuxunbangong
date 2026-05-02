package com.service.impl;

import com.baomidou.mybatisplus.plugins.Page;
import com.baomidou.mybatisplus.service.impl.ServiceImpl;
import com.dao.CourseEnrollDao;
import com.entity.CourseEnrollEntity;
import com.entity.view.CourseEnrollView;
import com.service.CourseEnrollService;
import com.utils.PageUtils;
import com.utils.Query;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;

@Service("courseEnrollService")
@Transactional
public class CourseEnrollServiceImpl extends ServiceImpl<CourseEnrollDao, CourseEnrollEntity> implements CourseEnrollService {
    @Override
    public PageUtils queryPage(Map<String, Object> params) {
        Page<CourseEnrollView> page = new Query<CourseEnrollView>(params).getPage();
        page.setRecords(baseMapper.selectListView(page, params));
        return new PageUtils(page);
    }
}

