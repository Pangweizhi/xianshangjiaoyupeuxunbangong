package com.service.impl;

import com.baomidou.mybatisplus.plugins.Page;
import com.baomidou.mybatisplus.service.impl.ServiceImpl;
import com.dao.ZuoyeSubmitDao;
import com.entity.view.ZuoyeSubmitView;
import com.service.ZuoyeSubmitService;
import com.utils.PageUtils;
import com.utils.Query;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;

import com.entity.ZuoyeSubmitEntity;

/**
 * 作业提交 服务实现类
 */
@Service("zuoyeSubmitService")
@Transactional
public class ZuoyeSubmitServiceImpl extends ServiceImpl<ZuoyeSubmitDao, ZuoyeSubmitEntity> implements ZuoyeSubmitService {

    @Override
    public PageUtils queryPage(Map<String, Object> params) {
        Page<ZuoyeSubmitView> page = new Query<ZuoyeSubmitView>(params).getPage();
        page.setRecords(baseMapper.selectListView(page, params));
        return new PageUtils(page);
    }
}
