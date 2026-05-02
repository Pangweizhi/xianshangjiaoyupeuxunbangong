package com.service.impl;

import com.baomidou.mybatisplus.plugins.Page;
import com.baomidou.mybatisplus.service.impl.ServiceImpl;
import com.dao.ExamDao;
import com.entity.ExamEntity;
import com.entity.view.ExamView;
import com.service.ExamService;
import com.utils.PageUtils;
import com.utils.Query;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;

@Service("examService")
@Transactional
public class ExamServiceImpl extends ServiceImpl<ExamDao, ExamEntity> implements ExamService {
    @Override
    public PageUtils queryPage(Map<String, Object> params) {
        Page<ExamView> page = new Query<ExamView>(params).getPage();
        page.setRecords(baseMapper.selectListView(page, params));
        return new PageUtils(page);
    }
}
