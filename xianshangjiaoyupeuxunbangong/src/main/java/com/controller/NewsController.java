package com.controller;

import com.alibaba.fastjson.JSONObject;
import com.annotation.IgnoreAuth;
import com.baomidou.mybatisplus.mapper.EntityWrapper;
import com.baomidou.mybatisplus.mapper.Wrapper;
import com.entity.NewsEntity;
import com.entity.view.NewsView;
import com.service.DictionaryService;
import com.service.JiaoshiService;
import com.service.NewsService;
import com.service.TokenService;
import com.service.YonghuService;
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

@RestController
@Controller
@RequestMapping("/news")
public class NewsController {
    private static final Logger logger = LoggerFactory.getLogger(NewsController.class);

    @Autowired
    private NewsService newsService;
    @Autowired
    private TokenService tokenService;
    @Autowired
    private DictionaryService dictionaryService;
    @Autowired
    private YonghuService yonghuService;
    @Autowired
    private JiaoshiService jiaoshiService;

    @RequestMapping("/page")
    public R page(@RequestParam Map<String, Object> params, HttpServletRequest request) {
        logger.debug("page controller params: {}", JSONObject.toJSONString(params));
        String role = String.valueOf(request.getSession().getAttribute("role"));
        if ("student".equalsIgnoreCase(role) || "学生".equals(role)) {
            params.put("yonghuId", request.getSession().getAttribute("userId"));
        } else if ("teacher".equalsIgnoreCase(role) || "教师".equals(role)) {
            params.put("jiaoshiId", request.getSession().getAttribute("userId"));
        }
        CommonUtil.checkMap(params);
        PageUtils page = newsService.queryPage(params);
        List<NewsView> list = (List<NewsView>) page.getList();
        for (NewsView item : list) {
            dictionaryService.dictionaryConvert(item, request);
        }
        return R.ok().put("data", page);
    }

    @RequestMapping("/info/{id}")
    public R info(@PathVariable("id") Long id, HttpServletRequest request) {
        logger.debug("info controller id: {}", id);
        NewsEntity news = newsService.selectById(id);
        if (news == null) {
            return R.error(511, "record not found");
        }
        NewsView view = new NewsView();
        BeanUtils.copyProperties(news, view);
        dictionaryService.dictionaryConvert(view, request);
        return R.ok().put("data", view);
    }

    @RequestMapping("/save")
    public R save(@RequestBody NewsEntity news, HttpServletRequest request) {
        logger.debug("save controller news: {}", news);
        sanitizeNewsPayload(news);
        Wrapper<NewsEntity> queryWrapper = new EntityWrapper<NewsEntity>()
            .eq("news_name", news.getNewsName())
            .eq("news_types", news.getNewsTypes());
        NewsEntity newsEntity = newsService.selectOne(queryWrapper);
        if (newsEntity != null) {
            return R.error(511, "duplicate record");
        }
        news.setInsertTime(new Date());
        news.setCreateTime(new Date());
        newsService.insert(news);
        return R.ok();
    }

    @RequestMapping("/update")
    public R update(@RequestBody NewsEntity news, HttpServletRequest request) {
        logger.debug("update controller news: {}", news);
        if (news.getId() == null) {
            return R.error(511, "missing id");
        }

        NewsEntity oldNewsEntity = newsService.selectById(news.getId());
        if (oldNewsEntity == null) {
            return R.error(511, "record not found");
        }

        if (StringUtils.isBlank(news.getNewsName())) {
            news.setNewsName(oldNewsEntity.getNewsName());
        }
        if (news.getNewsTypes() == null) {
            news.setNewsTypes(oldNewsEntity.getNewsTypes());
        }
        if (StringUtils.isBlank(news.getNewsContent())) {
            news.setNewsContent(oldNewsEntity.getNewsContent());
        }
        if (StringUtils.isBlank(news.getNewsPhoto()) || "null".equals(news.getNewsPhoto())) {
            news.setNewsPhoto(oldNewsEntity.getNewsPhoto());
        }
        if (news.getInsertTime() == null) {
            news.setInsertTime(oldNewsEntity.getInsertTime());
        }
        if (news.getCreateTime() == null) {
            news.setCreateTime(oldNewsEntity.getCreateTime());
        }

        sanitizeNewsPayload(news);

        Wrapper<NewsEntity> queryWrapper = new EntityWrapper<NewsEntity>()
            .notIn("id", news.getId())
            .andNew()
            .eq("news_name", news.getNewsName())
            .eq("news_types", news.getNewsTypes());
        NewsEntity newsEntity = newsService.selectOne(queryWrapper);
        if (newsEntity != null) {
            return R.error(511, "duplicate record");
        }

        newsService.updateById(news);
        return R.ok();
    }

    @RequestMapping("/delete")
    public R delete(@RequestBody Integer[] ids, HttpServletRequest request) {
        logger.debug("delete controller ids: {}", Arrays.toString(ids));
        newsService.deleteBatchIds(Arrays.asList(ids));
        return R.ok();
    }

    @RequestMapping("/batchInsert")
    public R save(String fileName, HttpServletRequest request) {
        logger.debug("batchInsert controller fileName: {}", fileName);
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        try {
            List<NewsEntity> newsList = new ArrayList<>();
            Date date = new Date();
            int lastIndexOf = fileName.lastIndexOf(".");
            if (lastIndexOf == -1) {
                return R.error(511, "invalid file name");
            }
            String suffix = fileName.substring(lastIndexOf);
            if (!".xls".equals(suffix)) {
                return R.error(511, "only xls is supported");
            }
            URL resource = this.getClass().getClassLoader().getResource("static/upload/" + fileName);
            File file = new File(resource.getFile());
            if (!file.exists()) {
                return R.error(511, "uploaded file not found");
            }
            List<List<String>> dataList = PoiUtil.poiImport(file.getPath());
            dataList.remove(0);
            for (List<String> data : dataList) {
                NewsEntity newsEntity = new NewsEntity();
//              newsEntity.setNewsName(data.get(0));
//              newsEntity.setNewsTypes(Integer.valueOf(data.get(0)));
//              newsEntity.setNewsPhoto("");
//              newsEntity.setInsertTime(date);
//              newsEntity.setNewsContent("");
//              newsEntity.setCreateTime(date);
                newsList.add(newsEntity);
            }
            newsService.insertBatch(newsList);
            return R.ok();
        } catch (Exception e) {
            logger.error("batch insert news failed", e);
            return R.error(511, "batch insert failed");
        }
    }

    @IgnoreAuth
    @RequestMapping("/list")
    public R list(@RequestParam Map<String, Object> params, HttpServletRequest request) {
        logger.debug("list controller params: {}", JSONObject.toJSONString(params));
        CommonUtil.checkMap(params);
        PageUtils page = newsService.queryPage(params);
        List<NewsView> list = (List<NewsView>) page.getList();
        for (NewsView item : list) {
            dictionaryService.dictionaryConvert(item, request);
        }
        return R.ok().put("data", page);
    }

    @RequestMapping("/detail/{id}")
    public R detail(@PathVariable("id") Long id, HttpServletRequest request) {
        logger.debug("detail controller id: {}", id);
        NewsEntity news = newsService.selectById(id);
        if (news == null) {
            return R.error(511, "record not found");
        }
        NewsView view = new NewsView();
        BeanUtils.copyProperties(news, view);
        dictionaryService.dictionaryConvert(view, request);
        return R.ok().put("data", view);
    }

    @RequestMapping("/add")
    public R add(@RequestBody NewsEntity news, HttpServletRequest request) {
        logger.debug("add controller news: {}", news);
        sanitizeNewsPayload(news);
        Wrapper<NewsEntity> queryWrapper = new EntityWrapper<NewsEntity>()
            .eq("news_name", news.getNewsName())
            .eq("news_types", news.getNewsTypes());
        NewsEntity newsEntity = newsService.selectOne(queryWrapper);
        if (newsEntity != null) {
            return R.error(511, "duplicate record");
        }
        news.setInsertTime(new Date());
        news.setCreateTime(new Date());
        newsService.insert(news);
        return R.ok();
    }

    private void sanitizeNewsPayload(NewsEntity news) {
        if (news == null) {
            return;
        }
        news.setNewsName(stripUnsupportedMysqlUtf8(news.getNewsName()));
        news.setNewsContent(stripUnsupportedMysqlUtf8(news.getNewsContent()));
        news.setNewsPhoto(stripUnsupportedMysqlUtf8(news.getNewsPhoto()));
    }

    /**
     * Remove 4-byte Unicode code points that cannot be stored in MySQL utf8 columns.
     */
    private String stripUnsupportedMysqlUtf8(String value) {
        if (value == null || value.isEmpty()) {
            return value;
        }
        StringBuilder builder = new StringBuilder(value.length());
        for (int i = 0; i < value.length(); ) {
            int codePoint = value.codePointAt(i);
            if (codePoint <= 0xFFFF) {
                builder.append((char) codePoint);
            }
            i += Character.charCount(codePoint);
        }
        return builder.toString();
    }
}
