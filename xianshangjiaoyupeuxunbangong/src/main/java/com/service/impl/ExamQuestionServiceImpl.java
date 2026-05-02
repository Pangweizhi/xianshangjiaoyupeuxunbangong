package com.service.impl;

import com.baomidou.mybatisplus.plugins.Page;
import com.baomidou.mybatisplus.service.impl.ServiceImpl;
import com.dao.ExamQuestionDao;
import com.entity.ExamQuestionEntity;
import com.entity.view.ExamQuestionView;
import com.service.ExamQuestionService;
import com.utils.PageUtils;
import com.utils.Query;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;

@Service("examQuestionService")
@Transactional
public class ExamQuestionServiceImpl extends ServiceImpl<ExamQuestionDao, ExamQuestionEntity> implements ExamQuestionService {
    @Override
    public PageUtils queryPage(Map<String, Object> params) {
        Page<ExamQuestionView> page = new Query<ExamQuestionView>(params).getPage();
        page.setRecords(baseMapper.selectListView(page, params));
        return new PageUtils(page);
    }
}
