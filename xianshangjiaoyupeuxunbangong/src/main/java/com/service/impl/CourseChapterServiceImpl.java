package com.service.impl;

import com.baomidou.mybatisplus.plugins.Page;
import com.baomidou.mybatisplus.service.impl.ServiceImpl;
import com.dao.CourseChapterDao;
import com.entity.CourseChapterEntity;
import com.entity.view.CourseChapterView;
import com.service.CourseChapterService;
import com.utils.PageUtils;
import com.utils.Query;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;

@Service("courseChapterService")
@Transactional
public class CourseChapterServiceImpl extends ServiceImpl<CourseChapterDao, CourseChapterEntity> implements CourseChapterService {
    @Override
    public PageUtils queryPage(Map<String, Object> params) {
        Page<CourseChapterView> page = new Query<CourseChapterView>(params).getPage();
        page.setRecords(baseMapper.selectListView(page, params));
        return new PageUtils(page);
    }
}

