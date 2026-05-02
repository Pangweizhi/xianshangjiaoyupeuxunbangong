package com.controller;

import com.alibaba.fastjson.JSONObject;
import com.annotation.IgnoreAuth;
import com.baomidou.mybatisplus.mapper.EntityWrapper;
import com.baomidou.mybatisplus.mapper.Wrapper;
import com.entity.ZuoyeSubmitEntity;
import com.entity.view.ZuoyeSubmitView;
import com.service.ZuoyeSubmitService;
import com.utils.CommonUtil;
import com.utils.PageUtils;
import com.utils.R;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletRequest;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.Map;

/**
 * 作业提交
 * 后端接口
 */
@RestController
@Controller
@RequestMapping("/zuoyeSubmit")
public class ZuoyeSubmitController {
    private static final Logger logger = LoggerFactory.getLogger(ZuoyeSubmitController.class);

    @Autowired
    private ZuoyeSubmitService zuoyeSubmitService;

    /**
     * 后端列表
     */
    @RequestMapping("/page")
    public R page(@RequestParam Map<String, Object> params, HttpServletRequest request) {
        logger.debug("page方法:,,Controller:{},,params:{}", this.getClass().getName(), JSONObject.toJSONString(params));
        String role = String.valueOf(request.getSession().getAttribute("role"));
        if ("学生".equals(role)) {
            params.put("yonghuId", request.getSession().getAttribute("userId"));
        } else if ("教师".equals(role)) {
            params.put("jiaoshiId", request.getSession().getAttribute("userId"));
        }
        params.put("submitDeleteStart", 1);
        params.put("submitDeleteEnd", 1);
        CommonUtil.checkMap(params);
        PageUtils page = zuoyeSubmitService.queryPage(params);
        return R.ok().put("data", page);
    }

    /**
     * 后端详情
     */
    @RequestMapping("/info/{id}")
    public R info(@PathVariable("id") Long id, HttpServletRequest request) {
        logger.debug("info方法:,,Controller:{},,id:{}", this.getClass().getName(), id);
        ZuoyeSubmitEntity zuoyeSubmit = zuoyeSubmitService.selectById(id);
        if (zuoyeSubmit != null) {
            ZuoyeSubmitView view = new ZuoyeSubmitView();
            BeanUtils.copyProperties(zuoyeSubmit, view);
            return R.ok().put("data", view);
        }
        return R.error(511, "查不到数据");
    }

    /**
     * 后端保存
     */
    @RequestMapping("/save")
    public R save(@RequestBody ZuoyeSubmitEntity zuoyeSubmit, HttpServletRequest request) {
        logger.debug("save方法:,,Controller:{},,zuoyeSubmit:{}", this.getClass().getName(), zuoyeSubmit.toString());
        String role = String.valueOf(request.getSession().getAttribute("role"));
        if ("学生".equals(role)) {
            zuoyeSubmit.setYonghuId(Integer.valueOf(String.valueOf(request.getSession().getAttribute("userId"))));
        }

        Wrapper<ZuoyeSubmitEntity> queryWrapper = new EntityWrapper<ZuoyeSubmitEntity>()
            .eq("zuoye_id", zuoyeSubmit.getZuoyeId())
            .eq("yonghu_id", zuoyeSubmit.getYonghuId())
            .eq("submit_file", zuoyeSubmit.getSubmitFile())
            .eq("submit_delete", 1);

        ZuoyeSubmitEntity entity = zuoyeSubmitService.selectOne(queryWrapper);
        if (entity == null) {
            zuoyeSubmit.setSubmitStatus("待批改");
            zuoyeSubmit.setSubmitScore(null);
            zuoyeSubmit.setSubmitRemark(null);
            zuoyeSubmit.setSubmitDelete(1);
            zuoyeSubmit.setCheckTime(null);
            zuoyeSubmit.setInsertTime(new Date());
            zuoyeSubmit.setCreateTime(new Date());
            zuoyeSubmitService.insert(zuoyeSubmit);
            return R.ok();
        }
        return R.error(511, "请勿重复提交相同附件");
    }

    /**
     * 后端修改
     */
    @RequestMapping("/update")
    public R update(@RequestBody ZuoyeSubmitEntity zuoyeSubmit, HttpServletRequest request) {
        logger.debug("update方法:,,Controller:{},,zuoyeSubmit:{}", this.getClass().getName(), zuoyeSubmit.toString());
        if ("".equals(zuoyeSubmit.getSubmitFile()) || "null".equals(zuoyeSubmit.getSubmitFile())) {
            zuoyeSubmit.setSubmitFile(null);
        }
        if (zuoyeSubmit.getSubmitStatus() == null || "".equals(zuoyeSubmit.getSubmitStatus().trim())) {
            zuoyeSubmit.setSubmitStatus("待批改");
        }
        if ("待批改".equals(zuoyeSubmit.getSubmitStatus())) {
            zuoyeSubmit.setSubmitScore(null);
            zuoyeSubmit.setCheckTime(null);
        } else {
            zuoyeSubmit.setCheckTime(new Date());
        }
        zuoyeSubmitService.updateById(zuoyeSubmit);
        return R.ok();
    }

    /**
     * 删除
     */
    @RequestMapping("/delete")
    public R delete(@RequestBody Integer[] ids, HttpServletRequest request) {
        logger.debug("delete:,,Controller:{},,ids:{}", this.getClass().getName(), Arrays.toString(ids));
        ArrayList<ZuoyeSubmitEntity> list = new ArrayList<>();
        for (Integer id : ids) {
            ZuoyeSubmitEntity entity = new ZuoyeSubmitEntity();
            entity.setId(id);
            entity.setSubmitDelete(2);
            list.add(entity);
        }
        if (list.size() > 0) {
            zuoyeSubmitService.updateBatchById(list);
        }
        return R.ok();
    }

    /**
     * 前端列表
     */
    @IgnoreAuth
    @RequestMapping("/list")
    public R list(@RequestParam Map<String, Object> params, HttpServletRequest request) {
        logger.debug("list方法:,,Controller:{},,params:{}", this.getClass().getName(), JSONObject.toJSONString(params));
        CommonUtil.checkMap(params);
        PageUtils page = zuoyeSubmitService.queryPage(params);
        return R.ok().put("data", page);
    }

    /**
     * 前端详情
     */
    @RequestMapping("/detail/{id}")
    public R detail(@PathVariable("id") Long id, HttpServletRequest request) {
        return info(id, request);
    }

    /**
     * 前端保存
     */
    @RequestMapping("/add")
    public R add(@RequestBody ZuoyeSubmitEntity zuoyeSubmit, HttpServletRequest request) {
        return save(zuoyeSubmit, request);
    }
}
