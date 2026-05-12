package com.controller;

import com.alibaba.fastjson.JSONObject;
import com.annotation.IgnoreAuth;
import com.baomidou.mybatisplus.mapper.EntityWrapper;
import com.baomidou.mybatisplus.mapper.Wrapper;
import com.entity.KaihuitongzhiEntity;
import com.entity.view.KaihuitongzhiView;
import com.service.DictionaryService;
import com.service.KaihuitongzhiService;
import com.utils.CommonUtil;
import com.utils.PageUtils;
import com.utils.PoiUtil;
import com.utils.R;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import javax.servlet.http.HttpServletRequest;
import java.io.File;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.Map;

/**
 * 会议 后端接口
 */
@RestController
@Controller
@RequestMapping("/kaihuitongzhi")
public class KaihuitongzhiController {
    private static final Logger logger = LoggerFactory.getLogger(KaihuitongzhiController.class);

    @Autowired
    private KaihuitongzhiService kaihuitongzhiService;
    @Autowired
    private DictionaryService dictionaryService;

    @RequestMapping("/refreshPublishTime")
    public R refreshPublishTime(HttpServletRequest request) {
        String role = String.valueOf(request.getSession().getAttribute("role"));
        if (!"管理员".equals(role)) {
            return R.error(401, "无权限执行该操作");
        }

        List<KaihuitongzhiEntity> allMeetings = kaihuitongzhiService.selectList(new EntityWrapper<KaihuitongzhiEntity>());
        if (allMeetings == null || allMeetings.isEmpty()) {
            return R.ok().put("data", 0);
        }

        Date now = new Date();
        ArrayList<KaihuitongzhiEntity> list = new ArrayList<>();
        for (KaihuitongzhiEntity meeting : allMeetings) {
            KaihuitongzhiEntity update = new KaihuitongzhiEntity();
            update.setId(meeting.getId());
            update.setInsertTime(now);
            update.setCreateTime(now);
            list.add(update);
        }
        kaihuitongzhiService.updateBatchById(list);
        return R.ok().put("data", list.size());
    }

    @RequestMapping("/page")
    public R page(@RequestParam Map<String, Object> params, HttpServletRequest request) {
        logger.debug("page controller params: {}", JSONObject.toJSONString(params));
        CommonUtil.checkMap(params);
        PageUtils page = kaihuitongzhiService.queryPage(params);
        List<KaihuitongzhiView> list = (List<KaihuitongzhiView>) page.getList();
        for (KaihuitongzhiView item : list) {
            dictionaryService.dictionaryConvert(item, request);
        }
        return R.ok().put("data", page);
    }

    @IgnoreAuth
    @RequestMapping("/list")
    public R list(@RequestParam Map<String, Object> params, HttpServletRequest request) {
        logger.debug("list controller params: {}", JSONObject.toJSONString(params));
        CommonUtil.checkMap(params);
        PageUtils page = kaihuitongzhiService.queryPage(params);
        List<KaihuitongzhiView> list = (List<KaihuitongzhiView>) page.getList();
        for (KaihuitongzhiView item : list) {
            dictionaryService.dictionaryConvert(item, request);
        }
        return R.ok().put("data", page);
    }

    @RequestMapping("/info/{id}")
    public R info(@PathVariable("id") Long id, HttpServletRequest request) {
        logger.debug("info controller id: {}", id);
        KaihuitongzhiEntity meeting = kaihuitongzhiService.selectById(id);
        if (meeting == null) {
            return R.error(511, "record not found");
        }
        KaihuitongzhiView view = new KaihuitongzhiView();
        BeanUtils.copyProperties(meeting, view);
        dictionaryService.dictionaryConvert(view, request);
        return R.ok().put("data", view);
    }

    @IgnoreAuth
    @RequestMapping("/detail/{id}")
    public R detail(@PathVariable("id") Long id, HttpServletRequest request) {
        logger.debug("detail controller id: {}", id);
        KaihuitongzhiEntity meeting = kaihuitongzhiService.selectById(id);
        if (meeting == null) {
            return R.error(511, "record not found");
        }
        KaihuitongzhiView view = new KaihuitongzhiView();
        BeanUtils.copyProperties(meeting, view);
        dictionaryService.dictionaryConvert(view, request);
        return R.ok().put("data", view);
    }

    @RequestMapping("/save")
    public R save(@RequestBody KaihuitongzhiEntity kaihuitongzhi, HttpServletRequest request) {
        logger.debug("save controller meeting: {}", kaihuitongzhi);
        sanitizeMeetingPayload(kaihuitongzhi);
        Wrapper<KaihuitongzhiEntity> queryWrapper = new EntityWrapper<KaihuitongzhiEntity>()
            .eq("kaihuitongzhi_name", kaihuitongzhi.getKaihuitongzhiName())
            .eq("kaihuitongzhi_types", kaihuitongzhi.getKaihuitongzhiTypes());
        KaihuitongzhiEntity exists = kaihuitongzhiService.selectOne(queryWrapper);
        if (exists != null) {
            return R.error(511, "duplicate record");
        }
        kaihuitongzhi.setInsertTime(new Date());
        kaihuitongzhi.setCreateTime(new Date());
        kaihuitongzhiService.insert(kaihuitongzhi);
        return R.ok();
    }

    @RequestMapping("/add")
    public R add(@RequestBody KaihuitongzhiEntity kaihuitongzhi, HttpServletRequest request) {
        return save(kaihuitongzhi, request);
    }

    @RequestMapping("/update")
    public R update(@RequestBody KaihuitongzhiEntity kaihuitongzhi, HttpServletRequest request) {
        logger.debug("update controller meeting: {}", kaihuitongzhi);
        if (kaihuitongzhi.getId() == null) {
            return R.error(511, "missing id");
        }
        KaihuitongzhiEntity old = kaihuitongzhiService.selectById(kaihuitongzhi.getId());
        if (old == null) {
            return R.error(511, "record not found");
        }
        if (StringUtils.isBlank(kaihuitongzhi.getKaihuitongzhiName())) {
            kaihuitongzhi.setKaihuitongzhiName(old.getKaihuitongzhiName());
        }
        if (kaihuitongzhi.getKaihuitongzhiTypes() == null) {
            kaihuitongzhi.setKaihuitongzhiTypes(old.getKaihuitongzhiTypes());
        }
        if (StringUtils.isBlank(kaihuitongzhi.getKaihuitongzhiContent())) {
            kaihuitongzhi.setKaihuitongzhiContent(old.getKaihuitongzhiContent());
        }
        if (kaihuitongzhi.getInsertTime() == null) {
            kaihuitongzhi.setInsertTime(old.getInsertTime());
        }
        if (kaihuitongzhi.getCreateTime() == null) {
            kaihuitongzhi.setCreateTime(old.getCreateTime());
        }

        sanitizeMeetingPayload(kaihuitongzhi);

        Wrapper<KaihuitongzhiEntity> queryWrapper = new EntityWrapper<KaihuitongzhiEntity>()
            .notIn("id", kaihuitongzhi.getId())
            .andNew()
            .eq("kaihuitongzhi_name", kaihuitongzhi.getKaihuitongzhiName())
            .eq("kaihuitongzhi_types", kaihuitongzhi.getKaihuitongzhiTypes());
        KaihuitongzhiEntity exists = kaihuitongzhiService.selectOne(queryWrapper);
        if (exists != null) {
            return R.error(511, "duplicate record");
        }
        kaihuitongzhiService.updateById(kaihuitongzhi);
        return R.ok();
    }

    @RequestMapping("/delete")
    public R delete(@RequestBody Integer[] ids, HttpServletRequest request) {
        logger.debug("delete controller ids: {}", Arrays.toString(ids));
        kaihuitongzhiService.deleteBatchIds(Arrays.asList(ids));
        return R.ok();
    }

    @RequestMapping("/batchInsert")
    public R batchInsert(String fileName, HttpServletRequest request) {
        logger.debug("batchInsert controller fileName: {}", fileName);
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        try {
            List<KaihuitongzhiEntity> list = new ArrayList<>();
            int lastIndexOf = fileName.lastIndexOf(".");
            if (lastIndexOf == -1) {
                return R.error(511, "invalid file name");
            }
            String suffix = fileName.substring(lastIndexOf);
            if (!".xls".equals(suffix)) {
                return R.error(511, "only xls is supported");
            }
            URL resource = this.getClass().getClassLoader().getResource("static/upload/" + fileName);
            if (resource == null) {
                return R.error(511, "uploaded file not found");
            }
            File file = new File(resource.getFile());
            if (!file.exists()) {
                return R.error(511, "uploaded file not found");
            }
            List<List<String>> dataList = PoiUtil.poiImport(file.getPath());
            if (!dataList.isEmpty()) {
                dataList.remove(0);
            }
            Date date = new Date();
            for (List<String> row : dataList) {
                KaihuitongzhiEntity meeting = new KaihuitongzhiEntity();
                if (row.size() > 0) {
                    meeting.setKaihuitongzhiName(row.get(0));
                }
                if (row.size() > 1 && StringUtils.isNotBlank(row.get(1))) {
                    try {
                        meeting.setKaihuitongzhiTypes(Integer.valueOf(row.get(1)));
                    } catch (NumberFormatException ignore) {
                        meeting.setKaihuitongzhiTypes(null);
                    }
                }
                if (row.size() > 2) {
                    meeting.setKaihuitongzhiContent(row.get(2));
                }
                sanitizeMeetingPayload(meeting);
                meeting.setInsertTime(date);
                meeting.setCreateTime(date);
                list.add(meeting);
            }
            kaihuitongzhiService.insertBatch(list);
            return R.ok();
        } catch (Exception e) {
            logger.error("batch insert meeting failed", e);
            return R.error(511, "batch insert failed");
        }
    }

    private void sanitizeMeetingPayload(KaihuitongzhiEntity meeting) {
        if (meeting == null) {
            return;
        }
        meeting.setKaihuitongzhiName(stripUnsupportedMysqlUtf8(meeting.getKaihuitongzhiName()));
        meeting.setKaihuitongzhiContent(stripUnsupportedMysqlUtf8(meeting.getKaihuitongzhiContent()));
    }

    private String stripUnsupportedMysqlUtf8(String value) {
        if (value == null || value.isEmpty()) {
            return value;
        }
        StringBuilder builder = new StringBuilder(value.length());
        for (int i = 0; i < value.length(); ) {
            int codePoint = value.codePointAt(i);
            if (codePoint <= 0xFFFF) {
                builder.appendCodePoint(codePoint);
            }
            i += Character.charCount(codePoint);
        }
        return builder.toString();
    }
}
