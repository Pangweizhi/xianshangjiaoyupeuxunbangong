package com.service.impl;

import com.baomidou.mybatisplus.plugins.Page;
import com.baomidou.mybatisplus.service.impl.ServiceImpl;
import com.dao.CourseCreditRecordDao;
import com.entity.CourseCreditRecordEntity;
import com.entity.view.CourseCreditRecordView;
import com.service.CourseCreditRecordService;
import com.utils.PageUtils;
import com.utils.Query;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;

@Service("courseCreditRecordService")
@Transactional
public class CourseCreditRecordServiceImpl extends ServiceImpl<CourseCreditRecordDao, CourseCreditRecordEntity> implements CourseCreditRecordService {
    @Override
    public PageUtils queryPage(Map<String, Object> params) {
        Page<CourseCreditRecordView> page = new Query<CourseCreditRecordView>(params).getPage();
        page.setRecords(baseMapper.selectListView(page, params));
        return new PageUtils(page);
    }
}

