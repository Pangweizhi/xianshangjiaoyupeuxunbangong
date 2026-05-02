
package com.controller;

import java.io.File;
import java.net.URL;
import java.text.SimpleDateFormat;
import com.alibaba.fastjson.JSONObject;
import java.util.*;
import javax.servlet.http.HttpServletRequest;

import com.service.TokenService;
import com.utils.*;
import com.service.DictionaryService;
import com.annotation.IgnoreAuth;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import com.baomidou.mybatisplus.mapper.EntityWrapper;
import com.baomidou.mybatisplus.mapper.Wrapper;
import com.entity.*;
import com.entity.view.*;
import com.service.*;
import com.utils.PageUtils;
import com.utils.R;
import com.alibaba.fastjson.*;

/**
 * 作业
 * 后端接口
 */
@RestController
@Controller
@RequestMapping("/zuoye")
public class ZuoyeController {
    private static final Logger logger = LoggerFactory.getLogger(ZuoyeController.class);

    private static final String TABLE_NAME = "zuoye";

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

    private ZuoyeView loadZuoyeViewById(Long id, HttpServletRequest request, boolean onlyPublished){
        Map<String, Object> params = new HashMap<>();
        params.put("page", 1);
        params.put("limit", 1);
        params.put("sort", "id");
        params.put("order", "desc");
        params.put("ids", Collections.singletonList(id));
        params.put("zuoyeDeleteStart", 1);
        params.put("zuoyeDeleteEnd", 1);
        if(onlyPublished){
            params.put("publishStatus", "published");
        }
        CommonUtil.checkMap(params);
        PageUtils page = zuoyeService.queryPage(params);
        List<ZuoyeView> list = (List<ZuoyeView>) page.getList();
        if(list == null || list.isEmpty()){
            return null;
        }
        ZuoyeView view = list.get(0);
        dictionaryService.dictionaryConvert(view, request);
        return view;
    }

    /**
    * 后端列表
    */
    @RequestMapping("/page")
    public R page(@RequestParam Map<String, Object> params, HttpServletRequest request){
        logger.debug("page方法:,,Controller:{},,params:{}",this.getClass().getName(),JSONObject.toJSONString(params));
        String role = String.valueOf(request.getSession().getAttribute("role"));
        if(false) {
            return R.error(511,"永远不会进入");
        } else if("学生".equals(role)) {
            params.put("yonghuId",request.getSession().getAttribute("userId"));
        } else if("教师".equals(role)) {
            params.put("jiaoshiId",request.getSession().getAttribute("userId"));
        }
        params.put("zuoyeDeleteStart",1);
        params.put("zuoyeDeleteEnd",1);
        CommonUtil.checkMap(params);
        PageUtils page = zuoyeService.queryPage(params);

        List<ZuoyeView> list =(List<ZuoyeView>)page.getList();
        for(ZuoyeView c:list){
            dictionaryService.dictionaryConvert(c, request);
        }
        return R.ok().put("data", page);
    }

    /**
    * 后端详情
    */
    @RequestMapping("/info/{id}")
    public R info(@PathVariable("id") Long id, HttpServletRequest request){
        logger.debug("info方法:,,Controller:{},,id:{}",this.getClass().getName(),id);
        ZuoyeView view = loadZuoyeViewById(id, request, false);
        if(view != null){
            return R.ok().put("data", view);
        }
        return R.error(511,"查不到数据");
    }

    /**
    * 后端保存
    */
    @RequestMapping("/save")
    public R save(@RequestBody ZuoyeEntity zuoye, HttpServletRequest request){
        logger.debug("save方法:,,Controller:{},,zuoye:{}",this.getClass().getName(),zuoye.toString());

        String role = String.valueOf(request.getSession().getAttribute("role"));
        if(false) {
            return R.error(511,"永远不会进入");
        } else if("教师".equals(role)) {
            zuoye.setJiaoshiId(Integer.valueOf(String.valueOf(request.getSession().getAttribute("userId"))));
        }

        Wrapper<ZuoyeEntity> queryWrapper = new EntityWrapper<ZuoyeEntity>()
            .eq("zuoye_name", zuoye.getZuoyeName())
            .eq("zuoye_types", zuoye.getZuoyeTypes())
            .eq("jiaoshi_id", zuoye.getJiaoshiId())
            .eq("zuoye_delete", zuoye.getZuoyeDelete());

        logger.info("sql语句:"+queryWrapper.getSqlSegment());
        ZuoyeEntity zuoyeEntity = zuoyeService.selectOne(queryWrapper);
        if(zuoyeEntity==null){
            if(zuoye.getPublishStatus() == null){
                zuoye.setPublishStatus("published");
            }
            if(zuoye.getScoreTotal() == null){
                zuoye.setScoreTotal(100);
            }
            zuoye.setZuoyeDelete(1);
            zuoye.setInsertTime(new Date());
            zuoye.setCreateTime(new Date());
            zuoyeService.insert(zuoye);
            return R.ok();
        }else {
            return R.error(511,"表中有相同数据");
        }
    }

    /**
    * 后端修改
    */
    @RequestMapping("/update")
    public R update(@RequestBody ZuoyeEntity zuoye, HttpServletRequest request) throws NoSuchFieldException, ClassNotFoundException, IllegalAccessException, InstantiationException {
        logger.debug("update方法:,,Controller:{},,zuoye:{}",this.getClass().getName(),zuoye.toString());
        ZuoyeEntity oldZuoyeEntity = zuoyeService.selectById(zuoye.getId());

        String role = String.valueOf(request.getSession().getAttribute("role"));
        Wrapper<ZuoyeEntity> queryWrapper = new EntityWrapper<ZuoyeEntity>()
            .notIn("id",zuoye.getId())
            .andNew()
            .eq("zuoye_name", zuoye.getZuoyeName())
            .eq("zuoye_types", zuoye.getZuoyeTypes())
            .eq("jiaoshi_id", zuoye.getJiaoshiId())
            .eq("zuoye_delete", zuoye.getZuoyeDelete());

        logger.info("sql语句:"+queryWrapper.getSqlSegment());
        ZuoyeEntity zuoyeEntity = zuoyeService.selectOne(queryWrapper);
        if("".equals(zuoye.getZuoyePhoto()) || "null".equals(zuoye.getZuoyePhoto())){
            zuoye.setZuoyePhoto(null);
        }
        if("".equals(zuoye.getZuoyeFile()) || "null".equals(zuoye.getZuoyeFile())){
            zuoye.setZuoyeFile(null);
        }
        if(zuoyeEntity==null){
            zuoyeService.updateById(zuoye);
            return R.ok();
        }else {
            return R.error(511,"表中有相同数据");
        }
    }

    /**
    * 删除
    */
    @RequestMapping("/delete")
    public R delete(@RequestBody Integer[] ids, HttpServletRequest request){
        logger.debug("delete:,,Controller:{},,ids:{}",this.getClass().getName(), Arrays.toString(ids));
        List<ZuoyeEntity> oldZuoyeList =zuoyeService.selectBatchIds(Arrays.asList(ids));
        ArrayList<ZuoyeEntity> list = new ArrayList<>();
        for(Integer id:ids){
            ZuoyeEntity zuoyeEntity = new ZuoyeEntity();
            zuoyeEntity.setId(id);
            zuoyeEntity.setZuoyeDelete(2);
            list.add(zuoyeEntity);
        }
        if(list.size() > 0){
            zuoyeService.updateBatchById(list);
        }

        return R.ok();
    }

    /**
     * 批量上传
     */
    @RequestMapping("/batchInsert")
    public R batchInsert(String fileName, HttpServletRequest request){
        logger.debug("batchInsert方法:,,Controller:{},,fileName:{}",this.getClass().getName(),fileName);
        Integer yonghuId = Integer.valueOf(String.valueOf(request.getSession().getAttribute("userId")));
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        try {
            List<ZuoyeEntity> zuoyeList = new ArrayList<>();
            Map<String, List<String>> seachFields= new HashMap<>();
            Date date = new Date();
            int lastIndexOf = fileName.lastIndexOf(".");
            if(lastIndexOf == -1){
                return R.error(511,"该文件没有后缀");
            }else{
                String suffix = fileName.substring(lastIndexOf);
                if(!".xls".equals(suffix)){
                    return R.error(511,"只支持后缀为xls的excel文件");
                }else{
                    URL resource = this.getClass().getClassLoader().getResource("static/upload/" + fileName);
                    File file = new File(resource.getFile());
                    if(!file.exists()){
                        return R.error(511,"找不到上传文件，请联系管理员");
                    }else{
                        List<List<String>> dataList = PoiUtil.poiImport(file.getPath());
                        dataList.remove(0);
                        for(List<String> data:dataList){
                            ZuoyeEntity zuoyeEntity = new ZuoyeEntity();
                            zuoyeList.add(zuoyeEntity);
                        }
                        zuoyeService.insertBatch(zuoyeList);
                        return R.ok();
                    }
                }
            }
        }catch (Exception e){
            e.printStackTrace();
            return R.error(511,"批量插入数据异常，请联系管理员");
        }
    }

    /**
    * 前端列表
    */
    @IgnoreAuth
    @RequestMapping("/list")
    public R list(@RequestParam Map<String, Object> params, HttpServletRequest request){
        logger.debug("list方法:,,Controller:{},,params:{}",this.getClass().getName(),JSONObject.toJSONString(params));

        CommonUtil.checkMap(params);
        params.put("publishStatus","published");
        params.put("zuoyeDeleteStart",1);
        params.put("zuoyeDeleteEnd",1);
        PageUtils page = zuoyeService.queryPage(params);

        List<ZuoyeView> list =(List<ZuoyeView>)page.getList();
        for(ZuoyeView c:list) {
            dictionaryService.dictionaryConvert(c, request);
        }

        return R.ok().put("data", page);
    }

    /**
    * 前端详情
    */
    @RequestMapping("/detail/{id}")
    public R detail(@PathVariable("id") Long id, HttpServletRequest request){
        logger.debug("detail方法:,,Controller:{},,id:{}",this.getClass().getName(),id);
        ZuoyeView view = loadZuoyeViewById(id, request, true);
        if(view != null){
            return R.ok().put("data", view);
        }
        return R.error(511,"查不到数据");
    }

    /**
    * 前端保存
    */
    @RequestMapping("/add")
    public R add(@RequestBody ZuoyeEntity zuoye, HttpServletRequest request){
        logger.debug("add方法:,,Controller:{},,zuoye:{}",this.getClass().getName(),zuoye.toString());
        Wrapper<ZuoyeEntity> queryWrapper = new EntityWrapper<ZuoyeEntity>()
            .eq("zuoye_name", zuoye.getZuoyeName())
            .eq("zuoye_types", zuoye.getZuoyeTypes())
            .eq("jiaoshi_id", zuoye.getJiaoshiId())
            .eq("zuoye_delete", zuoye.getZuoyeDelete());
        logger.info("sql语句:"+queryWrapper.getSqlSegment());
        ZuoyeEntity zuoyeEntity = zuoyeService.selectOne(queryWrapper);
        if(zuoyeEntity==null){
            if(zuoye.getPublishStatus() == null){
                zuoye.setPublishStatus("published");
            }
            if(zuoye.getScoreTotal() == null){
                zuoye.setScoreTotal(100);
            }
            zuoye.setZuoyeDelete(1);
            zuoye.setInsertTime(new Date());
            zuoye.setCreateTime(new Date());
            zuoyeService.insert(zuoye);

            return R.ok();
        }else {
            return R.error(511,"表中有相同数据");
        }
    }

}
