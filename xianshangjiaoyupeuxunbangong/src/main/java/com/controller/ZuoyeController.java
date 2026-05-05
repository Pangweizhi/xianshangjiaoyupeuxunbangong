package com.controller;

import com.alibaba.fastjson.JSONObject;
import com.annotation.IgnoreAuth;
import com.baomidou.mybatisplus.mapper.EntityWrapper;
import com.baomidou.mybatisplus.mapper.Wrapper;
import com.entity.ExamQuestionEntity;
import com.entity.ZuoyeEntity;
import com.entity.view.ZuoyeView;
import com.service.DictionaryService;
import com.service.ExamQuestionService;
import com.service.JiaoshiService;
import com.service.TokenService;
import com.service.YonghuService;
import com.service.ZuoyeService;
import com.utils.CommonUtil;
import com.utils.PageUtils;
import com.utils.PoiUtil;
import com.utils.R;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletRequest;
import java.io.File;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.*;

/**
 * 作业
 */
@RestController
@Controller
@RequestMapping("/zuoye")
public class ZuoyeController {
    private static final Logger logger = LoggerFactory.getLogger(ZuoyeController.class);

    @Autowired
    private ZuoyeService zuoyeService;
    @Autowired
    private TokenService tokenService;
    @Autowired
    private DictionaryService dictionaryService;
    @Autowired
    private YonghuService yonghuService;
    @Autowired
    private JiaoshiService jiaoshiService;
    @Autowired
    private ExamQuestionService examQuestionService;

    private ZuoyeView loadZuoyeViewById(Long id, HttpServletRequest request, boolean onlyPublished) {
        Map<String, Object> params = new HashMap<String, Object>();
        params.put("page", 1);
        params.put("limit", 1);
        params.put("sort", "id");
        params.put("order", "desc");
        params.put("ids", Collections.singletonList(id));
        params.put("zuoyeDeleteStart", 1);
        params.put("zuoyeDeleteEnd", 1);
        if (onlyPublished) {
            params.put("publishStatus", "published");
        }
        CommonUtil.checkMap(params);
        PageUtils page = zuoyeService.queryPage(params);
        List<ZuoyeView> list = (List<ZuoyeView>) page.getList();
        if (list == null || list.isEmpty()) {
            return null;
        }
        ZuoyeView view = list.get(0);
        dictionaryService.dictionaryConvert(view, request);
        return view;
    }

    @RequestMapping("/page")
    public R page(@RequestParam Map<String, Object> params, HttpServletRequest request) {
        logger.debug("page: {}", JSONObject.toJSONString(params));
        String role = String.valueOf(request.getSession().getAttribute("role"));
        if ("学生".equals(role)) {
            params.put("yonghuId", request.getSession().getAttribute("userId"));
        } else if ("教师".equals(role)) {
            params.put("jiaoshiId", request.getSession().getAttribute("userId"));
        }
        params.put("zuoyeDeleteStart", 1);
        params.put("zuoyeDeleteEnd", 1);
        CommonUtil.checkMap(params);
        PageUtils page = zuoyeService.queryPage(params);
        List<ZuoyeView> list = (List<ZuoyeView>) page.getList();
        for (ZuoyeView item : list) {
            dictionaryService.dictionaryConvert(item, request);
        }
        return R.ok().put("data", page);
    }

    @RequestMapping("/info/{id}")
    public R info(@PathVariable("id") Long id, HttpServletRequest request) {
        ZuoyeView view = loadZuoyeViewById(id, request, false);
        return view == null ? R.error(511, "查询不到数据") : R.ok().put("data", view);
    }

    @RequestMapping("/save")
    public R save(@RequestBody ZuoyeEntity zuoye, HttpServletRequest request) {
        String role = String.valueOf(request.getSession().getAttribute("role"));
        if ("教师".equals(role)) {
            zuoye.setJiaoshiId(Integer.valueOf(String.valueOf(request.getSession().getAttribute("userId"))));
        }
        sanitizeHomework(zuoye);

        Wrapper<ZuoyeEntity> queryWrapper = new EntityWrapper<ZuoyeEntity>()
            .eq("zuoye_name", zuoye.getZuoyeName())
            .eq("zuoye_types", zuoye.getZuoyeTypes())
            .eq("jiaoshi_id", zuoye.getJiaoshiId())
            .eq("zuoye_delete", 1);
        ZuoyeEntity exists = zuoyeService.selectOne(queryWrapper);
        if (exists != null) {
            return R.error(511, "表中有相同数据");
        }

        if (zuoye.getPublishStatus() == null || "".equals(zuoye.getPublishStatus().trim())) {
            zuoye.setPublishStatus("draft");
        }
        if (zuoye.getScoreTotal() == null || zuoye.getScoreTotal() <= 0) {
            zuoye.setScoreTotal(100);
        }
        zuoye.setZuoyeDelete(1);
        zuoye.setInsertTime(new Date());
        zuoye.setCreateTime(new Date());
        zuoyeService.insert(zuoye);
        return R.ok().put("data", zuoye);
    }

    @RequestMapping("/update")
    public R update(@RequestBody ZuoyeEntity zuoye, HttpServletRequest request) {
        ZuoyeEntity old = zuoyeService.selectById(zuoye.getId());
        if (old == null) {
            return R.error(511, "作业不存在");
        }
        sanitizeHomework(zuoye);

        String role = String.valueOf(request.getSession().getAttribute("role"));
        if ("教师".equals(role) && zuoye.getJiaoshiId() == null) {
            zuoye.setJiaoshiId(Integer.valueOf(String.valueOf(request.getSession().getAttribute("userId"))));
        }

        Wrapper<ZuoyeEntity> queryWrapper = new EntityWrapper<ZuoyeEntity>()
            .notIn("id", zuoye.getId())
            .eq("zuoye_name", zuoye.getZuoyeName())
            .eq("zuoye_types", zuoye.getZuoyeTypes())
            .eq("jiaoshi_id", zuoye.getJiaoshiId())
            .eq("zuoye_delete", 1);
        ZuoyeEntity exists = zuoyeService.selectOne(queryWrapper);
        if (exists != null) {
            return R.error(511, "表中有相同数据");
        }
        if (zuoye.getZuoyeDelete() == null) {
            zuoye.setZuoyeDelete(old.getZuoyeDelete() == null ? 1 : old.getZuoyeDelete());
        }
        zuoyeService.updateById(zuoye);
        return R.ok();
    }

    @RequestMapping("/bindQuestions")
    public R bindQuestions(@RequestBody Map<String, Object> payload) {
        Integer zuoyeId = payload.get("zuoyeId") == null ? null : Integer.valueOf(String.valueOf(payload.get("zuoyeId")));
        if (zuoyeId == null || zuoyeId <= 0) {
            return R.error(511, "请选择作业");
        }
        ZuoyeEntity homework = zuoyeService.selectById(zuoyeId);
        if (homework == null || homework.getZuoyeDelete() == null || homework.getZuoyeDelete() != 1) {
            return R.error(511, "作业不存在");
        }

        List<Integer> questionIds = parseQuestionIdList(payload.get("questionIds"));
        List<Integer> validIds = new ArrayList<Integer>();
        int totalScore = 0;
        for (Integer questionId : questionIds) {
            ExamQuestionEntity question = examQuestionService.selectById(questionId);
            if (question == null || question.getIsDeleted() == null || question.getIsDeleted() != 1) {
                continue;
            }
            if (homework.getKechengId() != null && question.getKechengId() != null
                && !homework.getKechengId().equals(question.getKechengId())) {
                continue;
            }
            validIds.add(question.getId());
            totalScore += question.getQuestionScore() == null ? 0 : question.getQuestionScore();
        }
        homework.setQuestionIds(joinQuestionIds(validIds));
        homework.setScoreTotal(totalScore > 0 ? totalScore : 100);
        zuoyeService.updateById(homework);
        return R.ok();
    }

    @RequestMapping("/questionList/{id}")
    public R questionList(@PathVariable("id") Long id, HttpServletRequest request) {
        ZuoyeEntity homework = zuoyeService.selectById(id);
        if (homework == null || homework.getZuoyeDelete() == null || homework.getZuoyeDelete() != 1) {
            return R.error(511, "作业不存在");
        }
        if (!"published".equals(homework.getPublishStatus())) {
            String role = String.valueOf(request.getSession().getAttribute("role"));
            if (!"教师".equals(role)) {
                return R.error(511, "作业未发布");
            }
        }

        List<Integer> ids = parseQuestionIds(homework.getQuestionIds());
        List<ExamQuestionEntity> result = new ArrayList<ExamQuestionEntity>();
        for (Integer questionId : ids) {
            ExamQuestionEntity question = examQuestionService.selectById(questionId);
            if (question == null || question.getIsDeleted() == null || question.getIsDeleted() != 1) {
                continue;
            }
            ExamQuestionEntity item = new ExamQuestionEntity();
            item.setId(question.getId());
            item.setKechengId(question.getKechengId());
            item.setExamId(question.getExamId());
            item.setQuestionType(question.getQuestionType());
            item.setQuestionTitle(question.getQuestionTitle());
            item.setOptionJson(question.getOptionJson());
            item.setQuestionScore(question.getQuestionScore());
            item.setSortNo(question.getSortNo());
            String role = String.valueOf(request.getSession().getAttribute("role"));
            if ("教师".equals(role)) {
                item.setCorrectAnswer(question.getCorrectAnswer());
                item.setAnalysisText(question.getAnalysisText());
            }
            result.add(item);
        }
        return R.ok().put("data", result);
    }

    @RequestMapping("/delete")
    public R delete(@RequestBody Integer[] ids) {
        ArrayList<ZuoyeEntity> list = new ArrayList<ZuoyeEntity>();
        for (Integer id : ids) {
            ZuoyeEntity entity = new ZuoyeEntity();
            entity.setId(id);
            entity.setZuoyeDelete(2);
            list.add(entity);
        }
        if (!list.isEmpty()) {
            zuoyeService.updateBatchById(list);
        }
        return R.ok();
    }

    @RequestMapping("/batchInsert")
    public R batchInsert(String fileName, HttpServletRequest request) {
        Integer yonghuId = Integer.valueOf(String.valueOf(request.getSession().getAttribute("userId")));
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        try {
            List<ZuoyeEntity> zuoyeList = new ArrayList<ZuoyeEntity>();
            Date date = new Date();
            int lastIndexOf = fileName.lastIndexOf(".");
            if (lastIndexOf == -1) {
                return R.error(511, "该文件没有后缀");
            }
            String suffix = fileName.substring(lastIndexOf);
            if (!".xls".equals(suffix)) {
                return R.error(511, "只支持后缀为xls的excel文件");
            }
            URL resource = this.getClass().getClassLoader().getResource("static/upload/" + fileName);
            File file = new File(resource.getFile());
            if (!file.exists()) {
                return R.error(511, "找不到上传文件，请联系管理员");
            }
            List<List<String>> dataList = PoiUtil.poiImport(file.getPath());
            dataList.remove(0);
            for (List<String> data : dataList) {
                ZuoyeEntity entity = new ZuoyeEntity();
                entity.setInsertTime(date);
                entity.setCreateTime(date);
                entity.setZuoyeDelete(1);
                zuoyeList.add(entity);
            }
            zuoyeService.insertBatch(zuoyeList);
            return R.ok();
        } catch (Exception e) {
            e.printStackTrace();
            return R.error(511, "批量插入数据异常，请联系管理员");
        }
    }

    @IgnoreAuth
    @RequestMapping("/list")
    public R list(@RequestParam Map<String, Object> params, HttpServletRequest request) {
        CommonUtil.checkMap(params);
        params.put("publishStatus", "published");
        params.put("zuoyeDeleteStart", 1);
        params.put("zuoyeDeleteEnd", 1);
        PageUtils page = zuoyeService.queryPage(params);
        List<ZuoyeView> list = (List<ZuoyeView>) page.getList();
        for (ZuoyeView item : list) {
            dictionaryService.dictionaryConvert(item, request);
        }
        return R.ok().put("data", page);
    }

    @RequestMapping("/detail/{id}")
    public R detail(@PathVariable("id") Long id, HttpServletRequest request) {
        ZuoyeView view = loadZuoyeViewById(id, request, true);
        return view == null ? R.error(511, "查询不到数据") : R.ok().put("data", view);
    }

    @RequestMapping("/add")
    public R add(@RequestBody ZuoyeEntity zuoye, HttpServletRequest request) {
        return save(zuoye, request);
    }

    private void sanitizeHomework(ZuoyeEntity zuoye) {
        if (zuoye == null) {
            return;
        }
        if ("".equals(zuoye.getZuoyePhoto()) || "null".equals(zuoye.getZuoyePhoto())) {
            zuoye.setZuoyePhoto(null);
        }
        if ("".equals(zuoye.getZuoyeFile()) || "null".equals(zuoye.getZuoyeFile())) {
            zuoye.setZuoyeFile(null);
        }
        zuoye.setQuestionIds(joinQuestionIds(parseQuestionIds(zuoye.getQuestionIds())));
    }

    private List<Integer> parseQuestionIdList(Object rawIds) {
        List<Integer> result = new ArrayList<Integer>();
        if (rawIds instanceof List) {
            for (Object item : (List<?>) rawIds) {
                if (item == null || "".equals(String.valueOf(item).trim())) {
                    continue;
                }
                result.add(Integer.valueOf(String.valueOf(item)));
            }
        }
        return result;
    }

    private List<Integer> parseQuestionIds(String questionIds) {
        List<Integer> result = new ArrayList<Integer>();
        if (questionIds == null || "".equals(questionIds.trim())) {
            return result;
        }
        String[] parts = questionIds.split(",");
        for (String part : parts) {
            if (part == null || "".equals(part.trim())) {
                continue;
            }
            result.add(Integer.valueOf(part.trim()));
        }
        return result;
    }

    private String joinQuestionIds(List<Integer> questionIds) {
        StringBuilder builder = new StringBuilder();
        for (Integer id : questionIds) {
            if (id == null || id <= 0) {
                continue;
            }
            if (builder.length() > 0) {
                builder.append(",");
            }
            builder.append(id);
        }
        return builder.toString();
    }
}
