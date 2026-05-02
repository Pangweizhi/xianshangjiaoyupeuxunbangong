package com.service.impl;

import com.baomidou.mybatisplus.plugins.Page;
import com.baomidou.mybatisplus.service.impl.ServiceImpl;
import com.dao.ExamRecordDao;
import com.entity.ExamRecordEntity;
import com.entity.view.ExamRecordView;
import com.service.ExamRecordService;
import com.utils.PageUtils;
import com.utils.Query;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;

@Service("examRecordService")
@Transactional
public class ExamRecordServiceImpl extends ServiceImpl<ExamRecordDao, ExamRecordEntity> implements ExamRecordService {
    @Override
    public PageUtils queryPage(Map<String, Object> params) {
        Page<ExamRecordView> page = new Query<ExamRecordView>(params).getPage();
        page.setRecords(baseMapper.selectListView(page, params));
        return new PageUtils(page);
    }
}
