
package com.controller;

import java.io.File;
import java.math.BigDecimal;
import java.net.URL;
import java.text.SimpleDateFormat;
import com.alibaba.fastjson.JSONObject;
import java.util.*;
import org.springframework.beans.BeanUtils;
import javax.servlet.http.HttpServletRequest;
import org.springframework.web.context.ContextLoader;
import javax.servlet.ServletContext;
import com.service.TokenService;
import com.utils.*;
import java.lang.reflect.InvocationTargetException;

import com.service.DictionaryService;
import org.apache.commons.lang3.StringUtils;
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
 * 会议
 * 后端接口
 * @author
 * @email
*/
@RestController
@Controller
@RequestMapping("/kaihuitongzhi")
public class KaihuitongzhiController {
    private static final Logger logger = LoggerFactory.getLogger(KaihuitongzhiController.class);

    private static final String TABLE_NAME = "kaihuitongzhi";

    @Autowired
    private KaihuitongzhiService kaihuitongzhiService;


    @Autowired
    private TokenService tokenService;
    @Autowired
    private DictionaryService dictionaryService;

    /**
     * 批量刷新旧会议发布时间
     */
    @RequestMapping("/refreshPublishTime")
    public R refreshPublishTime(HttpServletRequest request){
        String role = String.valueOf(request.getSession().getAttribute("role"));
        if(!"管理员".equals(role)){
            return R.error(401, "无权限执行该操作");
        }

        List<KaihuitongzhiEntity> allMeetings = kaihuitongzhiService.selectList(new EntityWrapper<KaihuitongzhiEntity>());
        if(allMeetings == null || allMeetings.isEmpty()){
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
}
