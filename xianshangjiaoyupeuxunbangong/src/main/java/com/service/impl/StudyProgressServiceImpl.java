package com.service.impl;

import com.baomidou.mybatisplus.plugins.Page;
import com.baomidou.mybatisplus.service.impl.ServiceImpl;
import com.dao.StudyProgressDao;
import com.entity.StudyProgressEntity;
import com.entity.view.StudyProgressView;
import com.service.StudyProgressService;
import com.utils.PageUtils;
import com.utils.Query;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;

@Service("studyProgressService")
@Transactional
public class StudyProgressServiceImpl extends ServiceImpl<StudyProgressDao, StudyProgressEntity> implements StudyProgressService {
    @Override
    public PageUtils queryPage(Map<String, Object> params) {
        Page<StudyProgressView> page = new Query<StudyProgressView>(params).getPage();
        page.setRecords(baseMapper.selectListView(page, params));
        return new PageUtils(page);
    }
}

